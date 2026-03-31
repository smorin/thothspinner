# First-Time PyPI Publish — v1.0.0 Step-by-Step

This guide covers the **one-time setup and first publish** of thothspinner to PyPI.
For subsequent releases, see [RELEASE.md](RELEASE.md).

---

## Overview

The publish pipeline works like this:

```
Commit & push to main  →  Configure OIDC (one-time)  →  just release 1.0.0
                                                               │
                                                     GitHub Actions publish.yml
                                                               │
                                                    Build  →  TestPyPI  →  PyPI
```

Work through these steps in order — each one is a prerequisite for the next.

---

## STEP 0 — Commit all pending changes

> **Why first:** The publish workflow builds from the source it checks out from GitHub. Everything must be committed and pushed before you tag.

**0.1** — Run all checks to make sure the codebase is clean:

```bash
just all
```

All four stages must pass: format → lint → typecheck → test. Fix any failures before continuing.

**0.2** — Check what's uncommitted:

```bash
git status
```

**0.3** — Stage and commit all pending changes (new files, modified files, deleted old root-level docs):

```bash
git add CONTRIBUTING.md CHANGELOG.md LICENSE RELEASE.md PUBLISH.md
git add .github/
git add planning/
git add MILESTONES.md README.md justfile pyproject.toml src/thothspinner/__init__.py uv.lock
git add -u   # stages deleted files (old M01.md–M15.md, prd_v1.md, etc.)
git commit -m "chore: prepare v1.0.0 release — metadata, CI/CD, docs, planning"
```

**0.4** — Push to `main`:

```bash
git push origin main
```

**0.5** — Confirm CI passes. Open this URL in your browser:

```
https://github.com/smorin/thothspinner/actions
```

Look for a workflow run called **"CI"** triggered by your push. It should show three jobs: **Test**, **Lint & Format**, **Type Check**. Wait for all three to show a green checkmark before proceeding. This typically takes 2–3 minutes.

---

## STEP 1 — Create GitHub Environments

> **Why:** The `publish.yml` workflow references `environment: testpypi` and `environment: pypi`. GitHub will refuse to run those jobs if the environments don't exist in the repository settings.

**1.1** — Open this URL in your browser:

```
https://github.com/smorin/thothspinner/settings/environments
```

You'll land on a page titled **"Environments"** with a green **"New environment"** button in the upper right.

**1.2** — Create the `testpypi` environment:

1. Click **"New environment"**
2. In the **"Name"** text field, type exactly: `testpypi` *(all lowercase, no spaces)*
3. Click **"Configure environment"**
4. Leave all settings at their defaults — do not add reviewers or branch restrictions
5. Click **"Save protection rules"**

You're taken back to the Environments list. You should now see `testpypi` in the list.

**1.3** — Create the `pypi` environment:

1. Click **"New environment"** again
2. In the **"Name"** text field, type exactly: `pypi` *(all lowercase, no spaces)*
3. Click **"Configure environment"**
4. **Recommended:** Under **"Required reviewers"**, click **"Add required reviewers"**, type your GitHub username (`smorin`), and select it from the dropdown. This adds a manual approval gate — the workflow will pause and ask you to click Approve before publishing to production PyPI.
5. Click **"Save protection rules"**

You should now see both `testpypi` and `pypi` in the Environments list.

---

## STEP 2 — Register Trusted Publisher on TestPyPI

> **Why:** TestPyPI needs to know that your GitHub Actions workflow is allowed to publish `thothspinner`. Without this, the publish step returns a 403 error.

**2.1** — Open your browser and go to:

```
https://test.pypi.org
```

**2.2** — Log in to your TestPyPI account.
- If you don't have a TestPyPI account, register at: `https://test.pypi.org/account/register/`
- TestPyPI is a separate service from PyPI — accounts are not shared.

**2.3** — After logging in, navigate to:

```
https://test.pypi.org/manage/account/publishing/
```

