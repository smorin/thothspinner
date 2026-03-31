## [x] Project P01: Developer Experience Improvements (v1.1.0)
**Goal**: Reduce maintenance friction and improve contributor onboarding by adding missing tooling across the board.

**In Scope**
- Fix `snapshot_report.html` not being gitignored
- Add `just update-snapshots` for pytest-textual-snapshot regeneration
- Add `just bump-patch`, `just bump-minor`, `just bump-major` for manual version bumping
- Add `just changelog` via git-cliff for automated CHANGELOG.md generation from Conventional Commits
- Add `just security` via bandit for security linting
- Add `bandit` to lefthook pre-commit checks
- Add Dependabot for automated dependency + GitHub Actions version PRs
- Add GitHub PR template and Issue templates (bug, feature)
- Add `.devcontainer/devcontainer.json` for zero-setup Codespaces onboarding

**Out of Scope**
- Fully automated (non-manual) version bumping
- MkDocs / API doc generation
- Performance benchmarking

### Tests & Tasks
- [x] [P01-T01] Fix .gitignore — add `snapshot_report.html`
- [x] [P01-T02] Update justfile — add bump-patch/minor/major, changelog, update-snapshots, security, current-version; update release and all
- [x] [P01-T03] Create cliff.toml — git-cliff Conventional Commits config
- [x] [P01-T04] Update lefthook.yml — add bandit pre-commit step
- [x] [P01-T05] Create .github/dependabot.yml
- [x] [P01-T06] Create .github/PULL_REQUEST_TEMPLATE.md
- [x] [P01-T07] Create .github/ISSUE_TEMPLATE/bug_report.md
- [x] [P01-T08] Create .github/ISSUE_TEMPLATE/feature_request.md
- [x] [P01-T09] Create .devcontainer/devcontainer.json

### Deliverable
```bash
$ just bump-minor
Bumped minor: 1.0.0 → 1.1.0
$ just changelog
# regenerates CHANGELOG.md from git history
$ just security
# runs bandit against src/
$ just update-snapshots
# regenerates Textual snapshots
```

### Automated Verification
- `git status` no longer shows `snapshot_report.html`
- `just bump-patch` / `bump-minor` / `bump-major` each update `pyproject.toml` correctly
- `just changelog` produces a valid `CHANGELOG.md`
- `just all` includes security step and passes

### Regression Test Status
- [ ] All existing tests still pass after changes

---
