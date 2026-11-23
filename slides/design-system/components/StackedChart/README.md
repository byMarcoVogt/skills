# StackedChart

A total and up to three parts over time in the house frame: stacked bars with the total above each bar, segment values inside, and the segments named at the right end of the last bar.

The example splits a retailer's revenue from 2020 to 2025 into online, stores and wholesale (illustrative values).

## Anatomy

1. **Sticker**: top right, `stamp` in a 2px `navy-700` outline with `radius-stamp`; "Illustrative" because the values are made up.
2. **Action title**: one sentence in `action-title` (Newsreader 500, 52/60), `navy-700`, at most two lines, each under 95% of the title width.
3. **Title rule**: 3px `navy-700`, full width, `space-4` above and below.
4. **Chart title**: `chart-title`, `navy-700`, the measure with its unit after a comma; a 100% stack says "in % of total".
5. **Segments**: at most three, `navy-700` at the base, then `navy-500`, then `slate-300`; square corners; one 2px `hairline` baseline, no y-axis. The part the message is about goes at the base.
6. **Values**: the total above each bar in `data-label` `navy-700`, `space-2` apart; segment values centred inside in `data-label`, white on navy, `navy-700` on `slate-300`; the same precision (here whole €m) in every bar.
7. **Segment names**: at the right end of the last bar, centred on their segments in stacking order, `footnote` bold in the segment's text colour (`navy-700`, `navy-500`, `muted` for the grey segment). No separate legend.
8. **Axis labels**: years as ’20 … ’25 in `footnote`/`muted`.
9. **So-what line**: `body-strong` "So what:" in `navy-700`, then `body`, under a 2px `slate-300` rule; a change in share is written as both values ("21% → 44%").
10. **Footer**: 3px `navy-700` rule at 98px from the bottom; source left; deck short name and page right.

## What the consumer provides

For each period the total and up to three parts that add up to it (more parts grouped into "Other"), the part names, source and vintage, the one-sentence message, and the so-what.
