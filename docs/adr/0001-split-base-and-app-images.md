# 1. Split the image into a base image and an app image

## Status

Accepted

## Context

The image built by this repo bundles R/Python tooling used to generate LOA/PLOA
report deliverables. A single `Dockerfile` built everything on every release:

- `rocker/verse:3.6.3` as the base OS/R environment.
- OS build dependencies (`build-essential`, `libssl-dev`, etc.).
- Python 3.11 built from source (`make altinstall`), since the base image
  doesn't ship it.
- `diff-pdf` and `diff-so-fancy`, built from source, used for report
  diffing/QA.
- `texmf/` copied into the image's local TeX tree, then `texhash`.
- A patch to `Sweave.sty` to use Helvetica instead of the `ae` package.
- Python dependencies from `requirements.txt` (including `dpm`, pinned to a
  Bitbucket commit).
- A handful of generic R helper packages (`dotenv`, `writexl`, `here`,
  `futile.logger`).
- The three private splor-mg R packages actually maintained by this team —
  `relatorios`, `execucao`, `reest` — installed from GitHub at versions passed
  in as build args, authenticated via a `GITHUB_PAT` mounted as a Docker
  build secret.

In practice, only the last group — the three private R packages — changes on
anything resembling a regular cadence. Everything else (base OS/R version,
Python build, TeX assets, QA tooling) changes rarely, if ever: bumping
`rocker/verse` or the Python version is a breaking change for every downstream
project consuming this image, and is not something the team is currently able
to do. Despite that, every release rebuilt all of it from scratch — recompiling
Python from source, rebuilding `diff-pdf`/`diff-so-fancy`, reprocessing TeX —
just to pick up a new `relatorios`/`execucao`/`reest` version.

This made releases slow, and conflated two things that change at very
different rates and for very different reasons.

## Decision

Split the single `Dockerfile` into two:

1. **`base/Dockerfile`** — everything that changes rarely and requires a
   deliberate, manual decision to bump:
   - `rocker/verse:3.6.3`
   - OS build dependencies
   - Python 3.11 built from source, plus Poetry (installed via
     `python3 -m pip install poetry`, no project dependencies yet)
   - `diff-pdf` and `diff-so-fancy`
   - `texmf/` copy + `texhash`
   - The `Sweave.sty` patch
   - The generic R helper packages (`dotenv`, `writexl`, `here`,
     `futile.logger`) — these are not versioned per-release and are not the
     packages this team maintains, so they live alongside the rest of the
     rarely-changing environment.

   Built and tagged manually, independent of the release process:
   `loamg:base.<n>` (plain incrementing integer, e.g. `loamg:base.1`).

2. **Root `Dockerfile`** — the actual per-release artifact:
   - `FROM loamg:base.<n>`, with the base tag hardcoded in the Dockerfile
     (not a build arg, for now — see Consequences).
   - Copies `pyproject.toml` and runs `poetry install` to install Python
     project dependencies (`pytest`, `frictionless[excel,html]`,
     `pandas[excel,html]`, and `dpm` — now pulled directly from
     `git+https://github.com/splor-mg/dpm.git@main` instead of a
     Bitbucket-pinned commit, since `dpm` has moved to GitHub).
   - The three `remotes::install_github(...)` secret-mount steps for
     `relatorios`, `execucao`, `reest`, unchanged from before.

   Tagged as `loamg:<base>-<execucao>-<reest>-<relatorios>`, e.g.
   `loamg:1-0.5.27-0.2.8-0.8.1`. A new tag is published every time any one of
   those four components changes.

Additionally:

- `requirements.in`/`requirements.txt` (the `uv`-managed pins) are removed,
  replaced by `pyproject.toml` declaring the current package set directly, with
  no migration of historical pins.
- The image name no longer uses `volumes` (to avoid the generic, overloaded
  term) — the new name is `loamg`.
- The `Makefile`, `README.md`, `CLAUDE.md`, and the CI workflow
  (`.github/workflows/publish_image.yaml`) are intentionally left unchanged in
  this pass. Updating them (in particular, having CI build/tag/push the app
  image against the base image, and deciding whether/how the base image gets
  its own publish flow) is deferred to a follow-up decision.

### Implementation notes

Two issues surfaced while building the split images that needed fixing in
`base/Dockerfile`:

1. Poetry's environment detection probes `/usr/bin/python`, which does not
   exist in this image (only `python3.11`/`python3` were installed via
   `make altinstall`). `poetry install` failed with
   `Command '['/usr/bin/python', '-Ic', 'import sys; print(sys.executable)']'
   returned non-zero exit status 2`. Fixed by also symlinking
   `/usr/bin/python -> python3.11` in the base image.
2. `/usr/bin/python` already existed in the base image (likely a Python 2
   stub from Debian Buster), so the symlink had to be created with `ln -sf`
   rather than `ln -s`, or the build would fail with
   `ln: failed to create symbolic link '/usr/bin/python': File exists`.

Both images were built and smoke-tested locally:

```bash
docker buildx build --load --tag loamg:base.1 -f base/Dockerfile .

docker buildx build --load --tag loamg:1-0.5.27-0.2.8-0.8.1 \
  --secret id=secret,src=.env \
  --build-arg relatorios_version=v0.8.01.1 \
  --build-arg execucao_version=v0.5.27 \
  --build-arg reest_version=v0.2.8 \
  .

docker run --rm loamg:1-0.5.27-0.2.8-0.8.1 \
  "Rscript -e 'library(relatorios); library(execucao); library(reest)'"

docker run --rm loamg:1-0.5.27-0.2.8-0.8.1 \
  "python3 -c 'import pandas, frictionless, dpm'"
```

Both R and Python packages load correctly in the resulting image.

## Consequences

- **Faster, cheaper releases.** A normal release (bumping one of the three R
  packages) no longer recompiles Python from source, rebuilds `diff-pdf`, or
  reprocesses TeX — it only reinstalls Python project deps via Poetry and the
  changed R package(s).
- **Explicit, deliberate base bumps.** Changing the base OS, R, or Python
  version now requires a conscious `base/Dockerfile` build and a new
  `loamg:base.<n>` tag, rather than happening implicitly as a side effect of
  every release.
- **Hardcoded base tag is a known rough edge.** The root `Dockerfile` currently
  hardcodes `FROM loamg:base.<n>`, meaning every base bump requires editing
  and committing a change to the root `Dockerfile` as well. This was a
  deliberate simplification for this first change; parameterizing it (e.g. via
  a build arg) is left for a later iteration.
- **CI, `Makefile`, `README.md`, and `CLAUDE.md` are now stale/incomplete**
  relative to the new two-image structure and need a follow-up pass — in
  particular, CI still builds the old single-Dockerfile flow, and none of the
  base-image build/publish process is automated yet.
- **`dpm` no longer requires Bitbucket credentials** for image builds, since it
  now installs from GitHub via `pyproject.toml`/Poetry rather than the old
  `requirements.in`/`uv` Bitbucket-commit pin. The Bitbucket credentials in
  `.env` are still used for other purposes noted in `CLAUDE.md` and were not
  removed.
- **No historical Python version pins.** `pyproject.toml` declares the current
  package set without a lockfile migration from `requirements.txt`; a
  `poetry.lock` will be generated fresh going forward.
