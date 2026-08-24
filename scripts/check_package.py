"""Verify the released wheel contains the public model surface and typed marker."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "cyrisk_model/__init__.py",
    "cyrisk_model/engine.py",
    "cyrisk_model/models.py",
    "cyrisk_model/py.typed",
}


def main() -> int:
    wheels = sorted((ROOT / "dist").glob("cyrisk_model-*.whl"))
    if len(wheels) != 1:
        print(f"expected one wheel, found {len(wheels)}", file=sys.stderr)
        return 1
    with zipfile.ZipFile(wheels[0]) as archive:
        missing = REQUIRED - set(archive.namelist())
    if missing:
        print(f"wheel missing files: {sorted(missing)}", file=sys.stderr)
        return 1
    print(f"VALID wheel={wheels[0].name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
