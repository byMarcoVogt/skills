# AppendixSlide

A backup slide in the house frame that carries the dense detail behind the main deck, marked with the "Backup" sticker and numbered A1, A2.

The example is a table of real GDP growth for twelve economies and the world, 2000–19 average to the 2027 projection (values illustrative, after IMF World Economic Outlook, October 2026).

## Anatomy

1. **Sticker**: "Backup" top right (right 80px, top 16px), `stamp` in `navy-700`, 2px `navy-700` outline, `radius-stamp`. It replaces "Illustrative", so made-up values are named as illustrative in the source line instead.
2. **Action title**: one sentence in `action-title`, `navy-700`; the backup still makes a point. Then a 3px `navy-700` rule.
3. **Dense exhibit**: here a table with more rows and tighter row padding, the same type sizes as the main deck (`footnote` bold `muted` header, `body` cells, `tabular-nums`, right-aligned numbers, 1px `hairline` row rules, a 2px `navy-700` rule under the header and above the totals). The message column is `navy-700` bold on `panel`.
4. **Footer**: 3px `navy-700` rule 98px from the bottom; source left in `footnote`/`muted`, including "values illustrative" where they are; deck name in `navy-700`, a `slate-300` "|" and the page number "A1".

The appendix opens with a SectionDivider titled "Appendix".

## What the consumer provides

The detailed data with source and vintage, a one-sentence message, the column or row that carries it, and the appendix page number (A1, A2 …).
