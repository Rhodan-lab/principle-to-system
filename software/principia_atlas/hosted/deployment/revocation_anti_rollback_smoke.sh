#!/usr/bin/env bash
set -euo pipefail

: "${RUNNER_TEMP:?RUNNER_TEMP is required}"

root="$RUNNER_TEMP/hosted-browser-smoke"
image="principia-atlas-hosted:first"
work="$root/revocation-anti-rollback"
state_dir="$work/state"
operator_container="principia-atlas-revocation-anti-rollback"
issuer="https://identity.example.test:19443"
external_subject="anti-rollback-smoke-learner"
event_id="anti-rollback-smoke-event-0001"

cleanup() {
  local status=$?
  docker rm -f "$operator_container" >/dev/null 2>&1 || true
  sudo rm -rf "$work"
  exit "$status"
}
trap cleanup EXIT

mkdir -p "$state_dir"
root_private="$work/root-private.der"
root_public="$work/root-public.der"
request_private="$work/request-private.der"
request_public="$work/request-public.der"
request_draft="$work/request-draft.json"
request_file="$work/request.json"
keyring_1_draft="$work/keyring-1-draft.json"
keyring_1="$work/keyring-1.json"
keyring_2_draft="$work/keyring-2-draft.json"
keyring_2="$work/keyring-2.json"
state_file="$state_dir/auth-state.sqlite"

openssl genpkey -algorithm ED25519 -outform DER -out "$root_private"
openssl pkey -inform DER -in "$root_private" -pubout -outform DER -out "$root_public"
openssl genpkey -algorithm ED25519 -outform DER -out "$request_private"
openssl pkey -inform DER -in "$request_private" -pubout -outform DER -out "$request_public"
chmod 0400 "$root_private" "$request_private"
chmod 0444 "$root_public" "$request_public"

python3 - <<'PYJSON'
import json
import os
import time
from pathlib import Path
work = Path(os.environ['RUNNER_TEMP']) / 'hosted-browser-smoke' / 'revocation-anti-rollback'
now = int(time.time())
request = {
    'contract': 'principia-atlas-hosted-oidc-revocation-request-draft/0.1',
    'tenant_id': 'local-preview',
    'issuer': 'https://identity.example.test:19443',
    'external_subject': 'anti-rollback-smoke-learner',
    'event_id': 'anti-rollback-smoke-event-0001',
    'issued_at': now - 5,
    'expires_at': now + 295,
    'receipt_ttl_seconds': 3600,
}
for name, generation in [('keyring-1-draft.json', 1), ('keyring-2-draft.json', 2)]:
    keyring = {
        'contract': 'principia-atlas-hosted-oidc-revocation-keyring-draft/0.2',
        'generation': generation,
        'keys': [{
            'public_key_file': str(work / 'request-public.der'),
            'not_before': now - 300,
            'not_after': now + 7200,
        }],
        'revoked_key_ids': [],
    }
    path = work / name
    path.write_text(json.dumps(keyring, sort_keys=True, separators=(',', ':')) + '\n')
    path.chmod(0o600)
path = work / 'request-draft.json'
path.write_text(json.dumps(request, sort_keys=True, separators=(',', ':')) + '\n')
path.chmod(0o600)
PYJSON

node software/principia_atlas/hosted/revocation_request_cli.mjs sign \
  --input "$request_draft" \
  --private-key-file "$request_private" \
  --output "$request_file" > "$work/request-sign-result.json"
node software/principia_atlas/hosted/revocation_request_cli.mjs keyring \
  --input "$keyring_1_draft" \
  --root-private-key-file "$root_private" \
  --output "$keyring_1" > "$work/keyring-1-result.json"
node software/principia_atlas/hosted/revocation_request_cli.mjs keyring \
  --input "$keyring_2_draft" \
  --root-private-key-file "$root_private" \
  --output "$keyring_2" > "$work/keyring-2-result.json"

STATE_FILE="$state_file" ISSUER="$issuer" EXTERNAL_SUBJECT="$external_subject" node --input-type=module <<'JS'
import { canonicalOidcSubject, openSqliteAuthState } from './software/principia_atlas/hosted/index.mjs';
const now = Math.floor(Date.now() / 1000);
const state = openSqliteAuthState(process.env.STATE_FILE);
const session = {
  sid: 'anti_rollback_smoke_session_0001',
  jti: 'anti_rollback_smoke_assertion_0001',
  sub: canonicalOidcSubject(process.env.ISSUER, process.env.EXTERNAL_SUBJECT),
  tenant_id: 'local-preview',
  roles: ['learner'],
  iat: now - 20,
  exp: now + 7200,
};
if (!state.commitExchange({ assertionId: session.jti, assertionExpiresAt: now + 300, session }, now)) {
  throw new Error('failed to seed anti-rollback smoke session');
}
state.close();
JS

