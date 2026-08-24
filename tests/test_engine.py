from __future__ import annotations

from pathlib import Path
from random import Random

import pytest
from cyrisk_core.models import FactorRange
from pydantic import ValidationError

from cyrisk_model.engine import _nearest_rank, _sample_factor, analyze
from cyrisk_model.models import AnalysisRequest, ExposureSummary

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic_model_request.json"


def load_request() -> AnalysisRequest:
    return AnalysisRequest.model_validate_json(FIXTURE.read_text(encoding="utf-8"))


def test_same_seed_and_request_produce_same_run() -> None:
    request = load_request()
    assert analyze(request) == analyze(request)


def test_different_seed_changes_synthetic_run() -> None:
    request = load_request()
    changed = request.model_copy(update={"deterministic_seed": 9})
    assert analyze(request).output_hash != analyze(changed).output_hash


def test_run_preserves_unit_and_partial_status() -> None:
    run = analyze(load_request())
    assert run.summary.unit == "synthetic-usd"
    assert run.completeness_status == "partial"
    assert len(run.sensitivities) == 2


def test_nearest_rank_rejects_invalid_percentile() -> None:
    with pytest.raises(ValueError, match="percentile"):
        _nearest_rank([1.0, 2.0], 0)


def test_uniform_sampler_returns_value_inside_declared_bounds() -> None:
    factor = FactorRange(
        factor_id="uniform-factor",
        metric="synthetic uniform factor",
        unit="synthetic-unit",
        distribution="uniform",
        lower="1",
        central="2",
        upper="3",
        source_class="synthetic",
        confidence="low",
        rationale="Sealed test input.",
    )
    assert 1 <= _sample_factor(factor, Random(7)) <= 3


def test_zero_width_pert_sampler_returns_declared_value() -> None:
    factor = FactorRange(
        factor_id="flat-pert-factor",
        metric="synthetic fixed factor",
        unit="synthetic-unit",
        distribution="pert",
        lower="2",
        central="2",
        upper="2",
        source_class="synthetic",
        confidence="low",
        rationale="Sealed test input.",
    )
    assert _sample_factor(factor, Random(7)) == 2


def test_summary_rejects_unordered_percentiles() -> None:
    with pytest.raises(ValidationError, match="ordered"):
        ExposureSummary(
            unit="synthetic-usd",
            sample_count=100,
            minimum="0",
            p05="3",
            p50="2",
            p95="4",
            maximum="5",
            mean="2",
        )
