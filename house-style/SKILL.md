---
name: house-style
description: Keeps the model's default habits out of what it writes and builds for the user, in German and English, in text, in rendered output (pages, artifacts, decks, docs, diagrams, UI) and in how answers and decisions are put to the user. Use whenever drafting or revising text, building something visual, or answering with options, findings or explanations, and when the user says house style, slop, "klingt nach KI", "sieht billig aus", "prüf den Text" or asks for a check of a text or page.
metadata:
  version: "0.1"
  benchmark: "51 lines, 4049 bytes"
  origin: "Fork of unslop from pstack, github.com/cursor/plugins (MIT)"
---

# house-style

Frontier models write and design well. What goes wrong are a few defaults that recur in every project: a dash in mid-sentence, a coloured bar on one side of a box, a code the user has to ask about, everything at once. This skill names those defaults so they stay out. It is not a writing lesson: where a check does not apply, write as you would.

Some patterns are wanted in named cases. Those are rations: allowed only in the listed case and form, everywhere else they fail the check. Hard rules hold in every context. Everything else is a principle: a judgment you apply to each element. An explicit request from the user overrides a check.

## How to use it

1. Before writing or building, read the reference for the medium:
   - text in any medium: [writing.md](writing.md)
   - anything rendered (page, artifact, deck, doc layout, diagram, chart, UI): [visual.md](visual.md)
   - answers, options, findings, reviews in chat: [conversation.md](conversation.md)
2. Write or build.
3. Check the output against the hard rules below and the checklist of each reference you read. Fix the passage, not just the flagged word, then check the fixed sentences again: a removed dash often comes back as a colon.
4. Stop when the checks pass. Do not produce another variant because one is possible, and do not report the check unless the user asks.

Text the user has approved stays as it is. If a check would change it, say so instead of changing it.

When the user asks for a check of a given text or page, return each finding as: quoted passage, the check it fails, the fix.

## Principles

1. **Every element earns its name and its position.** A sentence, label, line, box or control stays only if it carries something nothing else on the page carries.
2. **Say the concrete thing.** A sentence says what happens, who does it, with the number. If it could stand unchanged in another project, or names a feeling instead of a mechanism, it says nothing.
3. **The reader understands every name without asking.** Codes, coined labels, internal names and abbreviations get their meaning on first use, or a plainer word. A label says exactly what the thing is.
4. **As firm as the evidence and the decision, no firmer, no weaker.** Hedge only what cannot be known yet, once. State what is settled plainly.
5. **One term per thing.** Once the user has fixed or replaced a term, it is used everywhere and the old one does not return.
6. **Form follows content and importance.** Structure shows hierarchy, emphasis sits only where the point is, and parallel elements share one form.
7. **The user's material is the yardstick.** Calibrate on the user's own texts and named reference looks, never on earlier model output.

## Hard rules

Check that the output has:

- no dash as a sentence device (– or —) in German or English. Hyphens in compounds, ranges ("2019–2023") and titles quoted verbatim stay.
- no semicolon joining two clauses.
- no middle dot "·" as a separator. Items on one line are separated by " | ", or set as label and value.
- no working notes, self-checks, takeaways or helper lines inside a deliverable (the text, page or slide that goes out).
- no code, coined term or abbreviation in chat without its meaning on first use.
- no renaming of anything the user named (sessions, files, terms) without asking.

Each reference adds the hard rules of its medium.
