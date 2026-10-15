---
name: help
description: >
  Quick-reference card for all grugg modes, skills, and commands.
  One-shot display, not a persistent mode.
disable-model-invocation: true
---

# Grugg Help

Display this reference card when invoked. One-shot — do NOT change mode, write flag files, or persist anything. Output in grugg style.

Claude Code invokes skills as `/grugg:<skill>`, Codex as `$grugg:<skill>`. The examples below use Claude's form.

## Modes

| Mode | Trigger | What change |
|------|---------|-------------|
| **Lite** | `/grugg:grugg lite` | Drop filler. Keep sentence structure. |
| **Full** | `/grugg:grugg` | Drop articles and filler; preserve uncertainty. Fragments OK. Default. |
| **Ultra** | `/grugg:grugg ultra` | Extreme compression. Bare fragments. Prefer tables while preserving required artifact formats. |
| **Wenyan-Lite** | `/grugg:grugg wenyan-lite` | Classical Chinese style, light compression. |
| **Wenyan-Full** | `/grugg:grugg wenyan` | Full 文言文. Maximum classical terseness. |
| **Wenyan-Ultra** | `/grugg:grugg wenyan-ultra` | Extreme. Ancient scholar on a budget. |

Grugg is off until invoked. Mode stick until changed or session end.

## Skills

| Skill | Trigger | What it do |
|-------|---------|-----------:|
| **commit** | `/grugg:commit` | Terse commit messages. Conventional Commits. ≤50 char subject. |
| **review** | `/grugg:review` | One-line PR comments: `L42: bug: user null. Add guard.` |
| **compress** | `/grugg:compress <file>` | Compress .md files to grugg prose. Savings vary; structural validation is not a semantic guarantee. |
| **help** | `/grugg:help` | This card. |

## Deactivate

Say "stop grugg" or "normal mode". Resume anytime with `/grugg:grugg`.

## More

Based on [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee.
