# AEA/JEP article at 10.1257/jep.28.1.209

- Source: Jonathan A. Schwabish, "An Economist's Guide to Visualizing Data," *Journal of Economic Perspectives* 28(1): 209-234, Winter 2014. DOI: [10.1257/jep.28.1.209](https://doi.org/10.1257/jep.28.1.209). Official AEA page: <https://www.aeaweb.org/articles?id=10.1257/jep.28.1.209>. Full-text mirror read: <https://surf.econ.uic.edu/wp-content/uploads/sites/882/2023/05/Schwabish-Jonathan.-An-Economists-Guide-to-Visualizing-Data-2014.pdf>.
- Access status: Official AEA metadata page accessible; official AEA PDF redirected to a Cloudflare challenge/403 in this environment. Full article text was read from the UIC-hosted PDF mirror and cross-checked against the AEA metadata. This is direct-source reading from a mirror, not secondary-source reconstruction.
- Report date: 2026-05-25

## Core Slide-Writing Principles

- **Direct source claim:** Schwabish frames effective visualization around three principles: show the data, reduce clutter, and integrate explanatory text with the graph (pp. 210-211). He explicitly says graphs in reports and verbal presentations are for the reader or seminar audience, not for the author (p. 211).
  **Interpretation for economic research talks:** A talk figure should be redesigned for first-time audience comprehension, not copied from the exploratory output or paper appendix. The seminar listener should see the empirical object, unit, comparison, and takeaway without decoding software defaults.

- **Direct source claim:** The article roots good graphs in visual perception: viewers process basic visual attributes such as contrast, color, size, orientation, and shape quickly, so these attributes can guide attention (pp. 209-211).
  **Interpretation for economic research talks:** Use one or two visual encodings to make the estimand, treatment group, event date, or preferred specification pop. De-emphasize context series in gray, reserve accent color for the claim, and avoid decorative encodings that compete with the result.

- **Direct source claim:** Schwabish treats clutter as unnecessary or distracting visual material, including heavy gridlines, redundant tick marks and labels, icons, pictures, gradients, and fake dimensions (p. 210). Several redesigns lighten gridlines, remove redundant percent signs, reduce repeated labels, and make the data line visually dominant (pp. 212-214).
  **Interpretation for economic research talks:** Talk-facing plots should have muted grids, minimal tick marks, non-redundant units, no gradient fills, and no default point markers on every observation unless the marker carries meaning.

- **Direct source claim:** Legends and labels should be integrated close to the relevant mark; the article criticizes legends placed away from lines/bars/points and shows examples with direct labels and titles/units placed near the top-left entry point (pp. 210-211, 219).
  **Interpretation for economic research talks:** Prefer direct labels at line ends, beside highlighted dots, or above grouped bars. A Beamer audience should not have to look back and forth between a distant legend and the figure while listening.

- **Direct source claim:** Chart form should match the comparison task. The article recommends small multiples for dense multi-series line charts, zero baselines for bar/column charts, flat charts instead of 3D charts, horizontal layouts when labels are long, and alternatives to pie charts when the task is category comparison rather than simple part-to-whole judgment (pp. 212-226).
  **Interpretation for economic research talks:** Use small multiples or highlighted-series builds for heterogeneity/event-study panels; start bar charts at zero; avoid 3D; rotate the chart horizontally rather than rotating long labels; use bars, stacked bars, paired bars, or slope charts instead of pies when comparing categories across groups or time.

- **Direct source claim:** Schwabish notes a tension between explaining a specific idea and providing exact lookup values; when only selected points are labeled, complete data can be provided through a website, supplement, table, or appendix (pp. 215, 219-222).
  **Interpretation for economic research talks:** Slides may foreground the five relevant states, bins, cohorts, or countries, but complete labels and dense lookup tables belong in backup slides, the paper, or linked replication materials.

- **Direct source claim:** The article treats color as useful but easy to misuse, warns against default palettes, recommends designs that work in grayscale when needed, and notes that color-vision deficiencies affect a nontrivial share of viewers (pp. 211, 228-229).
  **Interpretation for economic research talks:** Color should not be the only carrier of meaning. Talk figures should pass a grayscale/color-vision sanity check, especially when they compare red/green series or when slides may be printed.

## Beamer-Specific Implications

- Build separate talk-facing figure exports when paper figures are too dense. A Beamer figure should have larger labels, lighter grids, fewer labels, and direct annotation around the claim.
- Let the `frame` title or a figure-internal title carry the substantive message; put units in the title/subtitle area rather than repeating units on every axis tick.
- For multi-line plots, use small multiples, direct line-end labels, or a staged highlight with `\only`, `\onslide`, or adjacent frames. Avoid a single spaghetti chart unless the point is the aggregate tangle itself.
- For scatterplots, label the observations discussed in the narration and gray out the rest. If unlabeled observations matter for transparency, put the full labeled version in backup.
- For bar/column charts, start at zero unless there is a clearly disclosed and defensible reason not to. Use horizontal bars for long treatment names, outcomes, countries, or bins.
- Avoid 3D chart effects, gradient fills, heavy borders, and decorative icons in empirical figures. They consume visual hierarchy and can distort perceived magnitudes.
- Treat pie charts as a narrow special case for a single part-to-whole message. For most seminar comparisons, use bars, stacked bars, paired bars, or slope charts.
- Use the shared Beamer accent colors semantically, but also verify the figure remains interpretable in grayscale. Pair color with labels, line style, marker shape, or position when the distinction is load-bearing.
- Use backup slides for exact lookup values, full regression tables, complete category labels, and unhighlighted robustness variants. The main slide should explain; the backup can document.

## What This Would Change In Our Current Framework

- Add a compact "data graphics checklist" to `.claude/rules/slide-writing-principles.md`: show the data, reduce clutter, integrate labels/text with the plotted marks, override software defaults, and design for the seminar audience rather than the analyst.
- Add chart-specific guidance under "Tables And Results": bar charts should normally start at zero; long labels should usually imply horizontal bars; dense multi-series line plots should become small multiples or highlighted-series builds; 3D charts should be disallowed for empirical results.
- Add a color verification bullet: figures should remain legible in grayscale and should not depend on red/green or hue-only contrasts for the main comparison.
- Add a backup-slide norm for selective labeling: if the main slide labels only the observations needed for the argument, provide the full labeled figure, table, or source path in backup when lookup matters.

## Tensions Or Caveats

- The article is about data visualization for research communication broadly, not a Beamer manual. The Beamer implications above are translations, not direct prescriptions from Schwabish.
- Some design choices are explicitly subjective in the article, including line thickness, series order, axis-label style, fonts, and palette. The stronger rules are for avoiding distortion, clutter, and unnecessary decoding.
- Removing labels can improve the talk slide while reducing lookup value. That is acceptable only when the paper, backup, or replication material preserves the full information.
- Schwabish is nuanced about pie charts: the article does not say they can never be used. It argues they are weak for many comparisons and more defensible for focused part-to-whole judgments.
- The tool list is from 2014. The durable contribution for this template is the design logic, not the specific software recommendations.

## Source Notes

- Official metadata from the AEA page identifies the article as Schwabish (2014), *Journal of Economic Perspectives* 28(1): 209-234, DOI [10.1257/jep.28.1.209](https://doi.org/10.1257/jep.28.1.209).
- Publisher access path attempted: <https://www.aeaweb.org/articles?id=10.1257/jep.28.1.209> -> "Download Full Text PDF (Complimentary)" -> `https://pubs.aeaweb.org/doi/pdfplus/10.1257/jep.28.1.209`; the final PDF request returned a Cloudflare challenge/403.
- Full-text reading path used: UIC-hosted PDF mirror at <https://surf.econ.uic.edu/wp-content/uploads/sites/882/2023/05/Schwabish-Jonathan.-An-Economists-Guide-to-Visualizing-Data-2014.pdf>.
- No new bibliography entry was added because the project task only requested this source report, and the official citation details are already known from the AEA page.
