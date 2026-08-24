from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cyrisk_model.models import AnalysisRequest

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_model_request.json"


def load_payload() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_request_selects_explicit_factors() -> None:
    request = AnalysisRequest.model_validate(load_payload())
    assert request.frequency_factor().factor_id == "frequency-range"
    assert [factor.factor_id for factor in request.loss_factors()] == ["recovery-range"]


def test_request_rejects_non_synthetic_scenario() -> None:
    payload = load_payload()
    payload["scenario"]["source_class"] = "supplied"  # type: ignore[index]
    with pytest.raises(ValidationError, match="sealed synthetic"):
        AnalysisRequest.model_validate(payload)


def test_request_rejects_unknown_frequency_factor() -> None:
    payload = load_payload()
    payload["frequency_factor_id"] = "missing-factor"
    with pytest.raises(ValidationError, match="frequency_factor_id"):
        AnalysisRequest.model_validate(payload)


def test_request_rejects_wrong_frequency_unit() -> None:
    payload = load_payload()
    payload["frequency_factor_id"] = "recovery-range"
    with pytest.raises(ValidationError, match="events-per-year"):
        AnalysisRequest.model_validate(payload)


def test_request_rejects_duplicate_loss_factor() -> None:
    payload = load_payload()
    payload["loss_factor_ids"] = ["recovery-range", "recovery-range"]
    with pytest.raises(ValidationError, match="must be unique"):
        AnalysisRequest.model_validate(payload)


def test_request_rejects_unknown_loss_factor() -> None:
    payload = load_payload()
    payload["loss_factor_ids"] = ["missing-factor"]
    with pytest.raises(ValidationError, match="loss factor is not present"):
        AnalysisRequest.model_validate(payload)


def test_request_rejects_loss_factor_unit_mismatch() -> None:
    payload = load_payload()
    payload["loss_factor_ids"] = ["frequency-range"]
    with pytest.raises(ValidationError, match="must match"):
        AnalysisRequest.model_validate(payload)
