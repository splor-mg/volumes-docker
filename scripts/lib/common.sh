# Shared helpers for scripts/*.sh. Source, don't execute.

require_env() {
  local var_name="$1"
  if [ -z "${!var_name:-}" ]; then
    echo "Missing required env var: ${var_name} (run this via 'infisical run --')" >&2
    exit 1
  fi
}

remote_image() {
  require_env DOCKERHUB_USERNAME
  require_env DOCKERHUB_IMAGE_NAME
  echo "${DOCKERHUB_USERNAME}/${DOCKERHUB_IMAGE_NAME}"
}

docker_login() {
  require_env DOCKERHUB_USERNAME
  require_env DOCKERHUB_TOKEN
  echo "${DOCKERHUB_TOKEN}" | docker login --username "${DOCKERHUB_USERNAME}" --password-stdin
}

label_value() {
  # $1 = image ref, $2 = label key
  docker inspect --format "{{ index .Config.Labels \"$2\" }}" "$1" 2>/dev/null || true
}

latest_upstream_tag() {
  # $1 = repo name under splor-mg (e.g. relatorios)
  git ls-remote --tags --refs "https://github.com/splor-mg/$1.git" \
    | awk -F/ '{print $NF}' \
    | sort -V | tail -n1
}
