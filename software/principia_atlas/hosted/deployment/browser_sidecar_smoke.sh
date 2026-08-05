#!/usr/bin/env bash
set -euo pipefail

: "${RUNNER_TEMP:?RUNNER_TEMP is required}"
: "${RELEASE_VERSION:?RELEASE_VERSION is required}"

root="$RUNNER_TEMP/hosted-browser-smoke"
image="principia-atlas-hosted:first"
network="principia-atlas-browser-smoke-net"
pod="principia-atlas-browser-pod"
idp="principia-atlas-browser-idp"
hosted="principia-atlas-browser-hosted"
edge="principia-atlas-browser-edge"
issuer_host="identity.example.test"
containers=("$edge" "$hosted" "$idp" "$pod")

show_diagnostics() {
  echo '--- browser sidecar smoke diagnostics ---' >&2
  docker ps -a --filter 'name=principia-atlas-browser-' >&2 || true
  for name in "${containers[@]}"; do
    if docker inspect "$name" >/dev/null 2>&1; then
      echo "--- $name inspect ---" >&2
      docker inspect "$name" --format 'status={{.State.Status}} running={{.State.Running}} exit={{.State.ExitCode}} error={{.State.Error}} oom={{.State.OOMKilled}}' >&2 || true
      echo "--- $name logs ---" >&2
      docker logs "$name" >&2 || true
    fi
  done
}

cleanup() {
  local status=$?
  if [[ $status -ne 0 ]]; then show_diagnostics; fi
  docker rm -f "${containers[@]}" >/dev/null 2>&1 || true
  docker network rm "$network" >/dev/null 2>&1 || true
  exit "$status"
}
trap cleanup EXIT

wait_https() {
  local url=$1
  for attempt in $(seq 1 40); do
    if curl --fail --silent \
      --resolve "$issuer_host:19443:127.0.0.1" \
      --cacert "$root/public/ca.crt" \
      "$url" >/dev/null; then
      return 0
    fi
    sleep 1
  done
  echo "HTTPS dependency did not become ready: $url" >&2
  return 1
}

wait_loopback() {
  local container=$1
  local url=$2
  for attempt in $(seq 1 40); do
    if docker exec "$pod" node -e "fetch('$url').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"; then return 0; fi
    if [[ "$(docker inspect "$container" --format '{{.State.Running}}' 2>/dev/null || echo false)" != true ]]; then
      echo "$container exited before readiness" >&2
      return 1
    fi
    sleep 1
  done
  echo "$container did not become ready: $url" >&2
  return 1
}

common_security=(
  --read-only
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=32m
  --cap-drop ALL
  --security-opt no-new-privileges:true
)

docker network create "$network" >/dev/null

docker run -d --name "$pod" \
  --network "$network" \
  --network-alias "$issuer_host" \
  -p 18083:8081 \
  -p 19443:19443 \
  --entrypoint sleep \
  "$image" infinity

docker run -d --name "$idp" \
  --network "container:$pod" \
  "${common_security[@]}" \
  --mount type=bind,src="$root/public",dst=/mock,readonly \
  --mount type=bind,src="$root/idp-secrets",dst=/run/idp,readonly \
  --mount type=bind,src="$root/secrets",dst=/run/secrets,readonly \
  --entrypoint node \
  "$image" \
  /opt/principia-atlas/hosted/deployment/mock_oidc_provider.mjs \
  --host 0.0.0.0 \
  --port 19443 \
  --issuer "https://$issuer_host:19443" \
  --client-id principia-atlas-browser \
  --client-secret-file /run/secrets/browser-client \
  --audience principia-atlas-external \
  --redirect-uri http://127.0.0.1:18083/auth/callback \
  --tls-key /run/idp/tls.key \
  --tls-cert /mock/tls.crt \
  --signing-key /run/idp/signing.key \
  --jwks /mock/jwks.json
wait_https "https://$issuer_host:19443/healthz"

docker run -d --name "$hosted" \
  --network "container:$pod" \
  "${common_security[@]}" \
  --env NODE_EXTRA_CA_CERTS=/mock/ca.crt \
  --mount type=bind,src="$root/config",dst=/config,readonly \
  --mount type=bind,src="$RUNNER_TEMP/hosted/store",dst=/store,readonly \
  --mount type=bind,src="$root/state",dst=/state \
  --mount type=bind,src="$root/audit",dst=/audit \
  --mount type=bind,src="$root/secrets",dst=/run/secrets,readonly \
  --mount type=bind,src="$root/public",dst=/mock,readonly \
  "$image" \
  --catalog /config/catalog.json \
  --tenants /config/tenants.json \
  --store /store \
  --state /state/auth-state.sqlite \
  --identity-secret-file /run/secrets/identity \
  --session-secret-file /run/secrets/session \
  --metrics-token-file /run/secrets/metrics \
  --oidc-policy /config/oidc-policy.json \
  --oidc-remote-jwks \
  --audit-log /audit/browser-smoke.ndjson \
  --instance-id browser-smoke \
  --host 127.0.0.1 \
  --port 8080 \
  --shutdown-timeout-ms 20000
wait_loopback "$hosted" http://127.0.0.1:8080/readyz

docker run -d --name "$edge" \
  --network "container:$pod" \
  "${common_security[@]}" \
  --env NODE_EXTRA_CA_CERTS=/mock/ca.crt \
  --mount type=bind,src="$root/config",dst=/config,readonly \
  --mount type=bind,src="$root/secrets",dst=/run/secrets,readonly \
  --mount type=bind,src="$root/public",dst=/mock,readonly \
  --entrypoint node \
  "$image" \
  /opt/principia-atlas/hosted/browser_edge_cli.mjs serve \
  --config /config/browser-oidc.json \
  --flow-secret-file /run/secrets/browser-flow \
  --client-secret-file /run/secrets/browser-client \
  --upstream-origin http://127.0.0.1:8080 \
  --host 0.0.0.0 \
  --port 8081 \
  --allow-network \
  --shutdown-timeout-ms 20000

for attempt in $(seq 1 40); do
  if curl --fail --silent http://127.0.0.1:18083/edge/healthz >/dev/null; then break; fi
  if [[ "$attempt" = 40 ]]; then
    echo 'browser edge did not become ready' >&2
    exit 1
  fi
  sleep 1
done

node software/principia_atlas/hosted/deployment/browser_smoke_client.mjs \
  --origin http://127.0.0.1:18083 \
  --issuer "https://$issuer_host:19443" \
  --issuer-address 127.0.0.1 \
  --ca "$root/public/ca.crt" \
  --version "$RELEASE_VERSION" \
  > "$root/result.json"

python3 -m json.tool "$root/result.json" >/dev/null
sudo test -s "$root/audit/browser-smoke.ndjson"
! sudo grep -Fq 'browser-client-secret' "$root/audit/browser-smoke.ndjson"
! sudo grep -Fq 'browser-flow-secret' "$root/audit/browser-smoke.ndjson"
