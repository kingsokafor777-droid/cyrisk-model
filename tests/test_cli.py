from __future__ import annotations

import json
from pathlib import Path

import pytest

from cyrisk_model.cli import main

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "synthetic_model_request.json"


def test_cli_emits_synthetic_run(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["analyze", str(FIXTURE)]) == 0
    emitted = json.loads(capsys.readouterr().out)
    assert emitted["summary"]["unit"] == "synthetic-usd"


def test_cli_rejects_invalid_json(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("not-json", encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["analyze", str(invalid)])
