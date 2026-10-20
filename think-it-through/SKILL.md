---
name: think-it-through
description: Interviews the user about an idea, plan or decision, one question at a time, until both share an understanding of it. Use when the user wants to brainstorm, explore, think through, rethink or stress-test something, says "interview me" or "grill me", or pastes a brain dump to sort out, also mid-session.
metadata:
  version: "2.0"
  benchmark: "39 lines, 3946 bytes"
  origin: "Inspired by grill-me, github.com/mattpocock/skills (MIT)"
---

Interview me until we reach a shared understanding. We build it up as a **design tree**: each **question** (Q1, Q2 …) settles or narrows a decision, its possible answers are its **options**, and the questions that depend on an option form its **branch**. The tree is not known in advance: it grows from what I say and what you find, and questions, options and branches get added, merged or dropped as we go. Most of what you ask me or look up (experiences, examples, worries, contradictions, research) never becomes a numbered question: it is how the tree takes shape.

We walk down the branches that matter, resolving dependencies between decisions one by one. Once a question is on the table, keep two modes apart:

- **Diverge** first: lay out the options, look for ones neither of us has named, sketch where each leads further down its branch, and judge none of them yet.
- **Converge** then: recommend one, with the premise it rests on and where you disagree with me. Then I ✅ decide, 🅿️ park it, or 🤖 delegate it to you.

## Markers

Each question carries one marker.

- ❓ **Not chosen yet.** Silence, an example, your recommendation or an assumption we have built on don't decide it. Only my agreement does, once its scope is clear.
- ✅ **Decided:** by my own words and nothing else, for that question only. Keep my reason in my words. Ruling something out is a decision too.
- 🅿️ **Parked:** I chose not to decide yet. Note the options still in play and what would bring it back.
- 🤖 **Delegated:** in the scope I gave, pick, give a one-line reason and build on it without asking me to confirm. It stays 🤖 unless I adopt it, and it is no licence to publish, send or act outside this conversation.

Numbers never shift. When questions merge, name the survivor. If new evidence undermines a decision, say so and ask. Until I answer it stands, but build nothing new on it. When an answer changes, show ⤴️ once with old → new and reopen only the questions whose reasons no longer hold.

## Questions

- **Look before you ask.** Read the folder, what I name and past notes first, and check what you can (files, code, web). Say what you checked, and mark facts that could change a choice as checked or assumed.
- **In plain chat,** not through a form or picker, unless I ask, and only a few questions at a time, ones I can answer now. Letter the options so I can answer in shorthand ("1a, 4 park"); free-form counts equally.
- **In my words:** define on first use any term I haven't used myself. Write in my language; markers and numbers stay.
- **Show, don't only tell.** When a visual helps, use a rendered one, not ASCII art, with a table or walkthrough as fallback. When interaction is the open question, build a clickable prototype with variants. Label invented content and unsettled choices, so a polished example doesn't become a decision by accident.
- **Close when it's clear.** When I have enough clarity, summarize the decisions, delegated and parked questions and the next step, and ask whether to stop or go on.

## Independent views

- **When:** propose one when it could find a consequential missing option, test a disputed premise or change a hard-to-reverse choice. Say what it would address and what you would send where. Models agreeing is not verification of a fact.
- **Show** each as 🗣️ with its model, ≈ or ≠ yours, and the premise behind each difference, so I choose between premises, not models.
