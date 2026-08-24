"""Generate a sealed synthetic Cyrisk model request deterministically."""

from __future__ import annotations

from pathlib import Path

from cyrisk_core.models import RiskScenario

from cyrisk_model.models import AnalysisRequest

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "fixtures" / "synthetic_model_request.json"

SCENARIO = {
    "scenario_id": "scn-ransomware-payments",
    "title": "Synthetic ransomware event against payments API",
    "asset_id": "asset-payments-api",
    "threat_event": "Synthetic ransomware execution",
    "loss_unit": "synthetic-usd",
    "source_class": "synthetic",
    "factors": [
        {
            "factor_id": "frequency-range",
            "metric": "annual event frequency",
            "unit": "events-per-year",
            "distribution": "triangular",
            "lower": "0.1",
            "central": "0.3",
            "upper": "0.8",
            "source_class": "synthetic",
            "confidence": "low",
            "rationale": "Sealed synthetic fixture assumption.",
        },
        {
            "factor_id": "recovery-range",
            "metric": "recovery loss component",
            "unit": "synthetic-usd",
            "distribution": "pert",
            "lower": "10000",
            "central": "25000",
            "upper": "50000",
            "source_class": "synthetic",
            "confidence": "low",
            "rationale": "Sealed synthetic fixture assumption.",
        },
    ],
    "loss_components": [
        {
            "component_id": "loss-recovery",
            "label": "Synthetic recovery component",
            "unit": "synthetic-usd",
            "factor_ids": ["recovery-range"],
            "rationale": "Exercises linkage only.",
        }
    ],
    "evidence_references": [
        {
            "evidence_id": "evidence-synthetic-control-gap",
            "source_class": "synthetic",
            "integrity_hash": "7f9b8c2b4b452be484fe4ecf7f8d08ed6a9ca2f80d29c1238ccce47f4e2343a4",
            "description": "Synthetic payload-blind evidence reference.",
            "expires_on": "2099-12-31",
        }
    ],
    "completeness_note": "Synthetic fixture; no input is a real-world observation or forecast.",
}


def main() -> None:
    request = AnalysisRequest(
        request_id="request-ransomware-baseline",
        scenario=RiskScenario.model_validate(SCENARIO),
        frequency_factor_id="frequency-range",
        loss_factor_ids=("recovery-range",),
        deterministic_seed=20260823,
        sample_count=1000,
        completeness_status="partial",
        limitations=(
            "Synthetic demonstration only; no result is a forecast, real estimate, or decision."
        ),
    )
    TARGET.write_text(request.model_dump_json(indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
