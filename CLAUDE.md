# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Builds Docker images (based on `rocker/verse`) that bundle R and Python
tooling used to generate the "volumes" (PDF/report deliverables) of Minas
Gerais's budget laws (LOA/PLOA — leis orçamentárias). See
[ADR 0001](docs/adr/0001-split-base-and-app-images.md) for why the build is
split into a base image and an app image, and their consequences.

There is no application code here — the repo is essentially two Dockerfiles,
build/release scripts, and TeX assets (`texmf/`) copied into the base image
for LaTeX/Sweave report rendering.

## Image structure

- **`base/Dockerfile`** — `rocker/verse:3.6.3`, OS build deps, Python 3.11
  built from source, Poetry, `diff-pdf`/`diff-so-fancy`, `texmf/` + `texhash`,
  the `Sweave.sty` patch, and a handful of generic R helper packages
  (`dotenv`, `writexl`, `here`, `futile.logger`). Changes rarely; bumped
  manually. Tagged `loamg:base.<n>`.
- **Root `Dockerfile`** — `FROM loamg:base.<n>` (hardcoded, not a build arg —
  see ADR 0001 Consequences). Installs Python project deps via
  `pyproject.toml`/Poetry (including `dpm`, pulled from
  `git+https://github.com/splor-mg/dpm.git@main`), then the three private
  splor-mg R packages (`relatorios`, `execucao`, `reest`) via
  `remotes::install_github()`, each authenticated with a `GITHUB_PAT` mounted
  as a Docker build secret. Tagged `loamg:<base>-<execucao>-<reest>-<relatorios>`.
  A new tag is published whenever any of those four components changes.

## Secrets: Infisical, not `.env`

All secrets (`GITHUB_PAT`, `DOCKERHUB_USERNAME`, `DOCKERHUB_IMAGE_NAME`,
`DOCKERHUB_TOKEN`) are stored in Infisical (see `.infisical.json` for the
workspace ID), not in a local `.env` file. Every script and `make` target that
needs them must be run through the Infisical CLI, e.g.:

```bash
infisical run -- make release
```

`scripts/build_image.sh` still writes a temporary `.env`-format file to satisfy
the existing `--mount=type=secret,id=secret` / `dotenv::load_dot_env()` step in
the root `Dockerfile` — it populates it from the `GITHUB_PAT` env var that
`infisical run` injects, so the Dockerfile itself is unchanged.

Bitbucket credentials are **no longer used anywhere** in this repo (the old
`requirements.in`/`uv`-pinned `dpm` dependency and the `renv`-based R package
resolution in CI are both gone per ADR 0001) — do not reintroduce them.

## Scripts (`scripts/`)

The build/release logic lives in scripts, not inline in the Makefile or the
CI YAML, specifically so it can be run identically locally and in CI:

- `scripts/lib/common.sh` — shared helpers, including `docker_login()`
  (`docker login` via `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN`, a Docker Hub
  access token, not the account password). Called by any script that pushes
  or pulls from Docker Hub — there's no ambient `docker login` session to
  rely on in CI, so every push/pull path authenticates explicitly.
- `scripts/build_image.sh --base=<n> --relatorios=<v> --execucao=<v> --reest=<v> [--push]`
  — builds the app image, labels it with the four version components
  (`io.splor.{base,relatorios,execucao,reest}_version`), and on `--push` logs
  in to Docker Hub, tags and pushes both the versioned tag and `:latest`, then
  creates and pushes a matching git tag `loamg-<base>-<execucao>-<reest>-<relatorios>`.
- `scripts/build_base_image.sh --n=<n> [--push]` — builds/pushes the base
  image. Base bumps are a deliberate manual decision; there's no
  auto-detection for this.
- `scripts/check_updates.sh` — logs in to Docker Hub, pulls `:latest`, reads
  the version labels off it, compares them against the latest GitHub tags for
  `relatorios`/`execucao`/`reest` (via `git ls-remote --tags`), and prints
  `key=value` lines including `update_needed=true|false`. This is how "what's
  currently deployed" is tracked — via the labels on the `:latest` image, not
  a separate lockfile.
- `scripts/check_and_build.sh` — orchestrator: runs `check_updates.sh`, and if
  updates were found, calls `build_image.sh --push` with the detected
  versions. Used by both `make release` and the daily CI job.

## Common commands

```bash
# Manual app-image build, versions passed explicitly
infisical run -- make build base=1 relatorios=v0.8.01.1 execucao=v0.5.27 reest=v0.2.8 push=1

# Manual base-image bump
infisical run -- make build-base n=2 push=1

# Check for upstream package updates without building
infisical run -- make check-updates

# Check for updates and build+push automatically if found
infisical run -- make release
```

## CI (`.github/workflows/publish_image.yaml`)

Runs daily (also `workflow_dispatch`-able). Authenticates to Infisical via a
machine identity (`INFISICAL_CLIENT_ID`/`INFISICAL_CLIENT_SECRET` GitHub
Actions secrets), then runs `infisical run -- make release` — the exact same
command used locally. There is no build/version logic duplicated in the
workflow YAML itself; all of it lives in `scripts/`.

## Base image bumps

Changing the base OS, R, or Python version requires:
1. Editing `base/Dockerfile`.
2. `infisical run -- make build-base n=<next> push=1`.
3. Updating the hardcoded `FROM loamg:base.<n>` in the root `Dockerfile`.

This is intentionally not automated (see ADR 0001).