The page is titled **"Your publishing configuration"**. Scroll down until you see a section titled **"Add a new pending publisher"**.
*(This section is for projects that don't exist yet on TestPyPI — which is the case here.)*

**2.4** — Fill in the form with these exact values:

| Field | Value |
|-------|-------|
| PyPI Project Name | `thothspinner` |
| Owner | `smorin` |
| Repository name | `thothspinner` |
| Workflow name | `publish.yml` |
| Environment name | `testpypi` |

**2.5** — Click **"Add"**.

You should see `thothspinner` appear in your list of pending publishers on that page. If you see an error, double-check that every field matches the table above exactly (case-sensitive).

---

## STEP 3 — Register Trusted Publisher on PyPI

> **Why:** Same as Step 2, but for production PyPI.

**3.1** — Open your browser and go to:

```
https://pypi.org
```

**3.2** — Log in to your PyPI account at: `https://pypi.org/account/login/`
*(Your PyPI account is separate from TestPyPI.)*

**3.3** — After logging in, navigate to:

```
https://pypi.org/manage/account/publishing/
```

Scroll down to the **"Add a new pending publisher"** section.

**3.4** — Fill in the form with these exact values:

| Field | Value |
|-------|-------|
| PyPI Project Name | `thothspinner` |
| Owner | `smorin` |
| Repository name | `thothspinner` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

**3.5** — Click **"Add"**.

You should see `thothspinner` appear in your list of pending publishers. If you see an error, check for typos — every field is case-sensitive.

---

## STEP 4 — Tag and Trigger the Publish Workflow

> **Why:** Pushing a `v*` tag is what triggers `publish.yml`. The tag is also the permanent version marker in git history.

**4.1** — Make sure you're on `main` with a clean working tree:

```bash
git status
```

Expected output: `nothing to commit, working tree clean`

If there are uncommitted changes, commit them first (see Step 0).

**4.2** — Confirm your Step 0 commit is at the top of the log:

```bash
git log --oneline -3
```

**4.3** — Run the release command:

```bash
just release 1.0.0
```

This runs four commands in sequence:
1. `just clean` — deletes `dist/`, `.pytest_cache/`, `htmlcov/`, `__pycache__`
2. `uv build` — rebuilds fresh `dist/thothspinner-1.0.0-py3-none-any.whl` and `dist/thothspinner-1.0.0.tar.gz`
3. `git tag v1.0.0` — creates the tag locally
4. `git push origin v1.0.0` — pushes the tag to GitHub, which triggers `publish.yml`

You'll see output like:
```
Enumerating objects: 1, done.
...
To github.com:smorin/thothspinner.git
 * [new tag]         v1.0.0 -> v1.0.0
```

---

## STEP 5 — Monitor the Publish Workflow

> **Why:** You need to watch the workflow progress and, if you configured a required reviewer on the `pypi` environment, manually approve the production publish step.

**5.1** — Open:

```
https://github.com/smorin/thothspinner/actions
```

**5.2** — At the top of the list, look for a workflow run with a yellow spinner (in progress) titled **"Publish to PyPI"**. Click on it.

**5.3** — You'll see three jobs displayed left-to-right:

```
Build  →  Publish to TestPyPI  →  Publish to PyPI
```

Each job must succeed (green checkmark) before the next one starts.

- **Build** (~30 seconds): Runs `uv build` and uploads the dist artifacts.
- **Publish to TestPyPI** (~30 seconds): Downloads artifacts, publishes to `test.pypi.org`.
- **Publish to PyPI**: See Step 5.4 below.

**5.4** — If you configured a required reviewer on the `pypi` environment (recommended in Step 1.3):

When **Publish to TestPyPI** completes, the **Publish to PyPI** job will show an orange clock icon and a banner that says:

> **"Waiting for review"** — This deployment requires a review from the owner before continuing.

1. Click the orange **"Review deployments"** button
2. Check the checkbox next to **`pypi`**
3. Optionally add a comment
4. Click **"Approve and deploy"**

The job will then start running.

**5.5** — Wait for all three jobs to show green checkmarks. Total time is typically 2–4 minutes.

**5.6** — If any job fails, click on it to see the logs. Common failures:

| Error | Cause | Fix |
|-------|-------|-----|
| `403 Forbidden` | OIDC not configured or field mismatch | Re-check Steps 2–3; environment name and workflow filename must match exactly |
| `400 File already exists` | Version already uploaded | Not possible for a brand-new project |
| `Environment not found` | GitHub environment doesn't exist | Re-check Step 1 |
| Workflow didn't trigger | Tag doesn't match `v*` | Confirm tag is `v1.0.0` not `1.0.0` |

---

## STEP 6 — Verify the Installation

> **Why:** Confirms the package is live and installable by end users.

Wait ~2 minutes after the workflow completes for PyPI's CDN to propagate.

**6.1** — Confirm the package pages exist:

- TestPyPI: `https://test.pypi.org/project/thothspinner/`
- PyPI: `https://pypi.org/project/thothspinner/`

Both pages should load and show version `1.0.0`.

**6.2** — Test a clean install using `uvx` (creates a temporary isolated environment automatically):

```bash
uvx --from thothspinner python -c "import thothspinner; print(thothspinner.__version__)"
```

Expected output: `1.0.0`

**6.3** — Or test with pip in a fresh virtual environment:

```bash
python3 -m venv /tmp/test-thothspinner
source /tmp/test-thothspinner/bin/activate
pip install thothspinner
python -c "from thothspinner import ThothSpinner; print('OK')"
deactivate
rm -rf /tmp/test-thothspinner
```

Expected output: `OK`

---

## STEP 7 — Verify Documentation Links

> **Why:** All URLs in `pyproject.toml` are displayed on the PyPI project page. Broken links are visible to every user.

Open each URL in your browser and confirm it loads:

| URL | What to check |
|-----|---------------|
| `https://github.com/smorin/thothspinner` | Repository homepage loads |
| `https://github.com/smorin/thothspinner/blob/main/docs/thothspinner_rich.md` | Rich API docs load |
| `https://github.com/smorin/thothspinner/blob/main/CHANGELOG.md` | Changelog loads; v1.0.0 is at the top |
| `https://github.com/smorin/thothspinner/issues` | Issues page loads |

> **Note:** If the repository is private, all of these links will return 404 for non-members. Make it public first:
> GitHub repo → **Settings** → scroll to the bottom → **"Danger Zone"** → **"Change repository visibility"** → **"Make public"**

---

## STEP 8 — Create GitHub Release and Announce

**8.1** — Go to:

```
https://github.com/smorin/thothspinner/releases/new
```

**8.2** — Fill in the form:

1. Click the **"Choose a tag"** dropdown → select **`v1.0.0`** (it already exists from Step 4)
2. In the **"Release title"** field, type: `v1.0.0`
3. In the **"Describe this release"** text area, paste the `## [1.0.0]` section from `CHANGELOG.md`
4. Leave **"Set as the latest release"** checked

**8.3** — Click **"Publish release"**.

**8.4** — Optional: Post an announcement in GitHub Discussions:

1. Go to: `https://github.com/smorin/thothspinner/discussions`
2. Click **"New discussion"** → select category: **"Announcements"**
3. Title: `thothspinner v1.0.0 — now on PyPI`
4. Body: link to the release, one-paragraph summary of what the library does, install command:
   ```
   pip install thothspinner
   ```

---

## STEP 9 — Mark M14 Complete

Update the planning docs to reflect everything is done:

**9.1** — In `planning/M14.md`, mark all remaining tasks as `[x]`:
- M14-T12, M14-T15, M14-T16, M14-T17, M14-T18
- M14-TS02, M14-TS04, M14-TS05, M14-TS06

**9.2** — In `MILESTONES.md`, change:

```
## [-] Milestone M14: Publishing to PyPI (v1.0.0)
```
to:
```
## [x] Milestone M14: Publishing to PyPI (v1.0.0)
```

**9.3** — Commit and push:

```bash
git add planning/M14.md MILESTONES.md
git commit -m "chore: mark M14 complete — thothspinner published to PyPI"
git push origin main
```

---

## Quick Reference — Exact Values

These values must match exactly everywhere they appear (PyPI, TestPyPI, GitHub):

| Setting | Value |
|---------|-------|
| Package name | `thothspinner` |
| GitHub owner | `smorin` |
| GitHub repo | `thothspinner` |
| Workflow filename | `publish.yml` |
| TestPyPI environment | `testpypi` |
| PyPI environment | `pypi` |
| Release tag format | `v1.0.0` |
