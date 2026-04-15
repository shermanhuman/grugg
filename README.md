# Grugg

A [promptherder](https://github.com/shermanhuman/promptherder) herd for ultra-compressed AI agent communication.

Grugg makes your AI coding agent respond in compressed, terse prose — cutting **~75% of output tokens** while keeping full technical accuracy. Six intensity levels from professional-lite to classical Chinese.

## Install

```bash
# Install promptherder
go install github.com/shermanhuman/promptherder/cmd/promptherder@latest

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
| `grugg-compress` | `/grugg:compress <file>` | Compress .md files to terse prose. Saves ~46% input tokens. |

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

Grugg is a maintained fork of **[caveman](https://github.com/JuliusBrussee/caveman)** by **[Julius Brussee](https://github.com/JuliusBrussee)**. The original project pioneered the idea that caveman-speak dramatically reduces LLM token usage without losing technical substance. Grugg carries that torch forward as a promptherder herd.

- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — the original project

## License

MIT License — Copyright (c) 2025 Julius Brussee
