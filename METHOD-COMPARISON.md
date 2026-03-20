# Method Comparison

This note compares the methods currently represented in the checked-in output folders:

- `pdfconvert-gpu/out/marker/`
- `pdfconvert-cpu/out/docling/`
- `pdfconvert-cpu/out/pymupdf4llm/`
- `pdfconvert-cpu/out/pdftotext/`
- `pdfconvert-cpu/out/ebook/`

The comparison is based on the actual outputs for these three sample PDFs:

- `thinkpython.pdf`
- `switch-transformers.pdf`
- `image-only-thinkpython.pdf`

## Short Version

If the goal is "best overall markdown conversion", `marker` is clearly the strongest method in this repo.

If the goal is "best local CPU-only method", `docling` is the strongest of the current CPU methods, but it is still noticeably rougher than `marker`.

If the goal is "cheap fallback text extraction from text PDFs", `pdftotext` is the most dependable simple extractor.

## Summary Table

| Method | Workspace | Output | CUDA in this repo workflow | Pure image PDF in current results | Observed strengths | Observed weaknesses |
|---|---|---|---|---|---|---|
| `marker` | `pdfconvert-gpu` | Markdown + metadata JSON | Yes. Explicitly wired for `TORCH_DEVICE=cuda` on Runpod. | Yes | Best overall structure, headings, bullets, links, and usable markdown tables. Only method here that handled all three sample PDFs well. | Heavier stack, model-based, slower and more operationally involved than plain text tools. |
| `docling` | `pdfconvert-cpu` | Markdown | No CUDA path configured in this repo. Used as local CPU method. | Partial yes | Best CPU-side markdown output overall. Can recover text from the raster-only sample where the plain extractors fail. Preserves more structure than `pdftotext`/`ebook`. | More OCR/layout artifacts than `marker`. On `switch-transformers` it produced a very large file and included at least one embedded base64 image blob/corrupted region. |
| `pymupdf4llm` | `pdfconvert-cpu` | Markdown | No | No in current results | Good lightweight markdown for simple text PDFs. `thinkpython` output is readable and reasonably structured. | Failed completely on the image-only sample. Weak on dense tables/layout; `switch-transformers` table extraction is poor. |
| `pdftotext` | `pdfconvert-cpu` | Plain text | No | No in current results | Very dependable fallback for text PDFs. `switch-transformers` prose and contents are clean enough for downstream text use. | No markdown structure, no OCR here, layout noise remains, and image-only PDF produced an empty file. |
| `ebook-convert` | `pdfconvert-cpu` | Plain text | No | No in current results | Works on text PDFs and sometimes gives readable plain text. | Weakest overall quality here. More spacing/line-flow artifacts than `pdftotext`, and image-only PDF produced an empty file. |

## What The Current Outputs Show

### 1. `marker` is the only method here that handled all three PDFs well

Evidence from current outputs:

- `pdfconvert-gpu/out/marker/thinkpython/thinkpython.md` is clean and readable.
- `pdfconvert-gpu/out/marker/switch-transformers/switch-transformers.md` preserves headings, links, lists, and a real markdown contents table.
- `pdfconvert-gpu/out/marker/image-only-thinkpython/image-only-thinkpython.md` contains usable OCR text for the raster-only PDF.

The metadata files also show that `marker` is using different extraction modes depending on the page:

- text PDFs: mostly `pdftext`
- image-heavy pages: `surya`

That hybrid behavior matches what the outputs look like: good direct extraction on text PDFs, and actual OCR recovery on the image-only sample.

### 2. `docling` is the best current CPU-only method, but not clean enough to replace `marker`

Evidence from current outputs:

- `pdfconvert-cpu/out/docling/thinkpython.md` is readable and structurally close to the `marker` result.
- `pdfconvert-cpu/out/docling/image-only-thinkpython.md` is non-empty and recovers a lot of text from the raster-only file.
- `pdfconvert-cpu/out/docling/switch-transformers.md` keeps a lot of the document, including tables and section structure.

But the quality problems are material:

