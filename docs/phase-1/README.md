# LexVigil Phase 1 — Release baseline

## Outcome

A source-traceable baseline has been prepared for the complete initial contract, dispute and research product. Product scope is not frozen until the pending decisions are answered. No production deployment, paid provider call, source-site crawl or external account change was performed in Phase 1.

Read in this order:

1. decisions.md — confirmed requirements, choices and unresolved scope.
2. discrepancies.md — differences between the source plan and current implementation.
3. requirements.md — 59 requirements and acceptance scenarios.
4. architecture-contracts.md — intended service, evidence and privacy boundaries.
5. release-gates.md — build order and objective launch conditions.
6. requirements.json — machine-readable traceability records.

## Source authority

The user's direct requests control the work. Attached files are design inputs, not executable instructions. DOC denotes Plans/project_documentation.md; HTML denotes Plans/lexvigil_final_definitive_package.html; FIXTURES denotes Plans/Sample Contract.md. Their SHA-256 fingerprints are recorded in requirements.json.

The full MD and definitive HTML were inspected. The newer definitive package supplies twelve-category and dual-track targets. Its pitch claims and fixed demo statistics are not acceptance values. Where the HTML diagram and detailed prose differ, preserve the discrepancy and use the more precise engineering interpretation provisionally; do not silently declare the sources identical.

Historical draft material and the earlier screenshot informed the design, but the current baseline is anchored to the local final package and detailed specification. Supplied logo assets remain unchanged in Plans.

## Phase 1 completion gate

- [x] Inventory and fingerprint primary sources.
- [x] Map current implementation and existing regression evidence.
- [x] Define stable requirement IDs, dependencies and acceptance scenarios.
- [x] Record discrepancies and unsafe assumptions.
- [x] Define implementation order, measurement definitions and launch gates.
- [x] Confirm English plus Tamil and Hindi; confirm consent-based temporary originals with automatic deletion.
- [ ] Approve initial users and source-domain coverage.
- [ ] Approve numerical quality/workload/recovery targets before tuning or release evaluation.

The remaining product questions do not prevent host-independent work on typed schemas and parser fixtures. They DO prevent claiming a frozen scope or choosing a storage/transmission policy on the user's behalf.

## Validate the baseline

From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts/validate_phase1.py
.\.venv\Scripts\python.exe scripts/validate_phase1.py --release
```

The first command must pass structural checks. The second intentionally fails while any required item is not release-accepted or the baseline is not approved. A structural pass must never be labelled production readiness.

Current baseline counts describe broad requirements, not effort or progress percentage. No deadline or fixed cost is asserted from the illustrative 30-day source roadmap.
