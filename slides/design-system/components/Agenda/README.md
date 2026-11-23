# Agenda

A content slide in the house frame that lists the deck's sections as rows under a title that states the deck's answer, repeated before each section with the current row highlighted.

The example shows the agenda repeated before section 2 of a world-economy briefing.

## Anatomy

1. **Action title**: the deck's answer in one sentence in `action-title`, `navy-700`, never "Agenda"; then a 3px `navy-700` rule, `space-4` apart.
2. **Rows**: one per section, separated by 1px `hairline` rules, spread evenly over the body height. Each row holds an icon that depicts the section (24px grid, 2px stroke, no fill, at `icon-glyph` size, centred on the first text line), the section title in `body-strong`, one line in `body` on the question it answers, and its first page number right-aligned in `muted`, `tabular-nums`.
3. **First state** (no section current): titles and icons `navy-700`, lines in `ink`, page numbers `muted`.
4. **Repeated state**: the current row keeps the first state; all other rows, their icons included, turn `muted`.
5. **Footer**: 3px `navy-700` rule 98px from the bottom; source left in `footnote`/`muted`; deck name in `navy-700`, a `slate-300` "|" and the page number right.

## What the consumer provides

The deck's answer as one sentence, the sections with one line each on what they answer and their first page number, an icon per section that says what it covers, and which section is current (or none for the first agenda).
