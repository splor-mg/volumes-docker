#!/usr/bin/env bash
# Build (and optionally push) the app image from the root Dockerfile.
#
# Requires env vars (typically injected via `infisical run --`):
#   GITHUB_PAT, DOCKERHUB_USERNAME, DOCKERHUB_IMAGE_NAME, DOCKERHUB_TOKEN (last
#   three only when --push)
#
# Usage:
#   ./scripts/build_image.sh --base=1 --relatorios=v0.8.01.1 --execucao=v0.5.27 --reest=v0.2.8 [--push]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/lib/common.sh

push=false
for arg in "$@"; do
  case "$arg" in
    --base=*) base="${arg#*=}" ;;
    --relatorios=*) relatorios="${arg#*=}" ;;
    --execucao=*) execucao="${arg#*=}" ;;
    --reest=*) reest="${arg#*=}" ;;
    --push) push=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

: "${base:?missing --base}"
: "${relatorios:?missing --relatorios}"
: "${execucao:?missing --execucao}"
: "${reest:?missing --reest}"
require_env GITHUB_PAT

tag="${base}-${execucao}-${reest}-${relatorios}"
local_image="loamg:${tag}"

secret_file="$(mktemp)"
trap 'rm -f "$secret_file"' EXIT
echo "GITHUB_PAT=${GITHUB_PAT}" > "$secret_file"

docker buildx build \
  --load \
  --tag "$local_image" \
  --secret id=secret,src="$secret_file" \
  --build-arg relatorios_version="$relatorios" \
  --build-arg execucao_version="$execucao" \
  --build-arg reest_version="$reest" \
  --label "io.splor.base_version=${base}" \
  --label "io.splor.relatorios_version=${relatorios}" \
  --label "io.splor.execucao_version=${execucao}" \
  --label "io.splor.reest_version=${reest}" \
  .

echo "Built ${local_image}"

if [ "$push" = true ]; then
  remote="$(remote_image)"
  docker_login
  docker tag "$local_image" "${remote}:${tag}"
  docker tag "$local_image" "${remote}:latest"
  docker push "${remote}:${tag}"
  docker push "${remote}:latest"

  git_tag="loamg-${tag}"
  git tag "$git_tag"
  git push origin "$git_tag"

  echo "Pushed ${remote}:${tag}, ${remote}:latest, and git tag ${git_tag}"
fi

echo "tag=${tag}"
