# skills

Agent Skills I built for my own daily work with Claude Code. Each one is a folder with a `SKILL.md` and its own README.

| Skill | What it does |
|---|---|
| [think-it-through](think-it-through) | Interviews you about an idea, plan or decision, one question at a time, until you and the agent share one understanding of it. |
| [close-the-gap](close-the-gap) ![experimental](https://img.shields.io/badge/status-experimental-orange) | Finds the most worthwhile gap between how you work with AI and the frontier, then teaches you across it, from the frontier back to your work. |
| [house-style](house-style) | Keeps a model's default habits out of what it writes and builds for you, in text, in rendered pages and in how it puts decisions to you. |
| [earn-its-place](earn-its-place) | Tests whether a skill still earns its place: switches it off for a window of real work, then rebuilds only what was missing or retires it. |

## Install

```bash
npx skills add byMarcoVogt/skills
```

This needs Node.js 22.20 or newer. [`skills`](https://github.com/vercel-labs/skills) lets you pick which skills to install and for which agents. Add `--skill <name>` to install one directly. Each skill's README also explains how to copy the folder by hand.

## License

[MIT](LICENSE)
