#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess


CUDA_RESERVED_VRAM_GB = 8
CUDA_SINGLE_WORKER_MAX_VRAM_GB = 24
VRAM_GB_PER_WORKER = 10
MAX_AUTO_WORKERS = 4


def detect_cuda() -> bool:
    for command in ("nvidia-smi", "nvidia-detector"):
        path = shutil.which(command)
        if not path:
            continue
        try:
            completed = subprocess.run(
                [path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if completed.returncode == 0:
            return True
    return False


def detect_nvidia_total_memory_gb() -> int | None:
    path = shutil.which("nvidia-smi")
    if not path:
        return None
    try:
        completed = subprocess.run(
            [
                path,
                "--query-gpu=memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if completed.returncode != 0:
        return None

    values: list[int] = []
    for line in completed.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            mib = int(line)
        except ValueError:
            continue
        values.append(mib)

    if not values:
        return None

    # Be conservative if multiple GPUs are visible.
    return max(1, min(values) // 1024)


def resolve_torch_device(value: str) -> str:
    if value != "auto":
        return value
    return "cuda" if detect_cuda() else "cpu"


def resolve_workers(value: str, torch_device: str) -> int:
    if value != "auto":
        workers = int(value)
        if workers < 1:
            raise SystemExit("MARKER_WORKERS must be >= 1")
        return workers

    cpu_count = os.cpu_count() or 1
    if torch_device == "cuda":
        total_memory_gb = detect_nvidia_total_memory_gb()
        if total_memory_gb is None:
            return 1
        # Keep L4-class GPUs on a single worker by default; marker's OCR stack
        # has enough per-process overhead that a 22-24 GB card easily OOMs.
        if total_memory_gb <= CUDA_SINGLE_WORKER_MAX_VRAM_GB:
            return 1
        usable_vram_gb = max(1, total_memory_gb - CUDA_RESERVED_VRAM_GB)
        gpu_based_workers = max(1, usable_vram_gb // VRAM_GB_PER_WORKER)
        return max(1, min(MAX_AUTO_WORKERS, cpu_count, gpu_based_workers))
    return max(1, min(MAX_AUTO_WORKERS, cpu_count // 2 or 1))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--torch-device", required=True)
    parser.add_argument("--marker-workers", required=True)
    args = parser.parse_args()

    torch_device = resolve_torch_device(args.torch_device)
    marker_workers = resolve_workers(args.marker_workers, torch_device)

    print(f"TORCH_DEVICE={torch_device}")
    print(f"MARKER_WORKERS={marker_workers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
