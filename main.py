"""Copy the committed front page into the competition's output directory."""

import os
from pathlib import Path
import shutil


def main():
    image = Path(__file__).resolve().with_name("entry.png").read_bytes()
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    output.mkdir(parents=True, exist_ok=True)
    for child in output.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
    (output / "entry.png").write_bytes(image)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
