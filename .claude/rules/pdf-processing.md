---
paths:
  - "docs/sources/**"
---

# Robust PDF Processing

## pdf-inspector-First Workflow

When you need or want to read the contents of a PDF, create a Markdown version
with Firecrawl [pdf-inspector](https://github.com/firecrawl/pdf-inspector) and
read that Markdown file instead of reading the PDF directly. This keeps source
reading searchable, quotable, and easier to revisit while classifying PDFs that
need OCR before agents rely on an incomplete extraction.

**Step 1: Receive or locate the PDF**
- User uploads PDF or other source material to `docs/sources/`, or the task
  references a PDF already in the repository.
- If the source is a compiled project deliverable and the `.tex` source exists,
  prefer the `.tex` for project-internal claims; use PDF conversion only when
  the compiled PDF itself is the object being reviewed.

**Step 2: Check PDF properties**
```bash
uv run python code/03_quality/pdf_to_markdown.py --help
```

**Step 3: Convert to Markdown**
```bash
uv run python code/03_quality/pdf_to_markdown.py \
  docs/sources/hyperdominance-paper.pdf \
  --output docs/sources/hyperdominance-paper.md
```

- Save the Markdown next to the PDF using the same stem unless a project-specific
  source folder already exists.
- If the Markdown is older than the PDF or seems incomplete, regenerate it before
  relying on it.
- The wrapper runs `pdf_inspector.process_pdf`, which classifies the document
  and produces layout-aware Markdown in one call. It reports `text_based`,
  `mixed`, `scanned`, or `image_based` plus pages that need OCR.
- A `text_based` PDF whose wrapper writes Markdown without a warning can be
  read from the generated Markdown. `mixed` PDFs may yield useful partial
  Markdown, but inspect every reported OCR-needed page in the original PDF or
  page images before making claims about it. For `scanned`, `image_based`, or
  encoding-corrupted PDFs, the wrapper exits without writing Markdown; obtain
  an authorized OCR/text version or use visual inspection for the needed
  material.
- Read the generated Markdown for abstracts, introductions, methods, results,
  literature claims, bibliographic details, and other text-centric content.

**Step 4: Decide whether visual inspection is needed**
Use the original PDF, page images, or PDF chunks in addition to Markdown when
Markdown would lose important information, including:

- scanned or OCR-poor pages
- figures, plots, diagrams, maps, screenshots, or equations where layout matters
- tables whose structure, alignment, footnotes, or multi-panel layout is important
- slide decks or forms where spatial organization carries meaning
- tasks asking about visual design, formatting, pagination, or exact PDF rendering

**Step 5: Selective deep reading**
- After scanning the Markdown, identify the most relevant sections.
- Read those sections in detail for the deliverable you're building.
- Inspect the corresponding PDF pages only when the Markdown is ambiguous or
  when visual/layout content affects the claim.
- Skip appendices, references, or less relevant sections unless needed.

## Error Handling Protocol

**If pdf-inspector fails, reports OCR-needed pages, or produces poor Markdown:**
1. Record whether the problem is an unreadable file, scan/OCR need, broken font
   encoding, tables, or other visual/layout content.
2. For `mixed` PDFs, use the Markdown only for the extractable portions and
   inspect the reported pages directly.
3. For `scanned` or `image_based` PDFs, do not invent a text extraction. Obtain
   an authorized OCR/text version, inspect the necessary PDF pages visually, or
   ask the user for the relevant page range.
4. If a native-text PDF still has poor output, inspect only the relevant page
   range visually and document the limitation in the resulting notes.

**If memory/token issues persist:**
1. Read the generated Markdown by section instead of loading the whole file.
2. Process only 2-3 chunks per session if PDF fallback is needed.
3. Focus on specific sections user identifies as most important.
