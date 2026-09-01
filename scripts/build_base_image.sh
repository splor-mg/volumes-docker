#!/usr/bin/env bash
# Build (and optionally push) the base image from base/Dockerfile.
#
# Base bumps are a deliberate, manual decision (see docs/adr/0001) — there is
# no auto-check for this, only explicit invocation with a new --n.
#
# Requires env vars (typically injected via `infisical run --`) when pushing:
#   DOCKERHUB_USERNAME, DOCKERHUB_IMAGE_NAME, DOCKERHUB_TOKEN
#
# Usage:
#   ./scripts/build_base_image.sh --n=1 [--push]
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
source scripts/lib/common.sh

push=false
for arg in "$@"; do
  case "$arg" in
    --n=*) n="${arg#*=}" ;;
    --push) push=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

: "${n:?missing --n}"

local_image="loamg:base.${n}"

docker buildx build \
  --load \
  --tag "$local_image" \
  -f base/Dockerfile \
  .

echo "Built ${local_image}"

if [ "$push" = true ]; then
  remote="$(remote_image)"
  docker_login
  docker tag "$local_image" "${remote}:base.${n}"
  docker push "${remote}:base.${n}"
  echo "Pushed ${remote}:base.${n}"
fi
