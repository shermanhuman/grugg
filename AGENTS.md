# grugg

A Claude Code and Codex plugin: skills in `skills/` (all manual-only), the compression tool in `skills/compress/scripts/`, offline tests in `tests/`, benchmarks in `benchmarks/`.

- **Merging is a human task.** Never merge a branch, squash-merge a PR, or push to the default branch. Create branches, push feature branches and open PRs; when work is ready, ask the user to merge.
- Every PR bumps `version` in `.claude-plugin/plugin.json` (CI checks it). Without a bump, installed copies never update.
- Before a PR: `python3 -m unittest discover -s tests`, the benchmark dry run in `.github/workflows/compression-tests.yml`, and `claude plugin validate .`.
- Every skill stays manual-only: `disable-model-invocation: true` in its `SKILL.md` for Claude Code and `agents/openai.yaml` with `allow_implicit_invocation: false` for Codex.
