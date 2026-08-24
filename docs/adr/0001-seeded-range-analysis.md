# ADR 0001: Use seeded range analysis, not predictive scoring

**Status:** Accepted

## Decision

The first release performs seed-controlled sampling from supplied bounded ranges and reports
synthetic percentiles. It does not train, calibrate, forecast, or call an external data service.

## Rationale

This preserves reproducibility, makes scenario assumptions inspectable, and prevents a portfolio
demonstration from being represented as an actuarial or financial prediction system.

## Consequences

Real-world use would require organization-specific methodology, source governance, reviewer
authority, calibration policy, data protection, validation, and decision workflow outside this
source-release package.
