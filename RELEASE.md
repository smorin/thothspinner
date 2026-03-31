# Release Guide

This document covers the full release process for ThothSpinner — from toolchain architecture through the step-by-step workflow, CI/CD pipeline internals, OIDC trusted publishing setup, and troubleshooting.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Versioning](#versioning)
- [Release Checklist](#release-checklist)
- [Step-by-Step Release Process](#step-by-step-release-process)
- [CI/CD Pipeline](#cicd-pipeline)
- [OIDC Trusted Publishing Setup](#oidc-trusted-publishing-setup)
- [Local Build & Publish](#local-build--publish)
- [Troubleshooting](#troubleshooting)

---

## Architecture

The release stack is built entirely on [uv](https://docs.astral.sh/uv/) — no hatch, no twine, no separate publish action.

```
┌─────────────────────────────────────────────────────────┐
│                    Release Pipeline                      │
│                                                          │
│  git tag v*                                              │
│      │                                                   │
│      ▼                                                   │
│  GitHub Actions: publish.yml                            │
│      │                                                   │
│      ├── [build job]                                     │
│      │       uv build  ──►  dist/*.whl + dist/*.tar.gz  │
│      │                                                   │
│      ├── [publish-testpypi job]                          │
│      │       uv publish --trusted-publishing always      │
│      │       --index-url https://test.pypi.org/legacy/  │
│      │                                                   │
│      └── [publish-pypi job]                              │
│              uv publish --trusted-publishing always      │
└─────────────────────────────────────────────────────────┘
```

### Toolchain

| Concern | Tool | Details |
|---------|------|---------|
| Build backend | `uv_build` | PEP 517 backend, bundled with uv |
| Package manager | `uv` | Dependency resolution, venv, lock file |
| Build | `uv build` | Produces wheel (`.whl`) and source dist (`.tar.gz`) |
| Publish | `uv publish` | Uploads to PyPI/TestPyPI via OIDC or token |
| Task runner | `just` | Wraps uv commands for local convenience |
| CI/CD | GitHub Actions | Automated test, lint, typecheck, publish |
| Auth | OIDC trusted publishing | No stored API tokens — GitHub mints short-lived tokens |

### Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, version, build-system config |
| `uv.lock` | Locked dependency graph (committed to repo) |
| `.github/workflows/ci.yml` | Runs tests, lint, typecheck on push/PR |
| `.github/workflows/publish.yml` | Builds and publishes on `v*` tag push |
| `justfile` | Local task automation (`just build`, `just release`) |
| `CHANGELOG.md` | Release notes, one section per version |

---

## Prerequisites

**Required:**
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [just](https://github.com/casey/just) — install with `brew install just` or `cargo install just`
- Git with push access to `main` and tag push rights on the repo

**For manual publishing (bypassing CI):**
- A PyPI API token, or OIDC trusted publishing configured for your local environment

**Verify your environment:**
```bash
make check   # checks for uv, python3, just
```

---

## Versioning

ThothSpinner uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

| Increment | When |
|-----------|------|
| `PATCH` | Bug fixes, dependency bumps, documentation changes |
| `MINOR` | New backward-compatible features, new components |
| `MAJOR` | Breaking API changes |

The version is declared statically in one place:

```toml
# pyproject.toml
[project]
version = "1.0.0"
```

Git tags follow the `v{version}` format (e.g., `v1.2.3`). The tag is the release trigger — pushing a `v*` tag kicks off the full publish workflow.

---

## Release Checklist

Before creating a release, verify all of the following:

- [ ] All CI checks pass on `main` (`push` triggers `ci.yml`)
- [ ] Test coverage is at or above 90% (`just test-cov`)
- [ ] `pyproject.toml` version is updated to the new version
- [ ] `CHANGELOG.md` has an entry for the new version with release date
- [ ] `README.md` footer version badge is updated (if applicable)
- [ ] No uncommitted changes (`git status` is clean)
- [ ] You are on the `main` branch

---

## Step-by-Step Release Process

### 1. Update the version

Edit `pyproject.toml` line 3:

```toml
[project]
version = "1.2.3"   # new version
```

### 2. Update CHANGELOG.md

Add a section at the top (below the `# Changelog` header):

```markdown
## [1.2.3] - 2026-04-15

### Added
- ...

### Fixed
- ...

### Changed
- ...
```

### 3. Run all checks locally

```bash
just all
```

This runs `format → lint → typecheck → test` in sequence. All must pass.

### 4. Commit the release

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v1.2.3"
git push origin main
```

Wait for the CI pipeline (`ci.yml`) to go green on `main`.

### 5. Tag and push

```bash
just release 1.2.3
```

This runs:
1. `just clean` — removes `dist/` and caches
2. `uv build` — builds fresh wheel and source distribution
3. `git tag v1.2.3`
4. `git push origin v1.2.3` — triggers `publish.yml`

Or manually if you prefer:

```bash
git tag v1.2.3
git push origin v1.2.3
```

### 6. Monitor the publish workflow

Go to the **Actions** tab on GitHub and watch the `Publish to PyPI` workflow:

1. **Build** — builds `dist/*.whl` and `dist/*.tar.gz`
2. **Publish to TestPyPI** — validates the package on [test.pypi.org](https://test.pypi.org/project/thothspinner/)
3. **Publish to PyPI** — publishes to [pypi.org/project/thothspinner/](https://pypi.org/project/thothspinner/)

Each publish job requires manual approval via its GitHub environment (`testpypi` → `pypi`) if environment protection rules are configured.

### 7. Verify the release

```bash
# Install from PyPI in a clean environment
uvx --from thothspinner python -c "import thothspinner; print(thothspinner.__version__)"

# Or with pip
pip install thothspinner==1.2.3
```

---

## CI/CD Pipeline

### `ci.yml` — Continuous Integration

Triggered on every push to `main` and every pull request targeting `main`.

```
push/PR to main
    │
    ├── test (matrix: Python 3.11, 3.12, 3.13)
    │       uv sync --all-extras
    │       uv run pytest
    │
    ├── lint
    │       uv run ruff format --check .
    │       uv run ruff check .
    │
    └── typecheck
            uv run ty check src/
```

All three jobs run in parallel. A PR cannot merge if any job fails.

### `publish.yml` — Release Publishing

Triggered only on tag pushes matching `v*` (e.g., `v1.0.0`, `v2.3.1`).

```
push tag v*
    │
    └── build (ubuntu-latest)
            astral-sh/setup-uv@v5
            uv build
            upload artifact: dist/
                │
                └── publish-testpypi (environment: testpypi)
                        permissions: id-token: write
                        uv publish --trusted-publishing always
                        --index-url https://test.pypi.org/legacy/
                            │
                            └── publish-pypi (environment: pypi)
                                    permissions: id-token: write
                                    uv publish --trusted-publishing always
```

Jobs are sequential: `build → publish-testpypi → publish-pypi`. A failure at any stage stops the pipeline.

---

## OIDC Trusted Publishing Setup

ThothSpinner uses [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) via OpenID Connect (OIDC). No API tokens are stored as GitHub secrets — GitHub Actions mints a short-lived OIDC token that PyPI accepts directly.

### How It Works

1. The workflow requests an OIDC token from GitHub (`id-token: write` permission)
2. `uv publish --trusted-publishing always` presents the token to PyPI
3. PyPI validates the token against the registered trusted publisher configuration
4. If valid, the upload is accepted

### Initial Setup (one-time, per maintainer)

You must register the GitHub Actions workflow as a trusted publisher on both PyPI and TestPyPI before the first release.

**On TestPyPI** ([test.pypi.org/manage/account/publishing/](https://test.pypi.org/manage/account/publishing/)):

| Field | Value |
|-------|-------|
| PyPI Project Name | `thothspinner` |
| Owner | `smorin` |
| Repository name | `thothspinner` |
| Workflow filename | `publish.yml` |
| Environment name | `testpypi` |

**On PyPI** ([pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/)):

| Field | Value |
|-------|-------|
| PyPI Project Name | `thothspinner` |
| Owner | `smorin` |
| Repository name | `thothspinner` |
| Workflow filename | `publish.yml` |
| Environment name | `pypi` |

### GitHub Environments

Two GitHub environments must exist in the repository settings ([Settings → Environments](https://github.com/smorin/thothspinner/settings/environments)):

- **`testpypi`** — used by the `publish-testpypi` job
- **`pypi`** — used by the `publish-pypi` job

Optionally add required reviewers to the `pypi` environment for an approval gate before production publishing.

---

## Local Build & Publish

These commands are available for testing builds or publishing manually (e.g., from a maintainer's machine with a token).

```bash
# Build wheel + source distribution
just build
# Output: dist/thothspinner-1.2.3-py3-none-any.whl
#         dist/thothspinner-1.2.3.tar.gz

# Publish to TestPyPI (for validation)
UV_PUBLISH_TOKEN=<your-testpypi-token> just publish-test

# Publish to PyPI
UV_PUBLISH_TOKEN=<your-pypi-token> just publish

# Full release (clean → build → tag → push)
just release 1.2.3
```

To inspect a built distribution before publishing:

```bash
uvx twine check dist/*
```

---

## Troubleshooting

### Build fails: `uv_build` not found

Ensure uv is up to date. `uv_build` is distributed as part of uv's bundled backend — it does not need to be installed separately.

```bash
uv self update
uv build
```

### Publish fails: `403 Forbidden` on PyPI

The OIDC trusted publisher is not configured, or the environment name / workflow filename does not match exactly what was registered on PyPI. Verify:

1. The workflow file is named `publish.yml` (not `publish.yaml`)
2. The environment in the workflow job matches the environment registered on PyPI (`pypi` / `testpypi`)
3. The repository owner and name match

### Publish fails: `400 File already exists`

A distribution with this version already exists on PyPI. PyPI does not allow overwriting. You must bump the version and release again.

### Tag was pushed but workflow did not trigger

Confirm the tag matches the `v*` pattern (e.g., `v1.2.3` not `1.2.3`). Check the Actions tab — filter by the `Publish to PyPI` workflow.

### TestPyPI publish succeeds but PyPI job is blocked

If the `pypi` GitHub environment has required reviewers configured, you must approve the deployment from the Actions UI before the job runs.

### Version on PyPI doesn't match `pyproject.toml`

The build is stamped with whatever version is in `pyproject.toml` at the time `uv build` runs. Ensure the version was committed before the tag was pushed.