rm -f "$root_private" "$request_private" "$request_draft" "$keyring_1_draft" "$keyring_2_draft"
test ! -e "$root_private"
test ! -e "$request_private"
chmod 0400 "$request_file"
chmod 0444 "$root_public" "$request_public" "$keyring_1" "$keyring_2"
sudo chown -R 10001:10001 "$work"

common_security=(
  --read-only
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=16m
  --cap-drop ALL
  --security-opt no-new-privileges:true
)

run_signed() {
  local keyring=$1
  local output=$2
  docker run --rm --name "$operator_container" \
    --network none \
    "${common_security[@]}" \
    --mount type=bind,src="$state_dir",dst=/state \
    --mount type=bind,src="$request_file",dst=/run/revocation-request.json,readonly \
    --mount type=bind,src="$keyring",dst=/run/revocation-keyring.json,readonly \
    --mount type=bind,src="$root_public",dst=/run/revocation-keyring-root.der,readonly \
    --entrypoint node \
    "$image" \
    /opt/principia-atlas/hosted/auth_state_cli.mjs revoke-oidc-request \
    --state /state/auth-state.sqlite \
    --request-file /run/revocation-request.json \
    --request-keyring-file /run/revocation-keyring.json \
    --keyring-root-key-file /run/revocation-keyring-root.der \
    > "$output"
}

run_signed "$keyring_1" "$work/first.json"
run_signed "$keyring_2" "$work/retry.json"

set +e
run_signed "$keyring_1" "$work/rollback.json" 2> "$work/rollback.err"
rollback_status=$?
set -e
test "$rollback_status" -ne 0
grep -Fq 'keyring rollback detected' "$work/rollback.err"

set +e
docker run --rm --name "$operator_container" \
  --network none \
  "${common_security[@]}" \
  --mount type=bind,src="$state_dir",dst=/state \
  --mount type=bind,src="$request_file",dst=/run/revocation-request.json,readonly \
  --mount type=bind,src="$request_public",dst=/run/revocation-public.der,readonly \
  --entrypoint node \
  "$image" \
  /opt/principia-atlas/hosted/auth_state_cli.mjs revoke-oidc-request \
  --state /state/auth-state.sqlite \
  --request-file /run/revocation-request.json \
  --request-key-file /run/revocation-public.der \
  > "$work/single-key.json" 2> "$work/single-key.err"
single_key_status=$?
set -e
test "$single_key_status" -ne 0
grep -Fq 'single-key trust source is disabled' "$work/single-key.err"

! grep -R -Fq "$external_subject" "$work/first.json" "$work/retry.json" "$work/rollback.err" "$work/single-key.err"
! grep -R -Fq "$issuer" "$work/first.json" "$work/retry.json" "$work/rollback.err" "$work/single-key.err"

ROLLBACK_STATUS="$rollback_status" SINGLE_KEY_STATUS="$single_key_status" python3 - <<'PYJSON'
import json
import os
from pathlib import Path
root = Path(os.environ['RUNNER_TEMP']) / 'hosted-browser-smoke'
work = root / 'revocation-anti-rollback'
first = json.loads((work / 'first.json').read_text())
retry = json.loads((work / 'retry.json').read_text())
assert first['verified_keyring_generation'] == 1
assert first['authorization_keyring_generation'] == 1
assert first['replayed'] is False
assert first['revoked_sessions'] == 1
assert retry['verified_keyring_generation'] == 2
assert retry['authorization_keyring_generation'] == 1
assert retry['replayed'] is True
assert retry['created_at'] == first['created_at']
assert retry['expires_at'] == first['expires_at']
result_path = root / 'replica-result.json'
result = json.loads(result_path.read_text())
result['revocation_keyring_anti_rollback'] = {
    'authorization_generation': first['authorization_keyring_generation'],
    'verified_generation': retry['verified_keyring_generation'],
    'root_key_id': retry['verified_keyring_root_id'],
    'rollback_rejected': int(os.environ['ROLLBACK_STATUS']) != 0,
    'single_key_downgrade_rejected': int(os.environ['SINGLE_KEY_STATUS']) != 0,
    'network': 'none',
    'operator_uid': '10001:10001',
}
result_path.write_text(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
PYJSON
