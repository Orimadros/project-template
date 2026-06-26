---
paths:
  - "**/*.R"
  - "code/**/*.R"
---

# R Code Standards

**Standard:** Senior Principal Data Engineer + PhD researcher quality

---

## 1. Reproducibility

- `set.seed()` called ONCE at top (YYYYMMDD format)
- All packages loaded at top via `library()` (not `require()`)
- All paths relative to repository root
- `dir.create(..., recursive = TRUE)` for output directories
- Any script that writes `data/` or `results/` assets must update the Provenance Ledger or explicitly flag the required entry.

## 2. Function Design

- `snake_case` naming, verb-noun pattern
- Roxygen-style documentation
- Default parameters, no magic numbers
- Named return values (lists or tibbles)

## 3. Script Readability

- Begin each script with a short human-readable purpose and data-flow description.
- Write top-level code as a narrative pipeline; put repeated or multi-step mechanics inside well-named functions.
- Use descriptive variable names for substantive quantities, samples, model objects, and output paths.
- Comments should explain project logic, sample restrictions, transformations, and why choices were made.

## 4. Domain Correctness

<!-- Customize for your field's known pitfalls -->
- Verify estimator implementations match paper equations and claims
- Check known package bugs (document below in Common Pitfalls)

## 5. Visual Identity

```r
# --- Your institutional palette ---
primary_blue  <- "#012169"
primary_gold  <- "#f2a900"
accent_gray   <- "#525252"
positive_green <- "#15803d"
negative_red  <- "#b91c1c"
```

### Custom Theme
```r
theme_custom <- function(base_size = 14) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title = element_text(face = "bold", color = primary_blue),
      legend.position = "bottom"
    )
}
```

### Figure Dimensions For Paper And Talks
```r
ggsave(filepath, width = 12, height = 5, bg = "transparent")
```

Talk-facing figures should use readable labels and colors that harmonize with `docs/deliverables/preambles/beamer-preamble.tex`.
For presentation exports, also prefer direct labels over distant legends when practical, pair color with line type/shape/position when distinctions are load-bearing, keep grids and borders light, and include units, transformations, sample restrictions, and uncertainty when they affect the slide claim.

## 6. RDS Data Pattern

**Heavy computations saved as RDS; paper/talk rendering loads pre-computed data.**

```r
saveRDS(result, file.path(out_dir, "descriptive_name.rds"))
```

## 7. Common Pitfalls

<!-- Add your field-specific pitfalls here -->
| Pitfall | Impact | Prevention |
|---------|--------|------------|
| Missing `bg = "transparent"` | White boxes in talks | Use transparent backgrounds when figures are layered on slides |
| Hardcoded paths | Breaks on other machines | Use relative paths |

## 8. Line Length & Mathematical Exceptions

**Standard:** Keep lines <= 100 characters.

**Exception: Mathematical Formulas** -- lines may exceed 100 chars **if and only if:**

1. Breaking the line would harm readability of the math (influence functions, matrix ops, finite-difference approximations, formula implementations matching paper equations)
2. An inline comment explains the mathematical operation:
   ```r
   # Sieve projection: inner product of residuals onto basis functions P_k
   alpha_k <- sum(r_i * basis[, k]) / sum(basis[, k]^2)
   ```
3. The line is in a numerically intensive section (simulation loops, estimation routines, inference calculations)

**Quality Gate Impact:**
- Long lines in non-mathematical code: minor penalty (-1 to -2 per line)
- Long lines in documented mathematical sections: no penalty

## 9. Code Quality Checklist

```
[ ] Packages at top via library()
[ ] set.seed() once at top
[ ] All paths relative
[ ] Functions documented (Roxygen)
[ ] Script opens with purpose/data flow and reads as a clear chain of named steps
[ ] Data/results outputs have Provenance Ledger asset and variable-level entries
[ ] Figures: transparent bg, explicit dimensions, seminar-room labels, non-hue encodings, and low-clutter axes
[ ] RDS: every computed object saved
[ ] Comments explain WHY not WHAT
```
