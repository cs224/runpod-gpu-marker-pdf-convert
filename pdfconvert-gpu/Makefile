SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c
.DELETE_ON_ERROR:

RUNPOD_CONFIG ?= .runpod.mk
-include $(RUNPOD_CONFIG)

UV ?= uv
PROJECT_DIR := $(abspath $(CURDIR))
PDFS := $(sort $(wildcard *.pdf))
INPUT_DIR ?= .marker-input
OUTPUT_DIR ?= out/marker
MARKER_WORKERS ?= auto
TORCH_DEVICE ?= auto
MARKER_FLAGS ?= --output_format markdown --disable_image_extraction

SSH_HOST ?= root@66.92.198.250
SSH_PORT ?= 11921
SSH_KEY ?= $(HOME)/.ssh/id_ed25519
REMOTE_DIR ?= /workspace/pdfconvert-gpu
REMOTE_SSH := ssh -p $(SSH_PORT) -i $(SSH_KEY) $(SSH_HOST)
REMOTE_SCP := scp -P $(SSH_PORT) -i $(SSH_KEY)
REMOTE_RSYNC := rsync -avz --delete -e "ssh -p $(SSH_PORT) -i $(SSH_KEY)"
SYNC_FILES := Makefile pyproject.toml .gitignore
PROVISION_FILES := $(SYNC_FILES) $(PDFS)
REMOTE_SCRIPT_DIR := $(REMOTE_DIR)/scripts
SCRIPT_FILES := $(sort $(wildcard scripts/*.py))

.PHONY: all sync convert provision fetch-out clean list-pdfs config-ssh show-ssh-config clear-ssh-config require-ssh-config show-marker-config

all: sync convert

sync:
	$(UV) sync

convert:
	test -n "$(PDFS)" || { echo "No PDFs found in $(PROJECT_DIR)"; exit 1; }
	eval "$$($(UV) run --no-sync python scripts/resolve_marker_settings.py --torch-device '$(TORCH_DEVICE)' --marker-workers '$(MARKER_WORKERS)')"
	printf 'Using marker settings: TORCH_DEVICE=%s MARKER_WORKERS=%s\n' "$$TORCH_DEVICE" "$$MARKER_WORKERS"
	$(UV) run --no-sync python scripts/prewarm_marker_models.py
	rm -rf "$(INPUT_DIR)"
	mkdir -p "$(INPUT_DIR)" "$(OUTPUT_DIR)"
	for pdf in $(PDFS); do
	  ln -sf "$(PROJECT_DIR)/$$pdf" "$(INPUT_DIR)/$$pdf"
	done
	TORCH_DEVICE="$$TORCH_DEVICE" $(UV) run marker "$(INPUT_DIR)" --output_dir "$(OUTPUT_DIR)" --workers "$$MARKER_WORKERS" $(MARKER_FLAGS)

show-marker-config:
	eval "$$($(UV) run --no-sync python scripts/resolve_marker_settings.py --torch-device '$(TORCH_DEVICE)' --marker-workers '$(MARKER_WORKERS)')"
	printf 'TORCH_DEVICE=%s\nMARKER_WORKERS=%s\n' "$$TORCH_DEVICE" "$$MARKER_WORKERS"

require-ssh-config:
	test -f "$(RUNPOD_CONFIG)" || { echo "Missing $(RUNPOD_CONFIG). Run: make config-ssh SSH_CMD='ssh root@HOST -p PORT -i ~/.ssh/id_ed25519'"; exit 1; }
	test -n "$(SSH_HOST)" || { echo "SSH_HOST is empty in $(RUNPOD_CONFIG)"; exit 1; }
	test -n "$(SSH_PORT)" || { echo "SSH_PORT is empty in $(RUNPOD_CONFIG)"; exit 1; }
	test -n "$(SSH_KEY)" || { echo "SSH_KEY is empty in $(RUNPOD_CONFIG)"; exit 1; }

config-ssh:
	test -n "$(SSH_CMD)" || { echo "Usage: make config-ssh SSH_CMD='ssh root@HOST -p PORT -i ~/.ssh/id_ed25519'"; exit 1; }
	$(UV) run --no-sync python scripts/configure_ssh.py --ssh-cmd '$(SSH_CMD)' --output "$(RUNPOD_CONFIG)"

show-ssh-config: require-ssh-config
	sed -n '1,120p' "$(RUNPOD_CONFIG)"

clear-ssh-config:
	rm -f "$(RUNPOD_CONFIG)"

provision: require-ssh-config
	test -n "$(PDFS)" || { echo "No PDFs found in $(PROJECT_DIR)"; exit 1; }
	$(REMOTE_SSH) "install -d '$(REMOTE_DIR)' '$(REMOTE_SCRIPT_DIR)'"
	$(REMOTE_SSH) "command -v uv >/dev/null 2>&1 || { curl -LsSf https://astral.sh/uv/install.sh | sh; install -m 0755 /root/.local/bin/uv /usr/local/bin/uv; if [ -x /root/.local/bin/uvx ]; then install -m 0755 /root/.local/bin/uvx /usr/local/bin/uvx; fi; }"
	$(REMOTE_SSH) "command -v rsync >/dev/null 2>&1 || { apt-get update && apt-get install -y rsync; }"
	$(REMOTE_SSH) "find '$(REMOTE_DIR)' -maxdepth 1 -type f \\( -name '*.pdf' -o -name '.gitignore' -o -name 'Makefile' -o -name 'pyproject.toml' \\) -delete"
	$(REMOTE_SSH) "find '$(REMOTE_SCRIPT_DIR)' -maxdepth 1 -type f -name '*.py' -delete"
	$(REMOTE_SCP) $(PROVISION_FILES) "$(SSH_HOST):$(REMOTE_DIR)/"
	$(REMOTE_SCP) $(SCRIPT_FILES) "$(SSH_HOST):$(REMOTE_SCRIPT_DIR)/"
	@printf '%s\n' "Provisioned $(REMOTE_DIR) on $(SSH_HOST)." "Next step on the pod:" "  cd $(REMOTE_DIR) && make all"

fetch-out: require-ssh-config
	if $(REMOTE_SSH) "command -v rsync >/dev/null 2>&1"; then
	  mkdir -p out
	  $(REMOTE_RSYNC) "$(SSH_HOST):$(REMOTE_DIR)/out/" "out/"
	else
	  rm -rf out
	  mkdir -p out
	  $(REMOTE_SSH) "test -d '$(REMOTE_DIR)/out'"
	  $(REMOTE_SSH) "cd '$(REMOTE_DIR)/out' && tar -cf - ." | tar -xf - -C out
	fi

clean:
	rm -rf "$(INPUT_DIR)" out

list-pdfs:
	@printf '%s\n' $(PDFS)
