"""Seed-controlled sampling and explainable summary calculations."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from decimal import ROUND_HALF_UP, Decimal

from cyrisk_core.canonical import content_hash
from cyrisk_core.models import FactorRange

from cyrisk_model.models import AnalysisRequest, ExposureSummary, InputSensitivity, ModelRun

QUANTUM = Decimal("0.000001")


def _as_float(value: Decimal) -> float:
    return float(value)


def _sample_factor(factor: FactorRange, generator: random.Random) -> float:
    lower = _as_float(factor.lower)
    central = _as_float(factor.central)
    upper = _as_float(factor.upper)
    if factor.distribution == "uniform":
        return generator.uniform(lower, upper)
    if factor.distribution == "triangular":
        return generator.triangular(lower, upper, central)
    width = upper - lower
    if width == 0:
        return lower
    alpha = 1 + 4 * (central - lower) / width
    beta = 1 + 4 * (upper - central) / width
    return lower + width * generator.betavariate(alpha, beta)


def _nearest_rank(sorted_values: Sequence[float], percentile: float) -> float:
    if not 0 < percentile <= 1:
        raise ValueError("percentile must be in (0, 1]")
    index = max(0, math.ceil(percentile * len(sorted_values)) - 1)
    return sorted_values[index]


def _decimal(value: float) -> Decimal:
    return Decimal(str(value)).quantize(QUANTUM, rounding=ROUND_HALF_UP)


def _sensitivity(factor: FactorRange) -> InputSensitivity:
    return InputSensitivity(
        factor_id=factor.factor_id,
        range_width=factor.upper - factor.lower,
        unit=factor.unit,
        interpretation=(
            "Synthetic input-range width; not a causal or real-world importance measure."
        ),
    )


def analyze(request: AnalysisRequest) -> ModelRun:
    """Produce a deterministic synthetic range record from an explicit request."""
    generator = random.Random(request.deterministic_seed)
    frequency = request.frequency_factor()
    loss_factors = request.loss_factors()
    samples = [
        _sample_factor(frequency, generator)
        * sum(_sample_factor(factor, generator) for factor in loss_factors)
        for _ in range(request.sample_count)
    ]
    ordered = sorted(samples)
    summary = ExposureSummary(
        unit=request.scenario.loss_unit,
        sample_count=request.sample_count,
        minimum=_decimal(ordered[0]),
        p05=_decimal(_nearest_rank(ordered, 0.05)),
        p50=_decimal(_nearest_rank(ordered, 0.50)),
        p95=_decimal(_nearest_rank(ordered, 0.95)),
        maximum=_decimal(ordered[-1]),
        mean=_decimal(sum(ordered) / len(ordered)),
    )
    input_hash = content_hash(
        {
            "scenario": request.scenario.model_dump(mode="json"),
            "request": request.model_dump(mode="json", exclude={"scenario"}),
        }
    )
    sensitivities = tuple(_sensitivity(factor) for factor in (frequency, *loss_factors))
    output_hash = content_hash(
        {
            "summary": summary.model_dump(mode="json"),
            "sensitivities": [item.model_dump(mode="json") for item in sensitivities],
        }
    )
    return ModelRun(
        run_id=f"run-{content_hash({'input_hash': input_hash, 'output_hash': output_hash})[:16]}",
        request_id=request.request_id,
        scenario_id=request.scenario.scenario_id,
        model_version=request.model_version,
        deterministic_seed=request.deterministic_seed,
        input_hash=input_hash,
        output_hash=output_hash,
        completeness_status=request.completeness_status,
        summary=summary,
        sensitivities=sensitivities,
        limitations=request.limitations,
    )
