# Controlled Evidence Pilot & Frozen Reference (non-production)

A runnable, non-production project that combines three things:

1. a **real CI/CD pipeline** — unit tests → deterministic build → one Docker image shared by three isolated stages (dev / qa / staging) → live HTTP health gates → real artifact attestation;
2. a **controlled 19-case evidence matrix** — 16 runnable controlled cases (a fault is injected at the evidence layer, each variant decides independently) plus 3 real-data cases that stay **blocked** until original source records are supplied;
3. the **frozen reference** of the original experiment package — verifier, 107 baseline predicates, 16 mutation assertions, consistency checks — preserved byte-identical and verified on every run.

Fictional sample data only; no real business data; no credentials.

## What's inside

- `app/`, `tests/`, `tools/`, `infra/` — a tiny HTTP service, unit tests, build / stage-check / dispatch / finalize utilities, Dockerfile + compose (three stages share one image)
- `verifier/` — closure audit checker (**pilot implementation**, dual-timepoint: historical vs. audit)
- `scenarios/` — machine-readable definitions of the 19 cases and the case builder; the builder injects controlled faults and **refuses to fabricate** the 3 real-data cases
- `protocols/` — pre-registration run plan (48 controlled runs, to be filled with observed results)
- `frozen_reference/EvidenceClosure/` — the original frozen package (verifier, tests, schemas, policies, figures data, results), kept untouched; integrity is checked against its own S9 manifest
- `.github/workflows/`
  - **E2 19-Case Matrix** — the single active entry point: one workflow, inputs `scenario_id` × `variant (B0/B1/B2)` × `replicate_index`. B0 = modern gates; B1 = adds real GitHub artifact attestation (issue + verify + tamper must fail); B2 = adds the pilot closure checker. Expected-red scenarios (e.g. `B01`, `B02`) are intentional gate failures and are archived like any other run.
  - **Original Frozen Reference Reproduction** — smoke (107 tests + consistency check) / full (adds 16 targeted mutations) regression of the frozen package, kept strictly separate from pilot statistics.

## Local quickstart (Python 3.12+, no Docker required)

```bash
python tools/check_frozen_manifest.py                       # frozen package integrity (S9, 85 files)
python -m tools.run_frozen_regression --mode smoke --out runs/original_smoke
python -m unittest discover -s tests -v
python -m tools.e2_local_suite                              # all 16 controlled cases locally; ZH-* refuse to build
python -m scenarios.build_case --scenario A202 --out runs/try_A202
python -m verifier.closure_audit --input runs/try_A202/case.json \
        --output runs/try_A202/result.json --allow-open     # expect: OPEN / NFI
```

Batch dispatch prints a plan by default and executes nothing:

```bash
python -m tools.e2_dispatch --scenario ALL --variant ALL    # dry-run
```

## Notes (honesty first)

- `verifier/closure_audit.py` is a **pilot checker**, not a final validated implementation; its outputs are pilot results.
- The 3 real-data cases (`ZH-*`) require original source records; the builder fails closed rather than fabricating them.
- Controlled cases use scripted logical clocks; nothing here claims to be a production history.
- Frozen-reference results and pilot results are separate evidence lines and must not be merged into one statistic.
