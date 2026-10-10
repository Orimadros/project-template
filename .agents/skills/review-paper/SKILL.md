---
name: review-paper
description: Review a canonical or external paper for argument, evidence, methods, or prose.
disable-model-invocation: true
---

# Review a paper

Use this when Leo requests a manuscript review. The request controls the scope: a
referee-style review, methods review, or focused proofreading pass. If no lens is
specified, provide a concise referee-style review. This skill reviews articles and
appendices; code review belongs to the code-review workflow, and talk review belongs
to `review-slides`.

## Workflow

1. Resolve the target from Leo's request. Default to
   `docs/deliverables/articles/main/main.tex`. Include appendices when they bear on the
   requested paper review. For an external PDF, follow
   `../../references/pdf-source-reading.md` and state any extraction limits.
2. Read the relevant article files and, for the canonical paper, the linked generated
   outputs and bibliography entries that support its main claims. Read the domain or
   journal profile only when relevant and meaningfully filled in.
3. Review the requested lens. For a broad review, assess question and contribution,
   literature positioning, data and measurement, identification or theoretical logic,
   inference, results, limitations, exposition, and consistency with cited evidence.
   For methods, focus on assumptions, estimand, design, estimation, inference, and
   robustness. For proofreading, report language, notation, and citation-consistency
   issues without expanding into a methods review.
4. Make each material finding specific: location, issue, why it matters, and a
   practical correction or decision for Leo. Separate evidence-based concerns from
   interpretation. Verify an external source before asserting that the paper
   misrepresents it; if source access is incomplete, say so.
5. Return prioritized findings and a short assessment of what works. Do not edit the
   manuscript or make research choices. Save a report only if Leo asks for a file.

Do not assign an aggregate score or numerical quality grade. Do not invent a concern to
fill a quota. The review is complete when the requested scope has been covered, every
major concern points to the relevant text or evidence, and limits of verification are
clear.
