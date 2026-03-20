SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c
.DELETE_ON_ERROR:

UV ?= uv
PROJECT_DIR := $(abspath $(CURDIR))
DOCX := $(sort $(wildcard *.docx))
PPTX := $(sort $(wildcard *.pptx))
OFFICE_FILES := $(DOCX) $(PPTX)
OUTPUT_DIR ?= out
PYTHON ?= $(UV) run python

.PHONY: all sync markitdown pandoc pptx2md clean list-files

all: sync markitdown pandoc pptx2md

sync:
	$(UV) sync

markitdown:
	test -n "$(OFFICE_FILES)" || { echo "No .docx or .pptx files found in $(PROJECT_DIR)"; exit 1; }
	mkdir -p "$(OUTPUT_DIR)/markitdown"
	for office_file in $(OFFICE_FILES); do
	  INPUT_PATH="$$office_file" OUTPUT_PATH="$(OUTPUT_DIR)/markitdown/$$office_file.md" $(PYTHON) scripts/convert_with_markitdown.py
	done

pandoc:
	test -n "$(DOCX)" || { echo "No .docx files found in $(PROJECT_DIR)"; exit 1; }
	mkdir -p "$(OUTPUT_DIR)/pandoc"
	for docx in $(DOCX); do
	  INPUT_PATH="$$docx" OUTPUT_PATH="$(OUTPUT_DIR)/pandoc/$$docx.md" $(PYTHON) scripts/convert_with_pandoc.py
	done

pptx2md:
	test -n "$(PPTX)" || { echo "No .pptx files found in $(PROJECT_DIR)"; exit 1; }
	mkdir -p "$(OUTPUT_DIR)/pptx2md"
	for pptx in $(PPTX); do
	  base="$${pptx%.pptx}"
	  INPUT_PATH="$$pptx" OUTPUT_PATH="$(OUTPUT_DIR)/pptx2md/$$base.md" IMAGE_DIR="$(OUTPUT_DIR)/pptx2md/$${base}_img" $(PYTHON) scripts/convert_with_pptx2md.py
	done

clean:
	rm -rf out .uv-cache

list-files:
	@printf '%s\n' $(OFFICE_FILES)
