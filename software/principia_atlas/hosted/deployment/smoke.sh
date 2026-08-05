#!/usr/bin/env bash
set -euo pipefail

: "${RUNNER_TEMP:?RUNNER_TEMP is required}"
: "${RELEASE_VERSION:?RELEASE_VERSION is required}"

containers=(principia-atlas-a principia-atlas-b)

show_diagnostics() {
  echo '--- hosted container diagnostics ---' >&2
  docker ps -a --filter 'name=principia-atlas-' >&2 || true
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
  if [[ $status -ne 0 ]]; then
    show_diagnostics
  fi
  docker rm -f "${containers[@]}" >/dev/null 2>&1 || true
  exit "$status"
}
trap cleanup EXIT

wait_ready() {
  local name=$1
  local port=$2
  for attempt in $(seq 1 30); do
    if curl --fail --silent "http://127.0.0.1:$port/readyz" >/dev/null; then
      return 0
    fi
    if [[ "$(docker inspect "$name" --format '{{.State.Running}}' 2>/dev/null || echo false)" != true ]]; then
      echo "$name exited before readiness" >&2
      return 1
    fi
    sleep 1
  done
  echo "$name did not become ready" >&2
  return 1
}

# Immutable deployment inputs are root-owned and readable but never writable by
# the numeric runtime user. Docker bind mounts them read-only as a second layer
# of protection. Writable state, audit, and backup paths remain UID 10001-owned.
sudo chown root:root "$RUNNER_TEMP/hosted/catalog.json" "$RUNNER_TEMP/hosted/tenants.json"
sudo chmod 0444 "$RUNNER_TEMP/hosted/catalog.json" "$RUNNER_TEMP/hosted/tenants.json"
sudo chown -R root:root "$RUNNER_TEMP/hosted/store"
sudo find "$RUNNER_TEMP/hosted/store" -type d -exec chmod 0555 {} +
sudo find "$RUNNER_TEMP/hosted/store" -type f -exec chmod 0444 {} +

common=(
  --read-only
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=32m
  --cap-drop ALL
  --security-opt no-new-privileges:true
  --mount type=bind,src="$RUNNER_TEMP/hosted/catalog.json",dst=/config/catalog.json,readonly
  --mount type=bind,src="$RUNNER_TEMP/hosted/tenants.json",dst=/config/tenants.json,readonly
  --mount type=bind,src="$RUNNER_TEMP/hosted/store",dst=/store,readonly
  --mount type=bind,src="$RUNNER_TEMP/hosted/state",dst=/var/lib/principia-atlas
  --mount type=bind,src="$RUNNER_TEMP/hosted/audit",dst=/var/log/principia-atlas
  --mount type=bind,src="$RUNNER_TEMP/hosted/secrets",dst=/run/secrets,readonly
)
server_args=(
  --catalog /config/catalog.json
  --tenants /config/tenants.json
  --store /store
  --state /var/lib/principia-atlas/auth-state.sqlite
  --identity-secret-file /run/secrets/identity
  --session-secret-file /run/secrets/session
  --metrics-token-file /run/secrets/metrics
  --audit-log /var/log/principia-atlas/audit.ndjson
  --host 0.0.0.0
  --port 8080
  --allow-network
  --shutdown-timeout-ms 20000
)

docker run -d --name principia-atlas-a -p 18081:8080 "${common[@]}" \
  principia-atlas-hosted:first "${server_args[@]}" --instance-id instance-a
docker run -d --name principia-atlas-b -p 18082:8080 "${common[@]}" \
  principia-atlas-hosted:first "${server_args[@]}" --instance-id instance-b

wait_ready principia-atlas-a 18081
wait_ready principia-atlas-b 18082

export PRINCIPIA_ATLAS_DEV_AUTH=1
export PRINCIPIA_ATLAS_IDENTITY_SECRET='ci-identity-secret-0123456789-abcdefghijklmnopqrstuvwxyz'
assertion="$(node software/principia_atlas/hosted/dev_identity.mjs \
  --tenants "$RUNNER_TEMP/hosted/tenants.json" \
  --subject ci-learner \
  --tenant local-preview \
  --roles learner)"

curl --fail --silent --dump-header "$RUNNER_TEMP/hosted/exchange.headers" \
  --request POST \
  --header "Authorization: Bearer $assertion" \
  --header "Origin: http://127.0.0.1:18081" \
  http://127.0.0.1:18081/api/auth/exchange \
  > "$RUNNER_TEMP/hosted/exchange.json"
cookie="$(awk 'BEGIN{IGNORECASE=1} /^set-cookie:/{print $2}' "$RUNNER_TEMP/hosted/exchange.headers" | tr -d '\r' | cut -d';' -f1)"
test -n "$cookie"

curl --fail --silent \
  --header "Cookie: $cookie" \
  "http://127.0.0.1:18082/app/$RELEASE_VERSION/" \
  > "$RUNNER_TEMP/hosted/release.html"
curl --fail --silent \
  --header 'Authorization: Bearer ci-metrics-token-0123456789-abcdefghijklmnopqrstuvwxyz' \
  http://127.0.0.1:18082/metrics \
  > "$RUNNER_TEMP/hosted/metrics.txt"
grep -q '^principia_atlas_up 1$' "$RUNNER_TEMP/hosted/metrics.txt"
! grep -Eiq 'tenant|subject|session|assertion' "$RUNNER_TEMP/hosted/metrics.txt"

docker stop --time 25 principia-atlas-a >/dev/null
curl --fail --silent \
  --header "Cookie: $cookie" \
  http://127.0.0.1:18082/api/session >/dev/null

sudo -u '#10001' node software/principia_atlas/hosted/auth_state_recovery.mjs backup \
  --state "$RUNNER_TEMP/hosted/state/auth-state.sqlite" \
  --output "$RUNNER_TEMP/hosted/backups/auth-state.sqlite" \
  > "$RUNNER_TEMP/hosted/backup-result.json"
sudo -u '#10001' node software/principia_atlas/hosted/auth_state_recovery.mjs verify \
  --backup "$RUNNER_TEMP/hosted/backups/auth-state.sqlite" \
  > "$RUNNER_TEMP/hosted/backup-verify.json"

docker stop --time 25 principia-atlas-b >/dev/null
sudo -u '#10001' node software/principia_atlas/hosted/auth_state_recovery.mjs restore \
  --backup "$RUNNER_TEMP/hosted/backups/auth-state.sqlite" \
  --state "$RUNNER_TEMP/hosted/state/restored.sqlite" \
  --confirm-offline ALL_INSTANCES_STOPPED \
  > "$RUNNER_TEMP/hosted/restore-result.json"
sudo -u '#10001' node software/principia_atlas/hosted/auth_state_recovery.mjs integrity \
  --state "$RUNNER_TEMP/hosted/state/restored.sqlite" \
  > "$RUNNER_TEMP/hosted/restored-integrity.json"

sudo -u '#10001' test -s "$RUNNER_TEMP/hosted/audit/audit.ndjson"
! sudo -u '#10001' grep -Fq 'ci-identity-secret' "$RUNNER_TEMP/hosted/audit/audit.ndjson"
! sudo -u '#10001' grep -Fq 'ci-session-secret' "$RUNNER_TEMP/hosted/audit/audit.ndjson"
! sudo -u '#10001' grep -Fq 'ci-metrics-token' "$RUNNER_TEMP/hosted/audit/audit.ndjson"
