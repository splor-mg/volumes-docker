#!/usr/bin/env bash
# Orchestrator: check for relatorios/execucao/reest updates, and if any are
# found, build and push a new app image with the detected versions. Used both
# by the daily CI schedule and locally (`infisical run -- make release`).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

result="$(./scripts/check_updates.sh)"
echo "$result"
eval "$result"

if [ "$update_needed" != "true" ]; then
  echo "No package updates found; nothing to build."
  exit 0
fi

./scripts/build_image.sh \
  --base="$base" \
  --relatorios="$relatorios" \
  --execucao="$execucao" \
  --reest="$reest" \
  --push
