# Threat Model

| Threat | Example | Mitigation/boundary |
|---|---|---|
| Non-reproducible result | A caller omits a seed or uses wall-clock state. | Seed and iteration count are required and recorded. |
| Unit confusion | A loss input is mixed with a frequency or real currency unit. | Request validation requires one events-per-year factor and loss factors matching scenario unit. |
| False precision | P50 is presented as a true loss estimate. | Summary always includes range percentiles and a limitation label; no decision API exists. |
| Input substitution | Inputs change after a run is reviewed. | Core canonical hashes bind the scenario and emitted run records input hash. |
| Data leakage | Customer evidence is embedded in a fixture. | Fixture uses a synthetic scenario and payload-blind Core references only. |
| Authority confusion | Output is treated as risk acceptance. | No approval action is exposed; downstream policy and authority validation are required. |
