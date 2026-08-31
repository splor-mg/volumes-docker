# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Builds a single Docker image (based on `rocker/verse`) that bundles R and Python
tooling used to generate the "volumes" (PDF/report deliverables) of Minas Gerais's
budget laws (LOA/PLOA — leis orçamentárias). The image installs three private
splor-mg R packages (`relatorios`, `execucao`, `reest`) from GitHub at pinned
versions, plus a Python toolchain (built from source) with the `dpm` package
installed from a Bitbucket-versioned commit in `requirements.txt`.

There is no application code here — the repo is essentially a `Dockerfile`,
build tooling, and TeX assets (`texmf/`) copied into the image for LaTeX/Sweave
report rendering.

## Setup

Create `.env` from the template and fill in Bitbucket credentials (used both to
pull the `dpm` git dependency via `uv` and, at build time, mounted into Docker
as a secret so `remotes::install_github()` can authenticate with `GITHUB_PAT`):

```bash
cp .env.example .env
# edit .env: BITBUCKET_AUTH_USER, BITBUCKET_APP_PASSWORD
```

## Common commands

Update Python dependency pins (must use `uv`, not plain `pip-compile`, so the
lockfile captures the git commit SHA of `dpm`):

```bash
uv pip compile requirements.in > requirements.txt
```

Build the image (via the `Makefile`, which wires `.env` in as a Docker build
secret and passes through the three R package versions as build args):

```bash
make image=loa2027.1 relatorios=v0.8.01.1 execucao=v0.5.27 reest=v0.2.8
```

This runs:

```bash
docker buildx build --tag volumes:$(image) --secret id=secret,src=.env \
  --build-arg relatorios_version=$(relatorios) \
  --build-arg execucao_version=$(execucao) \
  --build-arg reest_version=$(reest) .
```

Publish to Docker Hub (manual, after `docker login`):

```bash
docker tag volumes:loa2027.1 aidsplormg/volumes:loa2027.1
docker push aidsplormg/volumes:loa2027.1
```

## CI (`.github/workflows/publish_image.yaml`)

A weekly (Monday) scheduled job (also `workflow_dispatch`-able) that:
1. Regenerates `requirements.txt` via `uv pip compile` and commits it if changed.
2. Regenerates `requirements_R.txt` via `renv::install()` + `installed.packages()`
   and commits it if changed (uses `BITBUCKET_USER`/`BITBUCKET_PASSWORD` secrets
   for private R package resolution).
3. If any `**.txt` file changed, builds the image with hardcoded
   `relatorios`/`execucao`/`reest` versions and pushes the commits back to `main`.

Note the R/Python package versions baked into this workflow are separate from
the ones passed to `make` locally — update both when bumping a pinned version
for a new release.

## Dockerfile structure

Build stages, in order: install OS build deps → build Python 3.11 from source
(`make altinstall`, since the base image doesn't ship it) → build `diff-pdf`
and `diff-so-fancy` from source (used for report diffing/QA) → copy `texmf/`
into the image's local TeX tree and `texhash` → patch `Sweave.sty` to use
Helvetica instead of the `ae` package → `pip install -r requirements.txt` →
install a handful of R packages, then the three private splor-mg R packages,
each via a separate `RUN --mount=type=secret,id=secret` step that loads
`GITHUB_PAT` from the mounted `.env` secret.

When bumping the base image or Debian version, check whether the commented-out
`archive.debian.org` sed block at the top needs to be re-enabled (it was needed
for EOL'd Buster/rocker 3.6.3 repos, currently disabled for the 4.0.0 base).
