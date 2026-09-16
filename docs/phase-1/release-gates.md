# Execution order and release gates

## Build sequence

| Gate | Implementation package | Prerequisites | Exit evidence |
|---|---|---|---|
| G0 — Baseline | This Phase 1 package and decisions | User scope decisions | Approved baseline plus selected acceptance thresholds; no implied approval |
| G1 — Typed ingestion | Versioned domain/report schemas, document IDs/spans, fixture harness, parser hierarchy and upload safety | Confirmed Q01/Q02; Q05 limits and Q08 saved-original policy | Parser fixture assertions and honest extraction coverage |
| G2 — Reasoning core | References, nested terms, precedence/conditions, graph queries, normalized facts, six-pass engine, twelve categories | G1 | Per-class positive/negative tests with derivation provenance |
| G3 — Research and AI | Registry/adapters, passage verification, structured dispute/research, scoped AI and routing | G2 contracts, Q04/Q07/Q09, provider/source access | Mock fault tests AND separate live integration and legal-review evidence |
| G4 — Production engineering | Identity recovery, durable jobs, migrations, shared limits, retention and encryption | Approved retention/tenancy; start safe host-independent modules alongside G1–G3 | Multi-worker failure/recovery, access/deletion and PostgreSQL tests |
| G5 — Staging | Reproducible artifacts, chosen hosting, secrets, TLS, routing, email, monitoring and backups | Q06/Q10 and G3/G4 | Complete staging workflow, dependency readiness and restore/rollback evidence |
| G6 — Release acceptance | Held-out benchmark, browser/accessibility, load/fault/security and 14-step demo | G1–G5 | All approved acceptance records and no unresolved critical blocker |
| G7 — Pilot and launch | Controlled pilot, monitoring, operational ownership and final approval | G6 | Reviewed pilot findings and recorded release approval |

These are dependency gates, not promised calendar dates. Host-independent schema work can begin while product decisions are pending; storing/transmitting originals and provisioning paid infrastructure cannot be silently assumed.

## Benchmark plan

Use 30–60 controlled contracts from DOC §23, plus separate legal-research/dispute cases for every approved domain and language. Contract family, not merely file, is the split unit. Keep expected findings outside model inputs. Deduplicate near-identical variants across development and held-out sets.

Every category needs positive, negative and ambiguous examples. Include clean agreements, amendment replacement without contradiction, future amendments, nested definitions, valid exceptions, misdirected-but-existing references and scope/trigger mismatches. Supplied Sample Contract.md is seven concatenated synthetic examples with expected-answer commentary; split and remove labels before evaluation, then have a reviewer adjudicate them. Supplied expected text is not unquestionable ground truth.

Compare rule-only, LLM-only and hybrid on the same held-out inputs. Log pipeline version, model ID, configuration, date, time and cost. Mocked results are excluded from accuracy metrics.

## Measurement definitions and approvals

| Metric | Definition / guardrail | Target |
|---|---|---|
| Reference resolution | Correct target and scope / annotated resolvable references; report ambiguous and unresolved separately | Approve before held-out run |
| Clause extraction | Annotated clauses/spans recovered and extra/spurious clauses; stratify scanned/text/table layouts | Approve by language/layout |
| Conflict precision/recall/F1 | Match category and evidence relationship against adjudicated labels; per-class plus micro/macro; report ambiguous findings separately | Approve per category; no single aggregate hides a failed class |
| Source identity and claim support | Correct authority identity; separately count supported propositions among displayed legal propositions | Reviewer-defined targets and rejection policy |
| Unsupported legal claims | Unsupported / displayed material legal propositions; report severity and denominators | No invented claim may be knowingly accepted; empirical threshold requires reviewer approval |
| Latency | Queue delay and execution time separately; p50/p95 by workflow/document size/OCR status | Needs Q05/Q10 |
| Cost | Actual provider usage per logical job, including retries/escalation, not just first call | Needs budget Q05/Q09 |
| Recovery | Injected failure cases that recover correctly without duplicate publication/charges or data resurrection | All mandatory fault scenarios pass |
| Retention | Read denial at expiry and deletion completion against approved storage/backup policy | Needs Q02/Q08 |
| Restore | Measured data loss window and recovery time after restore rehearsal | RPO/RTO needs Q10 |

Do not tune on the held-out release set, invent thresholds after viewing results, or present 25 unit cases as a statistically established accuracy claim.

## Required failure drills

Provider outage/refusal/rate limit; malformed/large/scanned input; broken references; cyclic definitions; conflicting precedence; duplicate submission; worker death; two workers claiming one job; cancellation and deletion during a call; source unavailable/outdated; expired session; unauthorized original fetch; queue/database outage; backup restore; deployment rollback; full capacity.

## Release evidence record

For each requirement record: ID, acceptance scenario/version, input dataset/hash, environment, application revision or content manifest, execution time, command/run identifier, result/artifact, remaining risk, reviewer and approval. A test-file path alone is not release evidence.

Production release is blocked if any required row lacks accepted evidence, any mandatory decision is unresolved, or a critical security/legal-safety failure remains. Structural validator success alone never clears this gate.
