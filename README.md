# Grugg

A [promptherder](https://github.com/shermanhuman/promptherder) herd for ultra-compressed AI agent communication.

Grugg makes your AI coding agent respond in compressed, terse prose — aiming to reduce unnecessary output while retaining technical detail. Savings and quality depend on the model and task. Six intensity levels from professional-lite to classical Chinese.

## Install

```bash
# Install promptherder
go install github.com/shermanhuman/promptherder/cmd/promptherder@latest

# Select targets explicitly with Promptherder 1.x
promptherder install codex claude

# Pull this herd
promptherder pull https://github.com/shermanhuman/grugg

# Sync to agent targets
promptherder
```

## What's Included

### Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| `grugg` | `/grugg` | Core terse mode — lite, full, ultra, wenyan variants |
| `grugg-commit` | `/grugg-commit` | Terse commit messages. Conventional Commits. ≤50 char subject. |
| `grugg-review` | `/grugg-review` | One-line PR comments: `L42: bug: user null. Add guard.` |
| `grugg-help` | `/grugg-help` | Quick-reference card for all modes and skills |
| `grugg-compress` | `/grugg-compress <file>` | Compress .md files to terse prose. Validates a candidate and saves a backup before replacement. |

### Rules

| Rule | Description |
|------|-------------|
| `grugg-activate` | Always-on activation — grugg mode from first message |

## Intensity Levels

| Level | What it does |
|-------|-------------|
| **Lite** | Drop filler, keep grammar. Professional but no fluff. |
| **Full** | Drop articles, fragments OK, short synonyms. Default. |
| **Ultra** | Maximum compression. Telegraphic. Abbreviate everything. |
| **Wenyan-Lite** | Semi-classical Chinese. Grammar intact, filler gone. |
| **Wenyan-Full** | Full 文言文. Maximum classical terseness. |
| **Wenyan-Ultra** | Extreme. Ancient scholar on a budget. |

## Structure

```
grugg/
├── herd.json
├── skills/
│   ├── grugg/
│   │   └── SKILL.md
│   ├── grugg-commit/
│   │   └── SKILL.md
│   ├── grugg-review/
│   │   └── SKILL.md
│   ├── grugg-help/
│   │   └── SKILL.md
│   └── grugg-compress/
│       ├── SKILL.md
│       └── scripts/
└── rules/
    └── grugg-activate.md
```

## How it fits with Compound V

`grugg` is a companion herd to [compound-v](https://github.com/shermanhuman/compound-v). Compound V provides the methodology (planning, execution, review). Grugg provides the communication style — terse, efficient, no fluff.

```
compound-v  →  methodology (how to work)
oh          →  environment (what you work with)
grugg       →  communication (how to talk)
stack.md    →  project (what you're building)
```

Pull all three into any repo:

```bash
promptherder pull https://github.com/shermanhuman/compound-v
promptherder pull https://github.com/shermanhuman/oh
promptherder pull https://github.com/shermanhuman/grugg
promptherder
```

## Credits

Grugg is a maintained fork of **[caveman](https://github.com/JuliusBrussee/caveman)** by **[Julius Brussee](https://github.com/JuliusBrussee)**. The original project explored terse LLM communication; savings and retained meaning need evaluation for each model and task. Grugg carries that torch forward as a promptherder herd.

- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — the original project

## License

MIT License — Copyright (c) 2025 Julius Brussee

## 2.0.0 behavior and migration

Use native `/grugg` in Claude Code or `$grugg` in Codex (and the same prefix for other skill IDs). Older colon-style aliases are not installed by Promptherder 1.x. Explicit session style changes override the startup baseline; normal mode stays normal until changed again. There is no runtime reader for `GRUGG_DEFAULT_MODE` or a Grugg config file.

Grugg changes commentary, not required review evidence or artifact schemas. Plans and reviews retain Compound V’s required structure and may use terse prose. Code, commits, and PRs remain normal unless a dedicated formatter is requested. Grugg review/commit skills are formatting helpers and do not prevent their caller from completing already-authorized work.

Compression defaults to a candidate written and reviewed by the current agent. The CLI now requires `--candidate <path>` or explicit `--provider claude`; it never chooses a paid provider from credentials alone. Backups include the source's full filename, for example `notes.md.original.md`. Existing backups are preserved. Structural validation does not prove semantic equivalence.

Run `python3 -m unittest discover -s tests` for offline regressions. Benchmarks require explicit provider/model choices and measure token output, not instruction adherence. No fresh paid-model benchmark is claimed for this release. Existing Promptherder locks need a reviewed `--update-lock` sync.
