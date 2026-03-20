SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c
.DELETE_ON_ERROR:

UV ?= uv
PROJECT_DIR := $(abspath $(CURDIR))
PDFS := $(sort $(wildcard *.pdf))
OUTPUT_DIR ?= out
PYTHON ?= $(UV) run python

.PHONY: all sync pdftotext ebook pymupdf4llm docling clean list-pdfs

all: sync pdftotext ebook pymupdf4llm docling

sync:
	$(UV) sync

pdftotext:
	test -n "$(PDFS)" || { echo "No PDFs found in $(PROJECT_DIR)"; exit 1; }
	command -v pdftotext >/dev/null || { echo "Missing: pdftotext (install poppler-utils)"; exit 1; }
	mkdir -p "$(OUTPUT_DIR)/pdftotext"
	for pdf in $(PDFS); do
	  base="$${pdf%.pdf}"
	  pdftotext -enc UTF-8 -layout -nopgbrk "$$pdf" "$(OUTPUT_DIR)/pdftotext/$$base.txt"
	done

ebook:
	test -n "$(PDFS)" || { echo "No PDFs found in $(PROJECT_DIR)"; exit 1; }
	command -v ebook-convert >/dev/null || { echo "Missing: ebook-convert (install calibre)"; exit 1; }
	mkdir -p "$(OUTPUT_DIR)/ebook"
	for pdf in $(PDFS); do
	  base="$${pdf%.pdf}"
	  ebook-convert "$$pdf" "$(OUTPUT_DIR)/ebook/$$base.txt"
	done

pymupdf4llm:
	test -n "$(PDFS)" || { echo "No PDFs found in $(PROJECT_DIR)"; exit 1; }
	mkdir -p "$(OUTPUT_DIR)/pymupdf4llm"
	for pdf in $(PDFS); do
	  base="$${pdf%.pdf}"
	  PDF_PATH="$$pdf" OUTPUT_PATH="$(OUTPUT_DIR)/pymupdf4llm/$$base.md" $(PYTHON) -c 'from pathlib import Path; import os; import pymupdf4llm; Path(os.environ["OUTPUT_PATH"]).write_text(pymupdf4llm.to_markdown(os.environ["PDF_PATH"]), encoding="utf-8")'
	done

docling:
	test -n "$(PDFS)" || { echo "No PDFs found in $(PROJECT_DIR)"; exit 1; }
	mkdir -p "$(OUTPUT_DIR)/docling"
	for pdf in $(PDFS); do
	  stem="$${pdf%.pdf}"
	  tmp_dir="$$(mktemp -d)"
	  $(UV) run docling "$$pdf" --output "$$tmp_dir"
	  md_file="$$(find "$$tmp_dir" -type f -name '*.md' | head -n 1)"
	  test -n "$$md_file" || { echo "Docling did not produce Markdown for $$pdf"; rm -rf "$$tmp_dir"; exit 1; }
	  cp "$$md_file" "$(OUTPUT_DIR)/docling/$$stem.md"
	  rm -rf "$$tmp_dir"
	done

clean:
	rm -rf out .uv-cache

list-pdfs:
	@printf '%s\n' $(PDFS)
