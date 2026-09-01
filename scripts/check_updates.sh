#!/usr/bin/env bash
# Compare the versions baked into the currently published `:latest` app image
# (read from its OCI labels) against the latest GitHub tags for relatorios,
# execucao, and reest. Prints key=value lines (also usable with
# `>> "$GITHUB_OUTPUT"` in Actions).
#
# Requires env vars (typically injected via `infisical run --`):
#   DOCKERHUB_USERNAME, DOCKERHUB_IMAGE_NAME, DOCKERHUB_TOKEN
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/lib/common.sh

remote="$(remote_image)"

docker_login
docker pull "${remote}:latest" >/dev/null

base_current=$(label_value "${remote}:latest" io.splor.base_version)
relatorios_current=$(label_value "${remote}:latest" io.splor.relatorios_version)
execucao_current=$(label_value "${remote}:latest" io.splor.execucao_version)
reest_current=$(label_value "${remote}:latest" io.splor.reest_version)

relatorios_latest=$(latest_upstream_tag relatorios)
execucao_latest=$(latest_upstream_tag execucao)
reest_latest=$(latest_upstream_tag reest)

changed=false
[ "$relatorios_latest" != "$relatorios_current" ] && changed=true
[ "$execucao_latest" != "$execucao_current" ] && changed=true
[ "$reest_latest" != "$reest_current" ] && changed=true

echo "base=${base_current}"
echo "relatorios=${relatorios_latest}"
echo "execucao=${execucao_latest}"
echo "reest=${reest_latest}"
echo "update_needed=${changed}"
