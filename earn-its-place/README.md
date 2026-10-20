# Earn its place

```mermaid
flowchart LR
  I(Write down what it is for) --> B(Switch it off) --> W(Work as usual) --> A(Look back)
  A -->|something was missing| R(Rebuild only that)
  A -->|nothing was missing| X(Retire)
```

- Tests whether a skill, or a set of skills, still earns its place. A skill does only if work goes worse without it, so the test is a window of real work, not a reading of the skill.
- Before the window, it works out with you what the skill is for and writes that into `intent.md`.
- Afterwards, it judges the sessions the skill would have touched against `intent.md`, and looks just as hard for needs nobody wrote down.
- Too few relevant sessions mean the window was too short or the skill is no longer needed. It says which it thinks.

## Install

earn-its-place uses [think-it-through](../think-it-through) from this repo to find out what your skills are for, so install both.

```bash
npx skills add byMarcoVogt/skills --skill earn-its-place --skill think-it-through -g
```

This needs Node.js 22.20 or newer. Or copy both folders yourself:

| Agent | Put the folders in |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| Other agents that read `SKILL.md` | that agent's skills folder |

Then ask in plain words, for example "does my review skill still pay off?". It proposes the window, keeps copies of the sessions and schedules its own return on your machine. A scheduler that runs remotely can't read your transcripts.

## License

[MIT](LICENSE)
