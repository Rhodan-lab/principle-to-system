# OIDC revocation signing-key rotation

This runbook rotates the Ed25519 keys used to authorize hosted OIDC subject-revocation requests. It preserves the separation between the controlled signer and the networkless state operator.

## Security invariants

- Private signing keys exist only on the controlled signer host.
- The state operator receives one immutable keyring and one private signed request, both through read-only mounts.
- Issuer and external subject remain inside request files and never appear in process arguments or command output.
- A keyring is a trust root. It must be distributed through the same reviewed, immutable configuration path as tenant and OIDC policy.
- Each key has an explicit `not_before` and exclusive `not_after` Unix timestamp.
- A request is accepted only when its signing key is present, not revoked, and valid at the request's `issued_at` timestamp.
- `revoked_key_ids` overrides presence and validity. A revoked key is rejected immediately.
- The first successful execution persists `authorization_key_id` in the durable receipt. A retry signed by another trusted key reports both the current `verified_key_id` and the original `authorization_key_id`.

## Create the replacement key

Generate the new private/public pair on the signer host:

```bash
openssl genpkey -algorithm ED25519 -outform DER \
  -out /secure/revocation-key-b-private.der
openssl pkey -inform DER \
  -in /secure/revocation-key-b-private.der \
  -pubout -outform DER \
  -out /secure/revocation-key-b-public.der
chmod 0400 /secure/revocation-key-b-private.der
chmod 0444 /secure/revocation-key-b-public.der
```

Record both key identifiers:

```bash
node software/principia_atlas/hosted/revocation_request_cli.mjs key-id \
  --public-key-file /secure/revocation-key-a-public.der
node software/principia_atlas/hosted/revocation_request_cli.mjs key-id \
  --public-key-file /secure/revocation-key-b-public.der
```

## Build an overlap keyring

Create a mode-`0600` draft. The overlap must cover configuration rollout plus the maximum five-minute request lifetime. The example timestamps are placeholders and must be replaced with reviewed Unix seconds.

```json
{
  "contract": "principia-atlas-hosted-oidc-revocation-keyring-draft/0.1",
  "keys": [
    {
      "public_key_file": "/secure/revocation-key-a-public.der",
      "not_before": 1800000000,
      "not_after": 1800600000
    },
    {
      "public_key_file": "/secure/revocation-key-b-public.der",
      "not_before": 1800300000,
      "not_after": 1800900000
    }
  ],
  "revoked_key_ids": []
}
```

Build the canonical immutable keyring:

```bash
node software/principia_atlas/hosted/revocation_request_cli.mjs keyring \
  --input /secure/revocation-keyring-draft.json \
  --output /secure/revocation-keyring.json
```

The builder derives each key identifier from its SPKI bytes, rejects duplicate keys and invalid windows, sorts the output deterministically, refuses an existing output path, and creates the keyring without write or execute permissions.

## Deploy the overlap

Distribute only `/secure/revocation-keyring.json` to the state operator. Mount it read-only and continue mounting each request privately:

```bash
node software/principia_atlas/hosted/auth_state_cli.mjs revoke-oidc-request \
  --state /state/auth-state.sqlite \
  --request-file /run/revocation-request.json \
  --request-keyring-file /run/revocation-keyring.json
```

During overlap, requests signed by key A or key B are accepted within their respective windows. Move every signer to key B, then wait at least the maximum request lifetime plus deployment propagation before retiring key A.

The older single-key `--request-key-file` interface remains available for compatibility. Production rotation should use exactly one `--request-keyring-file`; supplying both trust sources is rejected.

## Retire or revoke the old key

For planned retirement, publish a new keyring with key A's `not_after` in the past or remove key A after its window and all requests have expired.

For suspected compromise, keep key A's identifier in `revoked_key_ids` and publish the replacement keyring immediately. Revocation overrides the configured validity window:

```json
{
  "contract": "principia-atlas-hosted-oidc-revocation-keyring-draft/0.1",
  "keys": [
    {
      "public_key_file": "/secure/revocation-key-a-public.der",
      "not_before": 1800000000,
      "not_after": 1800600000
    },
    {
      "public_key_file": "/secure/revocation-key-b-public.der",
      "not_before": 1800300000,
      "not_after": 1800900000
    }
  ],
  "revoked_key_ids": [
    "ed25519:REPLACE_WITH_KEY_A_IDENTIFIER"
  ]
}
```

Do not delete the evidence identifying a compromised key. The durable receipt retains the key that first authorized each new signed revocation event, including through verified backup and offline restore.

## Verify rotation evidence

A first execution under key A returns evidence shaped like:

```json
{
  "authorization_key_id": "ed25519:KEY_A",
  "verified_key_id": "ed25519:KEY_A",
  "replayed": false
}
```

A retry of the same event and target under key B returns:

```json
{
  "authorization_key_id": "ed25519:KEY_A",
  "verified_key_id": "ed25519:KEY_B",
  "replayed": true
}
```

`authorization_key_id` is historical and immutable for that receipt. `verified_key_id` describes the request used for the current invocation.

## Rollback

If key B deployment is faulty but key A is not compromised and remains inside its validity window:

1. Stop issuing with key B.
2. Republish the last reviewed keyring that trusts key A.
3. Verify the mounted keyring is immutable and the operator remains networkless.
4. Issue a fresh short-lived request with key A.
5. Diagnose key B outside the operator boundary.

Never roll back to a key listed as compromised. Generate a third key and publish a new keyring instead.
