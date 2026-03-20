# runpod-gpu-marker-pdf-convert

This repo is centered on one main purpose: speeding up high-quality PDF-to-Markdown conversion with `marker` on GPU-backed machines, especially Runpod pods.

The broader context is slightly wider than the name suggests. In addition to the GPU-first `marker` workflow for PDFs, the repo also includes CPU-only PDF and Office document conversion workspaces that are useful when a GPU is unnecessary or unavailable.

All workflows are kept simple: copy documents into a workspace, run `make all`, inspect that workspace's `out/` directory.

## Blog Post

This repo accompanies the blog post:

- `Quick Tip Nugget: Convert PDFs to Markdown on Runpod with marker-pdf and GPU Support`
- Placeholder link: <https://weisser-zwerg.dev/posts/quick-tip-nugget-gpu-pdf-converter/>

## Project layout

- `filesamples/pdf/`: committed sample PDFs for manual testing
- `filesamples/office/`: committed sample `.docx` and `.pptx` files for manual testing
- `pdfconvert-gpu/`: primary `marker` conversion workspace, including optional Runpod provisioning
- `pdfconvert-cpu/`: local CPU-oriented conversion workspace
- `officeconvert-cpu/`: local CPU-oriented Office document conversion workspace
- `AGENTS.md`: repo-specific workflow rules for assistants

The workspace directories intentionally do not track input PDFs. Each workspace has its own `.gitignore` that ignores local `*.pdf` files.

## How to use the workspaces

1. Copy one or more documents into the workspace you want to test.
2. Change into that workspace directory.
3. Run `make all`.

Example with the committed samples:

```bash
cp filesamples/pdf/*.pdf pdfconvert-gpu/
cd pdfconvert-gpu
make all
```

Or for the CPU workspace:

```bash
cp filesamples/pdf/*.pdf pdfconvert-cpu/
cd pdfconvert-cpu
make all
```

Or for the Office workspace:

```bash
cp filesamples/office/* officeconvert-cpu/
cd officeconvert-cpu
make all
```

## GPU workspace

`pdfconvert-gpu/` is the main workspace in this repo. It uses batch `marker` conversion over all local `*.pdf` files and writes outputs under:

```text
pdfconvert-gpu/out/marker/
```

Key commands:

```bash
cd pdfconvert-gpu
uv sync
make config-ssh SSH_CMD='ssh root@66.92.198.250 -p 11921 -i ~/.ssh/id_ed25519'
make provision
```

`make config-ssh` parses the usual Runpod SSH command once and writes a local `.runpod.mk` file that later targets reuse.

Default `marker` settings are auto-detected:

- `TORCH_DEVICE=auto`
- `MARKER_WORKERS=auto`

Current auto-detection rules:

- if `nvidia-smi` or `nvidia-detector` is available and exits successfully, use `TORCH_DEVICE=cuda`
- otherwise use `TORCH_DEVICE=cpu`
- on CUDA hosts, query GPU memory with `nvidia-smi --query-gpu=memory.total` when available
- on CUDA hosts with `24 GB` VRAM or less, default to `MARKER_WORKERS=1`
- on larger CUDA hosts, reserve `8 GB` for model/runtime overhead, then estimate workers as roughly `floor((VRAM_GB - 8) / 10)`, capped by visible CPU count and a repo-level maximum of `4`
- if CUDA is detected but GPU memory cannot be queried, fall back to `MARKER_WORKERS=1`
- on CPU-only hosts, default to a small CPU-based worker count derived from available CPUs, capped at `4`
- before `marker` starts multiprocessing, the workspace prewarms the required Surya model cache in a single process to avoid first-run download races between workers

Reasoning behind the CUDA rule:

- `marker` workers are constrained more by GPU memory than by raw CPU count.
- A host with many CPUs but limited VRAM can still fail if worker count is too high.
- This repo therefore uses a conservative VRAM-first heuristic on CUDA hosts.
- L4-class cards are intentionally kept at `1` worker by default, and larger GPUs keep explicit VRAM headroom before adding more workers.

Examples:

- `8 GB` GPU: `1` worker
- `22-24 GB` GPU: `1` worker
- `32 GB` GPU: `2` workers
- `48 GB` GPU: `4` workers unless you override `MARKER_WORKERS` explicitly

To inspect the resolved values without running a conversion:

```bash
cd pdfconvert-gpu
make show-marker-config
```

For remote GPU execution on the provisioned pod:

```bash
cd /workspace/pdfconvert-gpu
make all
exit
```

Disk sizing note for GPU pods:

- On the tested Runpod setup, after the initial `marker`/Surya model downloads, the pod storage footprint was about `13 GB` (`du -sh /workspace` reported `13G`).
- Treat that as baseline space for the conversion environment and downloaded models before adding your own PDFs, outputs, or any other large data.
- In practice, provisioning less than `20 GB` leaves little headroom; choose more if you plan to keep large inputs or other datasets on the pod.

Then back on the local machine:

```bash
cd pdfconvert-gpu
make fetch-out
```

## CPU workspace

`pdfconvert-cpu/` is the local-only workspace for tools that do not require a GPU. It is useful for comparison runs, lighter-weight workflows, or environments where GPU-backed `marker` conversion is unnecessary. It processes all local `*.pdf` files and writes outputs under:

- `out/pdftotext/`
- `out/ebook/`
- `out/pymupdf4llm/`
- `out/docling/`

Key commands:

```bash
cd pdfconvert-cpu
uv sync
make all
```

System tools required by some targets:

- `pdftotext` from `poppler-utils`
- `ebook-convert` from `calibre`

The Python-based CPU methods are managed through that workspace's `pyproject.toml` and `uv`.

## Office workspace

`officeconvert-cpu/` is the local-only workspace for Office documents. It broadens the repo beyond PDFs, but it is secondary to the repo's main purpose of high-quality GPU-backed `marker` conversion for PDFs. It currently processes local `.docx` and `.pptx` files and writes outputs under:

- `out/markitdown/`
- `out/pandoc/`
- `out/pptx2md/`

Key commands:

```bash
cd officeconvert-cpu
uv sync
make all
```

`make all` runs these converters:

- `markitdown` for `.docx` and `.pptx`
- `pandoc` for `.docx`
- `pptx2md` for `.pptx`

## Notes

- Run `uv` and `make` from inside the workspace you are using.
- `make all` always operates on the local input files in the current workspace directory.
- `officeconvert-cpu` operates on local `*.docx` and `*.pptx` files in that workspace directory.
- The committed samples in `filesamples/pdf/` and `filesamples/office/` are only there to copy from; they are not used automatically.
