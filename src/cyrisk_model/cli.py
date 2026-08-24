"""Local CLI for deterministic Cyrisk synthetic analysis requests."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from cyrisk_model.engine import analyze
from cyrisk_model.models import AnalysisRequest


def _load(path: Path) -> AnalysisRequest:
    with path.open(encoding="utf-8") as handle:
        return AnalysisRequest.model_validate(json.load(handle))


def main(argv: Sequence[str] | None = None) -> int:
    """Analyze one local JSON request and emit stable JSON."""
    parser = argparse.ArgumentParser(prog="cyrisk-model")
    parser.add_argument("command", choices=("analyze",))
    parser.add_argument("request", type=Path)
    args = parser.parse_args(argv)
    try:
        run = analyze(_load(args.request))
    except (OSError, ValidationError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    print(run.model_dump_json(by_alias=True))
    return 0
