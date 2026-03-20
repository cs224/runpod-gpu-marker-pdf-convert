from pathlib import Path
import os

from pptx2md import ConversionConfig, convert


def main() -> None:
    input_path = Path(os.environ["INPUT_PATH"])
    output_path = Path(os.environ["OUTPUT_PATH"])
    image_dir = Path(os.environ["IMAGE_DIR"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)
    convert(
        ConversionConfig(
            pptx_path=input_path,
            output_path=output_path,
            image_dir=image_dir,
            disable_notes=True,
        )
    )


if __name__ == "__main__":
    main()
