# 2. Scripted release process, Docker-Hub-label version tracking, and Infisical secrets

## Status

Accepted

## Context

[ADR 0001](0001-split-base-and-app-images.md) split the build into a base
image and an app image, but explicitly left the release automation stale:
`.github/workflows/publish_image.yaml`, the `Makefile`, `README.md`, and
`CLAUDE.md` still described the old single-`Dockerfile`, Bitbucket/`renv`-based
process. Concretely, the old CI workflow:

- Used `uv pip compile requirements.in > requirements.txt` and an `renv`-based
  R package resolution authenticated against Bitbucket, neither of which
  exist anymore — `dpm` and the three private R packages
  (`relatorios`/`execucao`/`reest`) are installed from GitHub via
  `pyproject.toml`/Poetry and `remotes::install_github()` respectively (see
  ADR 0001), and Bitbucket credentials are not used anywhere in the current
  build.
- Hardcoded package versions directly in the workflow YAML
  (`--build-arg relatorios_version=v0.7.64 ...`), so a version bump meant
  editing and committing a change to the workflow file itself.
- Built the image with a fixed tag (`volumes:ploa2025`) that didn't reflect
  the two-image split or the new `loamg` naming.
- Wrote Bitbucket credentials to a local `.env` file read by the Dockerfile's
  `--mount=type=secret` step — the only place secrets were sourced from.
- Had no equivalent process for building/publishing the new base image at
  all.
- Inlined all of this logic directly in the workflow YAML, so none of it
  could be run locally without editing the workflow file — you couldn't
  reproduce what CI does, or run a release manually, without hand-copying
  `docker buildx build` commands.

