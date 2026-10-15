# Grugg

Terse communication mode for Claude Code and Codex, packaged as a plugin.

Grugg makes your coding agent answer in compressed, terse prose: no filler, no pleasantries, technical detail intact. Savings and quality depend on the model and task. Six intensity levels, from professional-lite to classical Chinese. It's **opt-in**: nothing changes until you invoke it.

## Install

Claude Code:

```text
/plugin marketplace add shermanhuman/compound-v
/plugin install grugg@compound-v
```

Codex:

```bash
codex plugin marketplace add shermanhuman/compound-v
codex plugin add grugg@compound-v
```

Grugg is listed in the [Compound V](https://github.com/shermanhuman/compound-v) marketplace. Installed copies update when the plugin's version changes: in Claude Code turn on auto-update for the marketplace in `/plugin` or run `claude plugin update grugg@compound-v`; in Codex run `codex plugin marketplace upgrade compound-v`.

## Skills

All skills are manual-only: they run when you invoke them (`/grugg:<skill>` in Claude Code, `$grugg:<skill>` in Codex), never on their own.

| Skill | Invoke | What it does |
|-------|--------|--------------|
| `grugg` | `/grugg:grugg [level]` | Turn terse mode on, or change level; "stop grugg" or "normal mode" turns it off |
| `commit` | `/grugg:commit` | Terse commit messages. Conventional Commits. ≤50 char subject |
| `review` | `/grugg:review` | One-line review comments: `L42: bug: user null. Add guard.` |
| `compress` | `/grugg:compress <file>` | Shorten a prose file; validates a candidate and keeps a backup before replacing it |
| `help` | `/grugg:help` | Quick-reference card |

## Intensity levels

| Level | What it does |
|-------|-------------|
| **Lite** | Drop filler, keep grammar. Professional but no fluff. |
| **Full** | Drop articles, fragments OK, short synonyms. Default. |
| **Ultra** | Maximum compression. Telegraphic. Abbreviate everything. |
| **Wenyan-Lite** | Semi-classical Chinese. Grammar intact, filler gone. |
| **Wenyan-Full** | Full 文言文. Maximum classical terseness. |
| **Wenyan-Ultra** | Extreme. Ancient scholar on a budget. |

## Boundaries

Grugg changes commentary, not required structure. Plans and reviews keep their required sections, finding IDs and evidence (for example [Compound V](https://github.com/shermanhuman/compound-v)'s) and may use terse prose inside them. Code, commits and PRs stay normal unless you invoke a Grugg formatter. Security warnings, irreversible actions and confusing multi-step instructions temporarily switch back to normal prose.

## Compression

`compress` defaults to a candidate written and reviewed by the current agent. The CLI requires `--candidate <path>` or an explicit `--provider claude`; it never picks a paid provider from credentials alone. Backups keep the source's full filename (`notes.md.original.md`) and existing backups are never overwritten. Structural validation does not prove semantic equivalence.

Run `python3 -m unittest discover -s tests` for offline regressions. Benchmarks need an explicit provider and model and measure token output, not instruction adherence.

## Upgrading from 2.x

2.x was a [Promptherder](https://github.com/shermanhuman/promptherder) herd with an always-on activation rule and skills named `grugg-commit`, `grugg-review`, `grugg-help` and `grugg-compress`. 3.0 has no always-on rule, and the plugin namespace replaces the prefix: `/grugg:commit` and so on.

Deleting the herd alone leaves what Promptherder generated from it, including the activation text in `AGENTS.md`, so grugg would keep switching on. In each repository that pulled it:

1. Remove the herd: `rm -rf .promptherder/herds/grugg`.
2. Re-sync so Promptherder deletes the output it generated from the herd (its manifest tracks every file): `promptherder --update-lock`. If you've stopped using Promptherder, delete the generated `AGENTS.md`/`CLAUDE.md` sections and the `grugg*` folders under `.claude/skills/` and `.agents/skills/` by hand, keeping any hand-written instructions.
3. Check nothing is left: `grep -rl "smart grugg" AGENTS.md CLAUDE.md .claude .agents 2>/dev/null` prints nothing.
4. Install the plugin as above and start a fresh session.

## Credits

Grugg is a maintained fork of **[caveman](https://github.com/JuliusBrussee/caveman)** by **[Julius Brussee](https://github.com/JuliusBrussee)**. The original project explored terse LLM communication; savings and retained meaning need evaluation for each model and task.

## License

MIT License — Copyright (c) 2025 Julius Brussee
