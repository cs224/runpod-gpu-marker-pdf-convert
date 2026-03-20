#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from surya.common.s3 import download_directory
from surya.settings import settings


def iter_model_downloads():
    checkpoints = (
        ("layout", settings.LAYOUT_MODEL_CHECKPOINT),
        ("recognition", settings.RECOGNITION_MODEL_CHECKPOINT),
        ("table_rec", settings.TABLE_REC_MODEL_CHECKPOINT),
        ("detection", settings.DETECTOR_MODEL_CHECKPOINT),
        ("ocr_error", settings.OCR_ERROR_MODEL_CHECKPOINT),
    )

    seen: set[str] = set()
    for name, checkpoint in checkpoints:
        if not checkpoint.startswith("s3://") or checkpoint in seen:
            continue
        seen.add(checkpoint)
        remote_path = checkpoint.removeprefix("s3://")
        local_dir = Path(settings.MODEL_CACHE_DIR) / remote_path
        yield name, remote_path, local_dir


def main() -> int:
    for name, remote_path, local_dir in iter_model_downloads():
        local_dir.mkdir(parents=True, exist_ok=True)
        print(f"Ensuring {name} model cache at {local_dir}")
        download_directory(remote_path, str(local_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
