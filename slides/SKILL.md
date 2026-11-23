---
name: slides
description: Builds a presentation as a deck in Claude Slides, in the user's design system, and measures every changed slide before the user sees it. Optionally sketches the storyline first as ghost decks. Use when the user wants slides, a deck or a presentation built or revised, or a ghost deck or storyline for one.
argument-hint: "[topic or brief]"
metadata:
  version: "1.0.0"
  benchmark: "3968 bytes"
---

# Slides

## Preferred design system

<!-- The one place to name your design system. Leave the line after the colon empty to be asked each time. -->
Preferred design system: Marco Vogt Slides

Named: build in it without asking. If no Design System artifact by that name exists yet, offer once to create it from this skill's `design-system/` folder (the Design System type), then build in it. Empty: list the Design System artifacts and ask in a panel which one to use, with "My own look" as the last option.

## 1. Just build it, or choose

Ask **"Just build it, or do you want to choose?"** unless the user's words already say it.

- **Just build it:** no further panel. Where a slide's form is open, build it as variants in place (3a, 3b) and name what you chose in the reply.
- **Let me choose:** one panel with two questions: storyline first or straight to slides, and which decision the deck should drive (options from the brief). Nothing else is asked up front.

## 2. Storyline (only when chosen)

Follow `storyline/STORYLINE.md`, publish the ghost decks, and build the deck the user picks.

## 3. Build

- Before you choose a slide's form, settle what the slide must prove, and look for data that turns a list of points into a chart or into slides of their own. When the user criticises a slide as a whole, go back to its content and research again; do not restyle the same information.
- Keep a list of what the brief requires. After every change, compare the deck with it. When a comment removes a required item, say so and ask where it should go.
- Variants: never reuse a letter. Apply each correction to every visible variant, and carry it over before parking one; parked variants are hidden and moved to the back. A request that leaves the form open ("standardise", "rethink") becomes a new variant instead of overwriting the only one.
- A thin slide gets more real content, or is merged with another or dropped.
- Resolve a comment thread only in a way that keeps it readable, and ask first.

## 4. Check before every show

The user's standing request, overriding the Slides type's rule against verifying: no version of the deck is published or shown before it has been checked.

1. Read the design system's `project/tokens.json` with the Artifact tool into a local folder, once per session. For Marco Vogt Slides, `design-system/tokens.json` in this folder is the same file.
2. Write all of the deck's files locally before the first send. The Slides type sends the index, stylesheet and cover first, and that send already opens the deck: hold it until the whole deck passes. Then run
   `python -I "<this skill's folder>/scripts/check.py" --tokens <tokens.json> <folder holding project/> --shots <folder> --report <report.json>`
3. Fix every error it names and run it again until all slides pass. Then look at the PNGs of the changed slides for what no script measures: form, fill and balance, the argument. Anything you change after that look is checked again.
4. Publish. In the reply, give the check's last line for exactly that version ("3 of 3 slides pass").

NOT_MEASURED means the check could not trust or measure that slide: treat it as not checked and fix the cause. If a cause cannot be fixed, or the check cannot run on this surface or refuses (no Python, no Chromium, tokens it needs are missing), build anyway and write **not checked** in the reply for that version. Never say it passed.

## 5. Reply

The link, the check result or "not checked", and in two to four lines what you assumed, chose or left out.
