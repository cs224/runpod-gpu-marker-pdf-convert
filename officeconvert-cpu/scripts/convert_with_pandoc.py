from pathlib import Path
import os

import pypandoc


def main() -> None:
    input_path = Path(os.environ["INPUT_PATH"])
    output_path = Path(os.environ["OUTPUT_PATH"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pypandoc.convert_file(
        str(input_path),
        "gfm",
        format="docx",
        outputfile=str(output_path),
    )


if __name__ == "__main__":
    main()
