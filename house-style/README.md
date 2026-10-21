# House style

<h4 align="center">What does it do?</h4>

<p align="center">It holds the agent to your style in how it writes, designs and communicates.<br>
No dash in mid-sentence, no coloured bar beside every box,<br>
no code you have to ask about, no wall of options at once.</p>

<h4 align="center">Does it teach the model to write?</h4>

<p align="center">No. Frontier models write well. What goes wrong are a few defaults<br>
that come back in every project. This skill names them so they stay out.</p>

<h4 align="center">Where do the rules come from?</h4>

<p align="center">From one person's feedback, not from a list of AI words.<br>
1,087 corrections, choices and approvals since August 2026, from daily work<br>
in German and English, grouped and checked against each other.</p>

## What it catches

*Real cases from that feedback. The author's words are quoted as written.*

| The model did | The author said | In the skill |
|---|---|---|
| Put a coloured bar on the left of every card | "This is AI stylish, and I don't want it anywhere." | Hard rule: no bar on one side of a box |
| Listed decisions as S20, T3 and "the gate" | "wdym?" | Hard rule: no code in chat without its meaning |
| Opened a customer mail with "Leider gibt es eine Änderung. …" | "Get to the point." Chosen: "Ihre Lieferung kommt leider eine Woche später." | Ration: an announcement only when it names a category |
| Joined fields with middle dots | "seperators 'vertical line' > 'point'" | Hard rule: " \| " instead of "·" |
| Put a label above every slide title | Liked it once, on a consulting page with footer and page number. Elsewhere: "über den Titel sollte nichts Neues stehen" | Ration: one label, only where it says what the title does not |

Some patterns are banned outright. Most are allowed in named cases only, because that is how the author decided: rationing more often than banning.

## How it works

The skill has four files. `SKILL.md` holds seven principles and the hard rules for every medium. Three references hold the rest, and the agent reads the one for what it is making:

| File | For |
|:---:|:---:|
| `references/writing.md` | Text in any medium, German and English |
| `references/visual.md` | Pages, artifacts, slides, doc layout, diagrams, charts, UI |
| `references/conversation.md` | Answers with options, findings, reviews and decisions |

Each reference has rations (pattern, when it is allowed, in what form) and a checklist, and the visual and conversation references add hard rules of their own. The agent writes first, then checks its output against the list, fixes the passage and stops when the checks pass.

## Make it yours

The rules are one person's house style. They sit in plain tables and lists, so you can change a case, delete a row or add your own. Keep the shape of a ration: the pattern, when it is allowed, the form it takes.

## Built for Claude Code

house-style is written for Claude Code. The rules for text and pages work in any agent. Some rules in `references/conversation.md` assume Claude Code features, such as its question panel (`AskUserQuestion`) and commentable artifacts. In another agent, read those rules as intent, or delete them.

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

MIT. Inspired by [unslop](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md) in pstack by Lauren Tan (MIT). Informed by Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) and [Anzeichen für KI-generierte Inhalte](https://de.wikipedia.org/wiki/Wikipedia:Anzeichen_f%C3%BCr_KI-generierte_Inhalte). No text from either page is copied.
