---
paths:
  - "docs/sources/**"
---

# Robust PDF Processing

## MarkItDown-First Workflow

When you need or want to read the contents of a PDF, create a Markdown version
with MarkItDown and read that Markdown file instead of reading the PDF directly.
This keeps source reading searchable, quotable, and easier to revisit.

**Step 1: Receive or locate the PDF**
- User uploads PDF or other source material to `docs/sources/`, or the task
  references a PDF already in the repository.
- If the source is a compiled project deliverable and the `.tex` source exists,
  prefer the `.tex` for project-internal claims; use PDF conversion only when
  the compiled PDF itself is the object being reviewed.

**Step 2: Check PDF properties**
```bash
pdfinfo "docs/sources/paper_name.pdf" | grep "Pages:"
ls -lh "docs/sources/paper_name.pdf"
```

**Step 3: Convert to Markdown**
```bash
markitdown docs/sources/hyperdominance-paper.pdf -o docs/sources/hyperdominance-paper.md
```

- Save the Markdown next to the PDF using the same stem unless a project-specific
  source folder already exists.
- If the Markdown is older than the PDF or seems incomplete, regenerate it before
  relying on it.
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

**If a chunk fails to process:**
1. Note the problematic chunk (e.g., "Chunk p021-025 failed")
2. Try splitting into 1-2 page pieces
3. If still failing, skip and document the gap

**If MarkItDown fails or produces poor Markdown:**
1. Note the failure and whether the issue is text extraction, OCR, tables, or
   visual content.
2. Try converting only the relevant pages or splitting into 1-2 page pieces.
3. Check if Ghostscript is installed: `gs --version`
4. Try alternative splitting: `pdftk paper.pdf burst output paper_%03d.pdf`
5. If all else fails, ask the user to upload specific page ranges manually or
   provide an OCR/text version.

**If memory/token issues persist:**
1. Read the generated Markdown by section instead of loading the whole file.
2. Process only 2-3 chunks per session if PDF fallback is needed.
3. Focus on specific sections user identifies as most important.
