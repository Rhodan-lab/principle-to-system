#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PIN="$(tr -d '\r\n' < "$REPO_ROOT/software/one_website/atlas-commit.txt")"
if ! [[ "$PIN" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Invalid exact Atlas commit pin" >&2
  exit 1
fi
ATLAS_TEMP="$(mktemp -d /tmp/principia-atlas-source.XXXXXXXX)"
trap 'rm -rf "$ATLAS_TEMP"' EXIT
git clone --quiet https://github.com/Rhodan-lab/Atlas.git "$ATLAS_TEMP/repo"
git -C "$ATLAS_TEMP/repo" checkout --quiet --detach "$PIN"
ACTUAL="$(git -C "$ATLAS_TEMP/repo" rev-parse HEAD)"
if [[ "$ACTUAL" != "$PIN" ]]; then
  echo "Atlas checkout does not match exact source pin" >&2
  exit 1
fi
python3 -m pip install --disable-pip-version-check -r "$ATLAS_TEMP/repo/tools/foundation-validator/requirements.txt"
cd "$REPO_ROOT"
python3 software/one_website/build.py build --atlas-repo "$ATLAS_TEMP/repo" --output "$REPO_ROOT/dist"
python3 software/one_website/build.py verify --output "$REPO_ROOT/dist"
echo "Unified read-only Principia & Atlas website prepared under dist/"
