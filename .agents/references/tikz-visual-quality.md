# TikZ visual checks

Use these checks when a paper or talk creates or revises a TikZ diagram.

- Keep labels clear of curves, lines, points, braces, and other labels. Stagger nearby
  labels; place group labels beside the last point and axis labels at axis ends.
- Use consistent visual semantics. For example, solid marks can denote observed
  outcomes and hollow or dashed marks counterfactuals when that matches the diagram.
  Do not make an essential distinction depend on color alone.
- Keep axes and data marks visually stronger than grid and reference lines. Use direct
  labels where they reduce legend lookup.
- Extend axes beyond plotted points. Keep enough space around marks and labels, and
  choose a scale that leaves the diagram legible at its final paper or seminar size.
- Make units, transformations, and baselines explicit when they affect the claim.
- Edit the authoritative article or Beamer `.tex` file; do not maintain a separate
  diagram copy that can drift.

Inspect the rendered result for label collisions, consistent semantics, readable
labels, and spacing. Resolve crowding by revising the diagram rather than shrinking
its text.
