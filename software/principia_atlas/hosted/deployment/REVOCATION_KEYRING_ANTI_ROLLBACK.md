---
title: OIDC revocation keyring anti-rollback
slug: oidc-revocation-keyring-anti-rollback
module: Principia Atlas Hosted Operations
domain: technology
status: reviewed
prerequisites: []
connections: []
last_reviewed: 2026-08-05
content_license: CC-BY-4.0
---

# OIDC revocation keyring anti-rollback

This runbook upgrades OIDC revocation signing-key rotation from an unsigned compatibility keyring to a root-signed, monotonically versioned trust configuration. The upgrade is one-way for each durable authentication state.

## Security invariants

- The keyring root private key stays on the controlled configuration signer and never enters the hosted operator container.
- The operator receives only the immutable root public key, immutable signed keyring, private signed request, and durable authentication state.
- Every signed keyring contains a positive integer `generation`, a derived `root_key_id`, the request-signing keys, explicit validity windows, revoked key identifiers, and an Ed25519 signature over canonical domain-separated JSON.
- The pinned root public key must match `root_key_id`, and the keyring signature is verified before request authorization or state access.
- The state transaction stores the greatest accepted generation in `state_metadata` under `oidc_revocation_keyring_generation`.
- A generation lower than the stored value is rejected as rollback.
- A generation higher than the stored value advances the floor atomically with receipt replay or subject revocation.
- Event target mismatch is checked before generation advancement, so a mismatched request cannot raise the floor.
- Once a signed generation has been accepted, requests using a single public key or an unsigned compatibility keyring are rejected permanently for that state.
- The first receipt preserves `authorization_keyring_generation`; retries report the current `verified_keyring_generation` without rewriting historical authorization evidence.
- Verified backup and offline restore preserve the generation floor and receipt evidence.

## Generate the offline root

Generate one Ed25519 root on the controlled configuration signer:

```bash
openssl genpkey -algorithm ED25519 -outform DER \
  -out /secure/revocation-keyring-root-private.der
openssl pkey -inform DER \
  -in /secure/revocation-keyring-root-private.der \
  -pubout -outform DER \
  -out /secure/revocation-keyring-root-public.der
chmod 0400 /secure/revocation-keyring-root-private.der
chmod 0444 /secure/revocation-keyring-root-public.der
```

Distribute only the public file to the networkless operator boundary. Treat replacement of this root as a separate trust-root migration, not ordinary request-signing-key rotation.

## Build generation 1

Create a private draft with the signed contract and an explicit generation:

```json
{
  "contract": "principia-atlas-hosted-oidc-revocation-keyring-draft/0.2",
  "generation": 1,
  "keys": [
    {
      "public_key_file": "/secure/revocation-key-a-public.der",
      "not_before": 1800000000,
      "not_after": 1800600000
    }
  ],
  "revoked_key_ids": []
}
```

Sign and publish the immutable keyring:

```bash
node software/principia_atlas/hosted/revocation_request_cli.mjs keyring \
  --input /secure/revocation-keyring-generation-1.draft.json \
  --root-private-key-file /secure/revocation-keyring-root-private.der \
  --output /secure/revocation-keyring-generation-1.json
```

The command derives every key identifier, validates all windows, sorts key material deterministically, derives the root identifier, signs canonical JSON, refuses an existing output path, and creates the result without write or execute permissions.

## Activate signed anti-rollback mode

Mount the request, generation-1 keyring, and root public key read-only into the networkless operator:

```bash
node software/principia_atlas/hosted/auth_state_cli.mjs revoke-oidc-request \
  --state /state/auth-state.sqlite \
  --request-file /run/revocation-request.json \
  --request-keyring-file /run/revocation-keyring.json \
  --keyring-root-key-file /run/revocation-keyring-root-public.der
```

The first successful invocation stores generation `1`. This is the irreversible activation point. The older single-key and unsigned-keyring interfaces remain available only for pre-activation migration and are rejected after activation.

Expected evidence includes:

```json
{
  "authorization_keyring_generation": 1,
  "verified_keyring_generation": 1,
  "verified_keyring_root_id": "ed25519:ROOT_KEY_ID"
}
```

## Advance generations

For every trust change, copy the last reviewed draft, increment `generation` by exactly one, apply the key addition, retirement, or revocation, and sign it with the same offline root. Deploy the new immutable keyring before issuing requests that depend on the change.

A retry of an existing event under generation `2` can return:

```json
{
  "authorization_keyring_generation": 1,
  "verified_keyring_generation": 2,
  "replayed": true
}
```

The state floor becomes `2`, while the original receipt remains historically bound to generation `1`.

## Rollback behavior

After generation `2` has been observed, generation `1` is rejected even when its root signature, request signature, key validity, event, and target are otherwise valid. Copying an older keyring back into a mount cannot restore trust in a removed or revoked request-signing key.

Do not reset or delete `oidc_revocation_keyring_generation`. Doing so destroys the anti-rollback guarantee. Recovery must use the verified backup and offline restore tooling so the metadata floor and receipt columns move together.

## Incident response

For a compromised request-signing key, publish the next generation with the key identifier in `revoked_key_ids`. For a suspected keyring-root compromise, stop signed revocation automation, retain state and receipt evidence, and perform a separately reviewed root migration. Do not reuse a generation number with different keyring content.
