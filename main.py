"""Entry point for news-image-20261123.

Copies the committed front-page asset (assets/final-page.png) to
entry.png in the output directory. Pure Python 3 standard library
only; no network, no third-party packages. Deterministic: the same
asset always produces byte-identical output, from any working
directory.
"""

import os
import shutil
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    source = here / "assets" / "final-page.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)


if __name__ == "__main__":
    main()
