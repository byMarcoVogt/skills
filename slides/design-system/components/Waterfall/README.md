# Waterfall

A bridge from one total to another in the house frame: two full totals, the steps between them floating from the level the previous one left, and an action title that says what the bridge proves.

The example bridges a manufacturer's operating profit from €42.0m in 2024 to €44.5m in 2025 (illustrative values).

## Anatomy

1. **Sticker**: top right, `stamp` in a 2px `navy-700` outline with `radius-stamp`; "Illustrative" because the values are made up.
2. **Action title**: one sentence in `action-title` (Newsreader 500, 52/60), `navy-700`, at most two lines, each under 95% of the title width. Nothing above it.
3. **Title rule**: 3px `navy-700`, full width, `space-4` above and below.
4. **Chart title**: `chart-title`, `navy-700`, the measure with its unit after a comma ("Operating profit (EBIT), in €m").
5. **Legend**: small solid squares for the two step colours only: increase `navy-500`, decrease `slate-300`.
6. **Bars**: totals are full `navy-700` bars from the baseline; steps float, increases `navy-500`, decreases `slate-300`; square corners (`radius-none`); one 2px `hairline` baseline, no y-axis.
7. **Connectors**: 2px `hairline` lines running level from each bar to the next.
8. **Values**: `data-label` in `navy-700`, all above their bars, `space-2` apart; steps signed ("+9.5", "−7.0" with U+2212); one decimal throughout.
9. **Axis labels**: `footnote`/`muted` under each bar; totals named "Total ’24", "Total ’25".
10. **Note** (optional): text on a 2px `muted` rule at its measured text width, a 2px `muted` leader to a 14px `muted` dot hovering above the value it explains.
11. **So-what line**: `body-strong` "So what:" in `navy-700`, then `body` in `ink`, under a 2px `slate-300` rule.
12. **Footer**: 3px `navy-700` rule at 98px from the bottom; source left in `footnote`/`muted`; deck short name and page right in `body-strong`/`navy-700` with a `slate-300` "|".

## What the consumer provides

The start total, the end total and up to about six named steps that add up exactly to the difference, with source and vintage; the one-sentence message; optionally one note on the step the message is about, and the so-what or next step.
