"""Typed inputs and outputs for deterministic synthetic range analysis."""

from __future__ import annotations

from decimal import Decimal

from cyrisk_core.models import FactorRange, RiskScenario, SourceClass
from pydantic import BaseModel, ConfigDict, Field, model_validator

ID_PATTERN = r"^[a-z][a-z0-9_-]{2,63}$"


class ModelRecord(BaseModel):
    """Strict immutable model record."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class AnalysisRequest(ModelRecord):
    """Explicit synthetic analysis request; factor selection is never inferred."""

    request_id: str = Field(pattern=ID_PATTERN)
    scenario: RiskScenario
    frequency_factor_id: str = Field(pattern=ID_PATTERN)
    loss_factor_ids: tuple[str, ...] = Field(min_length=1)
    deterministic_seed: int = Field(ge=0, le=2_147_483_647)
    sample_count: int = Field(ge=100, le=100_000)
    model_version: str = Field(default="0.1.0", pattern=r"^\d+\.\d+\.\d+$")
    completeness_status: str = Field(pattern=r"^(complete|partial|insufficient)$")
    limitations: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_semantics(self) -> AnalysisRequest:
        if self.scenario.source_class is not SourceClass.SYNTHETIC:
            raise ValueError("v0.1.0 model accepts only sealed synthetic scenarios")
        factor_map = {factor.factor_id: factor for factor in self.scenario.factors}
        frequency = factor_map.get(self.frequency_factor_id)
        if frequency is None:
            raise ValueError("frequency_factor_id is not present in scenario")
        if frequency.unit != "events-per-year":
            raise ValueError("frequency factor unit must be events-per-year")
        if len(self.loss_factor_ids) != len(set(self.loss_factor_ids)):
            raise ValueError("loss_factor_ids must be unique")
        for factor_id in self.loss_factor_ids:
            factor = factor_map.get(factor_id)
            if factor is None:
                raise ValueError("loss factor is not present in scenario")
            if factor.unit != self.scenario.loss_unit:
                raise ValueError("loss factor unit must match scenario loss_unit")
        return self

    def frequency_factor(self) -> FactorRange:
        selected = self.frequency_factor_id
        return next(factor for factor in self.scenario.factors if factor.factor_id == selected)

    def loss_factors(self) -> tuple[FactorRange, ...]:
        selected = set(self.loss_factor_ids)
        return tuple(factor for factor in self.scenario.factors if factor.factor_id in selected)


class ExposureSummary(ModelRecord):
    """A range summary in the source scenario's explicitly declared unit."""

    unit: str = Field(min_length=1, max_length=64)
    sample_count: int = Field(ge=100)
    minimum: Decimal = Field(ge=0)
    p05: Decimal = Field(ge=0)
    p50: Decimal = Field(ge=0)
    p95: Decimal = Field(ge=0)
    maximum: Decimal = Field(ge=0)
    mean: Decimal = Field(ge=0)

    @model_validator(mode="after")
    def validate_order(self) -> ExposureSummary:
        if not self.minimum <= self.p05 <= self.p50 <= self.p95 <= self.maximum:
            raise ValueError("summary values must be ordered from minimum through maximum")
        return self


class InputSensitivity(ModelRecord):
    """One-at-a-time input-range width, not a causal or real-world importance claim."""

    factor_id: str = Field(pattern=ID_PATTERN)
    range_width: Decimal = Field(ge=0)
    unit: str = Field(min_length=1, max_length=64)
    interpretation: str = Field(min_length=1, max_length=240)


class ModelRun(ModelRecord):
    """Reproducibility record for a completed local synthetic run."""

    run_id: str = Field(pattern=ID_PATTERN)
    request_id: str = Field(pattern=ID_PATTERN)
    scenario_id: str = Field(pattern=ID_PATTERN)
    model_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    deterministic_seed: int = Field(ge=0)
    input_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    output_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    completeness_status: str = Field(pattern=r"^(complete|partial|insufficient)$")
    summary: ExposureSummary
    sensitivities: tuple[InputSensitivity, ...] = Field(min_length=1)
    limitations: str = Field(min_length=1, max_length=500)
