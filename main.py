"""Entry program for the make.fun bounty "Sum up 17 November's world
news in one image" (news-image-20261117).

The artwork ships in this repository as ``entry.png`` beside this file;
the program simply copies it to the output directory, so every run —
with no network and a read-only repo mount — writes byte-identical
output. The output directory is ``/output`` by default and can be
overridden with the ``MAKEFUN_OUTPUT_DIR`` environment variable.
"""

import os
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"


def output_path():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    return out_dir / "entry.png"


def main():
    target = output_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, target)


if __name__ == "__main__":
    main()
