from pathlib import Path
import os

from markitdown import MarkItDown


def main() -> None:
    input_path = Path(os.environ["INPUT_PATH"])
    output_path = Path(os.environ["OUTPUT_PATH"])

    result = MarkItDown().convert(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
