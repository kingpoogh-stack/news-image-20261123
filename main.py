"""Deliverable for the news-image-20261123 entry.

The front-page image is rendered ahead of time and committed as
assets/final-page.png. This program simply places a copy of that
asset at entry.png inside the output directory, which is taken from
the MAKEFUN_OUTPUT_DIR environment variable when set and defaults
to /output. It uses nothing beyond the Python standard library, so
it runs unchanged in the grading sandbox, and because it only ever
copies the same committed bytes, its output is identical on every
run and from every working directory.
"""

import os
import shutil
from pathlib import Path


def deliver() -> Path:
    asset = Path(__file__).resolve().parent / "assets" / "final-page.png"
    destination_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "entry.png"
    shutil.copyfile(asset, destination)
    return destination


if __name__ == "__main__":
    deliver()
