# Earn its place

```mermaid
flowchart LR
  I(Write down what it is for) --> B(Switch it off) --> W(Work as usual) --> A(Look back)
  A -->|something was missing| R(Rebuild only that)
  A -->|nothing was missing| X(Retire)
```

- Tests whether a skill, or a set of skills, still earns its place. A skill does only if work goes worse without it, so the test is a window of real work, not a reading of the skill.
- Before the window, it uses [think-it-through](../think-it-through) from this repo to work out with you what the skill is for, and writes that into `intent.md`. The install below adds both.
- Afterwards, it judges the sessions the skill would have touched against `intent.md`, and looks just as hard for needs nobody wrote down.
- Too few relevant sessions mean the window was too short or the skill is no longer needed. It says which it thinks.

## How to use it

**Agent invoked**<br>
Your agent picks it up when you ask whether a skill still pays off, and when a trial's window is up and the scheduled session comes back.

**You invoke it**<br>
`/earn-its-place` in Claude Code, `$earn-its-place` in Codex.

## Install

```bash
npx skills add byMarcoVogt/skills --skill earn-its-place --skill think-it-through -g
```

Or copy manually:

| Agent | Put the folders in |
|:---:|:---:|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| Other agents that read `SKILL.md` | that agent's skills folder |

## License

[MIT](LICENSE)
