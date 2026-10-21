# House style

<p align="center">Holds the agent to your style in how it writes, designs and communicates.<br>
Built from 1,087 of one person's corrections, choices and approvals since August 2026.</p>

## What it catches

| The model did | The author said | In the skill |
|---|---|---|
| Put a coloured bar on the left of every card | "This is AI stylish, and I don't want it anywhere." | Hard rule: no bar on one side of a box |
| Listed decisions as S20, T3 and "the gate" | "wdym?" | Hard rule: no code in chat without its meaning |
| Joined fields with middle dots | "seperators 'vertical line' > 'point'" | Hard rule: " \| " instead of "·" |

## How it works

`SKILL.md` holds the principles and hard rules. For each task the agent reads one reference: [writing](references/writing.md), [visual](references/visual.md) or [conversation](references/conversation.md). The rules are plain tables, so you can change, delete or add your own. Some conversation rules assume Claude Code features. In other agents, read them as intent.

## Install

```bash
npx skills add byMarcoVogt/skills --skill house-style -g
```

Or copy manually:

| Agent | Put the folder in |
|:---:|:---:|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| Other agents that read `SKILL.md` | that agent's skills folder |

## License

MIT. Inspired by [unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) in pstack by Lauren Tan (MIT).