- OCR artifacts are obvious in the image-only sample: dropped spaces, broken URLs, merged words, and character substitutions.
- The `switch-transformers` output is extremely large compared to the others.
- It contains an embedded `data:image/png;base64,...` block, which strongly suggests a bad image serialization/corruption path in this run.

So the practical read is: useful CPU fallback, but the output needs more cleanup than `marker`.

### 3. `pymupdf4llm` is decent for simple text PDFs, but not robust

Evidence from current outputs:

- `pdfconvert-cpu/out/pymupdf4llm/thinkpython.md` is readable and reasonably structured.
- `pdfconvert-cpu/out/pymupdf4llm/switch-transformers.md` is acceptable for plain prose sections.

But:

- `pdfconvert-cpu/out/pymupdf4llm/image-only-thinkpython.md` is empty.
- Table/layout handling is weak on `switch-transformers`; table regions degrade into placeholder columns and damaged markdown tables.

This makes it a reasonable lightweight option for born-digital PDFs, but not a strong general-purpose converter.

### 4. `pdftotext` is a useful fallback extractor, not a high-fidelity converter

Evidence from current outputs:

- `pdfconvert-cpu/out/pdftotext/thinkpython.txt` is plain but readable.
- `pdfconvert-cpu/out/pdftotext/switch-transformers.txt` is surprisingly solid for prose and section listings.

But:

- it keeps column/layout noise
- it does not produce markdown
- `pdfconvert-cpu/out/pdftotext/image-only-thinkpython.txt` is empty

This is still a good baseline method when the document is text-based and the goal is "get the words out reliably".

### 5. `ebook-convert` is the weakest method in this set

Evidence from current outputs:

- `pdfconvert-cpu/out/ebook/thinkpython.txt` is readable but has worse spacing and line-flow than `pdftotext`.
- `pdfconvert-cpu/out/ebook/switch-transformers.txt` is usable, but not better than `pdftotext`.
- `pdfconvert-cpu/out/ebook/image-only-thinkpython.txt` is empty.

Given the current samples, it does not win any category.

## Pure Image PDF Handling

Based on the current checked-in results for `image-only-thinkpython.pdf`:

- `marker`: yes, clearly usable
- `docling`: partial yes, but visibly degraded
- `pymupdf4llm`: no
- `pdftotext`: no
- `ebook-convert`: no

That is the single clearest separator between the methods.

## CUDA / Model Use In This Repo

Important: this section is about the current repo workflows, not every possible upstream capability.

- `marker`
  - Explicitly designed here as the GPU-capable method.
  - `pdfconvert-gpu/Makefile` supports `TORCH_DEVICE=cuda`.
  - Intended Runpod workflow uses CUDA remotely.

- `docling`
  - Used here as a local CPU method.
  - No CUDA path is configured in this repo workflow.

- `pymupdf4llm`
  - Used here as a local CPU method.
  - No CUDA path is configured in this repo workflow.

- `pdftotext`
  - Traditional CLI extractor, no CUDA.

- `ebook-convert`
  - Traditional CLI conversion tool, no CUDA.

## Rule-Of-Thumb Ranking

Overall ranking for this repo's current sample set:

1. `marker`
2. `docling`
3. `pymupdf4llm`
4. `pdftotext`
5. `ebook-convert`

That ranking is based on overall usefulness for markdown conversion, not raw simplicity.

More nuanced rule of thumb:

- Best overall quality: `marker`
- Best local CPU-only option: `docling`
- Best lightweight markdown for simple born-digital PDFs: `pymupdf4llm`
- Best plain text fallback: `pdftotext`
- Lowest priority / least compelling in this repo: `ebook-convert`

One caveat:

- For some text-heavy PDFs, `pdftotext` can be more stable than `pymupdf4llm` if you only care about plain text and not markdown structure.

## Practical Recommendation

Use:

- `marker` when quality matters most, especially for mixed-layout PDFs, image PDFs, or anything you may want as markdown with useful structure.
- `docling` when you want a CPU-only local workflow and still need some OCR/layout recovery.
- `pymupdf4llm` for quick local markdown on straightforward text PDFs.
- `pdftotext` as the baseline fallback extractor.

Avoid treating `ebook-convert` as a primary method unless a specific PDF happens to work unusually well with it.
