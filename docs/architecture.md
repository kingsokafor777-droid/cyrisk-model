# Architecture

`cyrisk-model` is a pure local calculation boundary. It accepts a validated Core scenario and an
explicit analysis request. It has no database client, cloud client, scheduler, network call, or
background process.

## Runtime flow

1. The caller provides a `RiskScenario` and an `AnalysisRequest` selecting factor IDs.
2. The request validates factor presence and compatible frequency/loss units.
3. A local `random.Random(seed)` samples the selected ranges for the declared count.
4. The model emits rounded synthetic samples, nearest-rank percentile summary, input-range
   sensitivity labels, canonical input hash, and a limitation statement.

## Failure rules

The model rejects unknown or duplicate factor IDs, a frequency factor whose unit is not
`events-per-year`, a loss factor whose unit differs from the scenario loss unit, non-synthetic
scenario examples, unbounded sample counts, and unsupported distribution declarations. It never
substitutes a missing input, chooses a seed, or falls back to a live source.

## Non-negotiable rules

- A model run summarizes fictional supplied inputs; it does not predict events or losses.
- Sensitivity is model-input sensitivity, not proof that a control or factor causes an outcome.
- An incomplete scenario must remain explicit through `completeness_status` and `limitations`.
- All outputs retain the scenario's declared unit and must not silently become currency claims.
