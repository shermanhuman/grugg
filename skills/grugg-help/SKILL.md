---
name: grugg-help
description: >
  Quick-reference card for all grugg modes, skills, and commands.
  One-shot display, not a persistent mode. Trigger: /grugg-help,
  "grugg help", "what grugg commands", "how do I use grugg".
---

# Grugg Help

Display this reference card when invoked. One-shot — do NOT change mode, write flag files, or persist anything. Output in grugg style.

## Modes

| Mode | Trigger | What change |
|------|---------|-------------|
| **Lite** | `/grugg lite` | Drop filler. Keep sentence structure. |
| **Full** | `/grugg` | Drop articles and filler; preserve uncertainty. Fragments OK. Default. |
| **Ultra** | `/grugg ultra` | Extreme compression. Bare fragments. Tables over prose. |
| **Wenyan-Lite** | `/grugg wenyan-lite` | Classical Chinese style, light compression. |
| **Wenyan-Full** | `/grugg wenyan` | Full 文言文. Maximum classical terseness. |
| **Wenyan-Ultra** | `/grugg wenyan-ultra` | Extreme. Ancient scholar on a budget. |

Mode stick until changed or session end.

## Skills

| Skill | Trigger | What it do |
|-------|---------|-----------:|
| **grugg-commit** | `/grugg-commit` | Terse commit messages. Conventional Commits. ≤50 char subject. |
| **grugg-review** | `/grugg-review` | One-line PR comments: `L42: bug: user null. Add guard.` |
| **grugg-compress** | `/grugg-compress <file>` | Compress .md files to grugg prose. Savings vary; structural validation is not a semantic guarantee. |
| **grugg-help** | `/grugg-help` | This card. |

## Deactivate

Say "stop grugg" or "normal mode". Resume anytime with `/grugg`.

## Configuration

No runtime hook reads `GRUGG_DEFAULT_MODE` or a Grugg config file in this herd. Choose the session mode in your request. To change a project's startup style, explicitly override `rules/grugg-activate.md` through Promptherder settings and sync. "Normal mode" remains effective for the current session.

Native invocation uses `/grugg` in Claude and `$grugg` in Codex; apply the same prefix to other skill IDs. `grugg-compress` is the portable skill name, not a `grugg:compress` namespace alias.

## More

Based on [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee.
