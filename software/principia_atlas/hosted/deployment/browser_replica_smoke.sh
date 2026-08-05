#!/usr/bin/env bash
set -euo pipefail

: "${RUNNER_TEMP:?RUNNER_TEMP is required}"
: "${RELEASE_VERSION:?RELEASE_VERSION is required}"

root="$RUNNER_TEMP/hosted-browser-smoke"
image="principia-atlas-hosted:first"
network="principia-atlas-browser-replica-net"
pod="principia-atlas-replica-pod"
idp="principia-atlas-replica-idp"
hosted_a="principia-atlas-replica-hosted-a"
hosted_b="principia-atlas-replica-hosted-b"
edge_a="principia-atlas-replica-edge-a"
edge_b="principia-atlas-replica-edge-b"
gateway="principia-atlas-replica-gateway"
issuer_host="identity.example.test"
external_host="learn.example.test"
containers=("$gateway" "$edge_b" "$edge_a" "$hosted_b" "$hosted_a" "$idp" "$pod")

show_diagnostics() {
  echo '--- cross-replica browser smoke diagnostics ---' >&2
  docker ps -a --filter 'name=principia-atlas-replica-' >&2 || true
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
  local host=$1
  local port=$2
  local url=$3
  for attempt in $(seq 1 40); do
    if curl --fail --silent --noproxy '*' \
      --resolve "$host:$port:127.0.0.1" \
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
  -p 18443:18443 \
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
  --redirect-uri "https://$external_host:18443/auth/callback" \
  --tls-key /run/idp/tls.key \
  --tls-cert /mock/idp.crt \
  --signing-key /run/idp/signing.key \
  --jwks /mock/jwks.json
wait_https "$issuer_host" 19443 "https://$issuer_host:19443/healthz"

run_hosted() {
  local name=$1
  local port=$2
  local instance=$3
  docker run -d --name "$name" \
    --network "container:$pod" \
    "${common_security[@]}" \
    --env NODE_EXTRA_CA_CERTS=/mock/ca.crt \
    --mount type=bind,src="$root/config",dst=/config,readonly \
    --mount type=bind,src="$RUNNER_TEMP/hosted/store",dst=/store,readonly \
    --mount type=bind,src="$root/replica-state",dst=/state \
    --mount type=bind,src="$root/replica-audit",dst=/audit \
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
    --audit-log "/audit/$instance.ndjson" \
    --instance-id "$instance" \
    --host 127.0.0.1 \
    --port "$port" \
    --shutdown-timeout-ms 20000
}

run_hosted "$hosted_a" 8080 replica-a
run_hosted "$hosted_b" 8090 replica-b
wait_loopback "$hosted_a" http://127.0.0.1:8080/readyz
wait_loopback "$hosted_b" http://127.0.0.1:8090/readyz

run_edge() {
  local name=$1
  local port=$2
  local upstream=$3
  docker run -d --name "$name" \
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
    --upstream-origin "$upstream" \
    --host 0.0.0.0 \
    --port "$port" \
    --allow-network \
    --shutdown-timeout-ms 20000
}

run_edge "$edge_a" 8081 http://127.0.0.1:8080
run_edge "$edge_b" 8082 http://127.0.0.1:8090
wait_loopback "$edge_a" http://127.0.0.1:8081/edge/healthz
wait_loopback "$edge_b" http://127.0.0.1:8082/edge/healthz

docker run -d --name "$gateway" \
  --network "container:$pod" \
  "${common_security[@]}" \
  --mount type=bind,src="$root/public",dst=/mock,readonly \
  --mount type=bind,src="$root/gateway-secrets",dst=/run/gateway,readonly \
  --entrypoint node \
  "$image" \
  /opt/principia-atlas/hosted/deployment/mock_tls_gateway.mjs \
  --host 0.0.0.0 \
  --port 18443 \
  --upstream-origin http://127.0.0.1:8081 \
  --callback-upstream-origin http://127.0.0.1:8082 \
  --callback-path /auth/callback \
  --session-upstream-origin http://127.0.0.1:8082 \
  --session-path /api/session \
  --tls-key /run/gateway/tls.key \
  --tls-cert /mock/gateway.crt
wait_https "$external_host" 18443 "https://$external_host:18443/edge/healthz"

node software/principia_atlas/hosted/deployment/browser_smoke_client.mjs \
  --origin "https://$external_host:18443" \
  --origin-address 127.0.0.1 \
  --issuer "https://$issuer_host:19443" \
  --issuer-address 127.0.0.1 \
  --ca "$root/public/ca.crt" \
  --version "$RELEASE_VERSION" \
  > "$root/replica-result.json"

python3 -m json.tool "$root/replica-result.json" >/dev/null
sudo test -s "$root/replica-audit/replica-a.ndjson"
sudo test -s "$root/replica-audit/replica-b.ndjson"
sudo grep -F '"event":"auth.oidc"' "$root/replica-audit/replica-b.ndjson" | grep -Fq '"outcome":"success"'
! sudo grep -Fq '"event":"auth.oidc"' "$root/replica-audit/replica-a.ndjson"
sudo grep -F '"event":"auth.logout"' "$root/replica-audit/replica-a.ndjson" | grep -Fq '"outcome":"revoked"'
! sudo grep -Fq '"event":"auth.logout"' "$root/replica-audit/replica-b.ndjson"
sudo grep -F '"event":"session.reject"' "$root/replica-audit/replica-b.ndjson" | grep -Fq '"reason":"unregistered_or_revoked"'
! sudo grep -Fq 'browser-client-secret' "$root/replica-audit/"*.ndjson
! sudo grep -Fq 'browser-flow-secret' "$root/replica-audit/"*.ndjson