Separately, the team decided to stop keeping secrets (`GITHUB_PAT`, Docker Hub
credentials, image naming) in a local `.env` file at all, moving them to
[Infisical](https://infisical.com/) instead, so they can be managed and
rotated in one place and shared consistently between local runs and CI.

## Decision

### Logic lives in scripts, not in the Makefile or the CI YAML

All build/check/release logic was extracted into `scripts/*.sh`, so the exact
same commands run locally and in CI:

- `scripts/build_image.sh --base=<n> --relatorios=<v> --execucao=<v> --reest=<v> [--push]`
  builds the app image from the root `Dockerfile`, labels it with
  `io.splor.{base,relatorios,execucao,reest}_version` OCI labels, and on
  `--push` logs in to Docker Hub, pushes both the versioned tag
  (`<base>-<execucao>-<reest>-<relatorios>`) and `:latest`, then creates and
  pushes a matching git tag `loamg-<base>-<execucao>-<reest>-<relatorios>`.
- `scripts/build_base_image.sh --n=<n> [--push]` builds/pushes the base image
  from `base/Dockerfile`, tagged `loamg:base.<n>`. Base bumps stay a
  deliberate, manual decision (per ADR 0001) — there is no auto-detection or
  scheduled check for this, only explicit invocation with a new `--n`.
- `scripts/check_updates.sh` pulls the published `:latest` app image, reads
  its version labels, compares them against the latest GitHub tags for
  `relatorios`/`execucao`/`reest` (`git ls-remote --tags`), and prints
  `key=value` lines including `update_needed=true|false`.
- `scripts/check_and_build.sh` orchestrates the two: runs
  `check_updates.sh`, and if it reports `update_needed=true`, calls
  `build_image.sh --push` with the detected versions.
- `scripts/lib/common.sh` holds shared helpers (`require_env`,
  `remote_image`, `docker_login`, `label_value`, `latest_upstream_tag`).

The `Makefile` and the CI workflow are both now thin callers of these
scripts — see below.

### Version tracking: OCI labels on `:latest`, not a lockfile or renv

The R package check no longer uses `renv`/Bitbucket at all. Instead,
"what's currently deployed" is read directly off the published Docker image:
`build_image.sh` bakes each of the four version components in as OCI labels
at build time, and `check_updates.sh` reads them back off `:latest` via
`docker inspect`. There is no separate lockfile or versions file to keep in
sync with what was actually published — the running image is the source of
truth.

Each successful `--push` also creates a git tag
(`loamg-<base>-<execucao>-<reest>-<relatorios>`) as a human-readable release
record, but it is not what `check_updates.sh` reads from — the Docker label
is.

### Docker Hub auth: explicit `docker login` via a token, not an ambient session

Every script that pushes to or pulls from Docker Hub (`build_image.sh`,
`build_base_image.sh`, `check_updates.sh`) calls `docker_login()` first,
which runs `docker login` non-interactively using `DOCKERHUB_USERNAME` and
`DOCKERHUB_TOKEN` (a Docker Hub access token, not the account password).
This was necessary because CI has no pre-existing local `docker login`
session to rely on — the first attempt at `make build-base ... push=1`
failed locally with `denied: requested access to the resource is denied`
because nothing in the scripts authenticated to Docker Hub before pushing.

### Secrets: Infisical, not `.env`

`GITHUB_PAT`, `DOCKERHUB_USERNAME`, `DOCKERHUB_IMAGE_NAME`, and
`DOCKERHUB_TOKEN` are stored in Infisical (workspace ID in `.infisical.json`)
instead of a local `.env` file. Every script and `make` target that needs
them is run through the Infisical CLI:

```bash
infisical run -- make release
```

`DOCKERHUB_USERNAME` and `DOCKERHUB_IMAGE_NAME` are read from the environment
rather than hardcoded in the scripts, so the Docker Hub account or image name
can change without a code change.

`build_image.sh` still writes a temporary `.env`-format file to satisfy the
root `Dockerfile`'s existing `--mount=type=secret,id=secret` /
`dotenv::load_dot_env()` step — it populates that file from the `GITHUB_PAT`
env var that `infisical run` injects, so the Dockerfile itself did not need
to change.

Bitbucket credentials (`BITBUCKET_AUTH_USER`/`BITBUCKET_APP_PASSWORD`,
formerly in `.env.example`) are removed entirely — they are not used
anywhere in the current build.

### Makefile: kept, thinned to a wrapper around the scripts

Make was kept (rather than migrating to taskipy) specifically for its
argument-passing ergonomics — `make build base=1 relatorios=v0.8.01.1 ...` —
which taskipy does not offer any advantage over. Each target is now a
one-line call into the corresponding script:

```bash
infisical run -- make build base=1 relatorios=v0.8.01.1 execucao=v0.5.27 reest=v0.2.8 push=1
infisical run -- make build-base n=2 push=1
infisical run -- make check-updates
infisical run -- make release
```

### CI: same command as local, on a daily schedule

`.github/workflows/publish_image.yaml` was rewritten to:

1. Check out the repo.
2. Install the Infisical CLI.
3. Authenticate to Infisical using a machine identity (Universal Auth:
   `INFISICAL_CLIENT_ID`/`INFISICAL_CLIENT_SECRET` GitHub Actions secrets),
   Infisical's current recommended auth method over the legacy service
   token.
4. Run `infisical run --client-id=... --client-secret=... --env=dev -- make release` —
   the exact same command available locally, against the `dev` Infisical
   environment.

The schedule changed from weekly (`0 0 * * 1`) to daily (`0 0 * * *`), since
`check_and_build.sh` is now cheap to run when nothing has changed (it exits
after `check_updates.sh` reports `update_needed=false`, without building
anything).

None of the build/version/check logic is duplicated in the workflow YAML —
all of it lives in `scripts/`, so it can be reproduced identically by running
the same `infisical run -- make ...` commands locally.

## Consequences

- **Locally reproducible CI.** Any release CI performs can be run and
  debugged locally with the identical command
  (`infisical run -- make release`), rather than only being runnable inside
  GitHub Actions.
- **No more hand-edited version bumps in the workflow file.** Versions are
  either passed explicitly to `make build` or auto-detected by
  `check_updates.sh` from GitHub tags — never hardcoded in YAML.
- **Docker Hub is the version source of truth.** There's no lockfile to fall
  out of sync with what was actually published; `check_updates.sh` always
  reflects the real `:latest` image. This does mean `check_updates.sh` (and
  any push) requires network access to Docker Hub and GitHub, and a
  `DOCKERHUB_TOKEN` with at least pull access even to _check_ for updates.
- **New required Infisical secret: `DOCKERHUB_TOKEN`.** Anyone running these
  scripts — locally or in CI — now needs this in addition to the existing
  `GITHUB_PAT`/`DOCKERHUB_USERNAME`/`DOCKERHUB_IMAGE_NAME`. It must be a
  Docker Hub access token (Account Settings → Security), not the account
  password.
- **Base image publishing still has no update-check automation**, by
  design — base bumps stay a deliberate `make build-base n=<next> push=1`
  call, consistent with ADR 0001's decision that this should never happen
  implicitly.
- **`README.md`/`CLAUDE.md` rewritten** to match this process and drop all
  Bitbucket/`.env` instructions; `.env.example` was deleted.
- **Not yet end-to-end tested.** `make build-base n=1 push=1` was run
  locally and confirmed the build step works; the push step was only
  validated after adding `docker_login()` in response to a `denied: ...`
  error on the first attempt. A full `make release` / `make build` (app
  image) run, and a full CI run, have not yet been exercised as of this
  writing.
