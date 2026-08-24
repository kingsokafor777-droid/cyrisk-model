# Contributing

Do not commit real incident data, customer evidence, real loss figures, market/insurance data,
credentials, live API dependencies, current timestamps, or unseeded randomness. Every new input
requires a unit, a stated interpretation, deterministic tests, and a limitation note.

Run `make check` before proposing a change. Do not reduce coverage or replace a reproducible
sample with a wall-clock, service, or provider dependency to make a test pass.
