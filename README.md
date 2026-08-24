# Cyrisk Model

> **Deterministic range analysis for sealed Cyrisk scenarios—never a loss forecast or decision engine.**

`cyrisk-model` consumes a versioned `RiskScenario` from
[`cyrisk-core` v0.1.0](https://github.com/kingsokafor777-droid/cyrisk-core/releases/tag/v0.1.0)
and a supplied `AnalysisRequest`. It applies a documented seeded sampler to bounded factor ranges
and emits a reproducible **synthetic exposure-range analysis** with percentile summaries, manifest
hashes, and input-range sensitivity indicators.

## Scope boundary

The package is intentionally offline and local-first. It does not ingest a customer environment,
retrieve market/insurance data, calibrate against historical incidents, predict a breach, estimate
actual losses, calculate ROI, set risk tolerance, accept risk, recommend a purchase, or execute a
control change. The committed example is sealed synthetic data using `synthetic-usd`.

> The output is a reproducible transformation of supplied fictional inputs. It is **not** a
> financial forecast, actuarial estimate, audit result, investment recommendation, or decision.

## Analysis contract

| Input | Required property | Why it matters |
|---|---|---|
| `RiskScenario` | Versioned Core record and payload-blind evidence references. | Keeps the model separated from raw evidence and live systems. |
| `AnalysisRequest` | Explicit frequency factor, explicit loss factors, seed, and bounded iteration count. | Prevents semantic guessing and non-deterministic output. |
| `ExposureSummary` | Sample count, minimum, P05, P50, P95, maximum, and mean in a declared unit. | Prevents a single result from being treated as certain. |
| `InputSensitivity` | One-at-a-time synthetic input-range spread. | Explains model sensitivity, not real-world causal influence. |
| `ModelRun` | Scenario/input hashes, model version, seed, summary, and limitations. | Supports reproducibility and downstream review. |

## Method

For every iteration, the model samples the caller-selected frequency factor and loss factors from
their declared `triangular`, `uniform`, or PERT range. It multiplies the sampled frequency by the
sum of sampled loss factors, then derives nearest-rank percentiles over the synthetic sample set.
The seed, input hash, model version, and iteration count are part of the emitted run record.

The implementation is a **demonstration of range analysis**, not validation that distributions or
inputs are appropriate. NIST frames scenario, likelihood, impact, and risk-register information as
inputs to enterprise risk-management processes; those inputs do not replace organizational review.
[1] [2]

## Quick start

```bash
make bootstrap
make check
cyrisk-model analyze fixtures/synthetic_model_request.json
```

## Release controls

`make check` regenerates the sealed fixture, runs Ruff, strict mypy, branch-aware tests at a 95%
minimum, and verifies the wheel. Hosted CI tests Python 3.10–3.13 and CodeQL; workflows are pinned
to immutable action SHAs.

## References

[1]: https://csrc.nist.gov/pubs/ir/8286/r1/final "NISTIR 8286 Rev. 1"
[2]: https://csrc.nist.gov/pubs/ir/8286/a/r1/final "NISTIR 8286A Rev. 1"
