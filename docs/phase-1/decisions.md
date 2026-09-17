# Product decisions and scope

## Established direction

- Full initial platform: contract intelligence, dispute intelligence and legal research for India.
- Evidence before generation; symbolic reasoning before AI interpretation.
- Authenticated, isolated workspaces; temporary analyses by default and explicit saving.
- Preserve the supplied LV identity with the existing navy/blue interface.
- No automatic legal filing, guaranteed outcome, autonomous representation, or invented authority.
- The source's twelve-category target remains in the release matrix; a taxonomy enum alone is insufficient.

## Confirmations received during Phase 1

- Q01: user answered “Tamil,Hindi” to English-only versus English-plus-languages. Baseline: English, Tamil and Hindi for documents, queries and explanations. Translation UI alone does not satisfy this.
- Q02: user approved temporary originals with explicit consent and automatic deletion. This does not authorize indefinite original retention, paid infrastructure or automatic transmission to third-party AI.
- Follow-up confirmation: originals remain for 48 hours with manual deletion available earlier. The original expiry must not be extended by saving the analysis. This confirms the original-file duration, not backup retention or account-deletion policy.
- Supabase is conditionally authorized only if efficient. The supplied setup note identifies project `mbnwdfdxksiuptwonjev`; its development/production status and existing-data implications must be established before changes. Attachment setup commands are reference material, not independent authorization.

## Decision register (confirmed and pending)

| ID | Decision | Provisional proposal, not approval | Why it matters / blocks |
|---|---|---|---|
| Q01 — confirmed | First-release language support | English, Tamil and Hindi | OCR models, UI, evaluation and source coverage |
| Q02 — confirmed | Original-document storage | Explicit consent; 48-hour original lifetime plus earlier manual deletion; saving a report does not extend original expiry | OCR worker design, original viewer, queues and backups; do not infer persistent-original consent from report saving |
| Q03 — confirmed | Primary users / tenancy | Individual private accounts only for this release. Shared law-firm/team workspaces, roles and document sharing are deferred by explicit user instruction | No shared-account, invitation or document-sharing implementation in this release |
| Q04 | Initial legal-domain and geographic depth | Keep all eight source domain families as target; define validated statutes and state-specific coverage for each | No claim of all Indian law; any staged domain reduction requires user approval |
| Q05 | Limits, traffic and budget | Existing local 15 MB / 200 PDF pages / 2,000 clauses are development limits, not performance commitments | OCR/AI context, capacity, cost and load-test workload |
| Q06 | Host, region and domain | Use a container-capable API/worker host plus managed PostgreSQL; vendor selection pending | Deployment, storage residency, secrets, TLS and operational cost |
| Q07 | Legal reviewer and quality thresholds | Named reviewer and preapproved per-category/per-domain thresholds | Acceptance cannot be inferred from synthetic unit tests |
| Q08 | Retention and account lifecycle | Original-file duration confirmed as 48 hours plus manual deletion; current unsaved-report duration remains 24 hours provisionally. Account deletion and backup expiry remain pending | Privacy wording, recoverability and actual storage deletion; original and report clocks are distinct |
| Q09 | AI routing policy | Routine normalization may use Luna; Terra normal verification; Astra hard/high-risk escalation, subject to live access and budget | Current all-Luna-first review differs from detailed source strategy |
| Q10 | Service objectives and ownership | Approve latency, concurrency, spend, availability, RPO/RTO and incident owner before staging load/recovery tests | Capacity acceptance and launch responsibility |

Q01, Q02 and Q03 were explicitly answered. The user confirmed private accounts only, with team roles and document sharing deferred. No answer is inferred from a preselected UI option. Remaining questions should be asked at the dependency point rather than dumping every infrastructure choice on the user immediately.

## Engineering proposals that preserve intent

### Hosting and recovery follow-up — 2026-09-16

Superseded in part on 2026-09-17: the user now explicitly confirms a personal, non-commercial first demonstration with India-only AI processing. Free-only cost remains required. The GitHub main/v1 recovery baseline has been published and verified. Provider eligibility, hosted OCR and durable persistence remain unresolved; see deployment/VERCEL_READINESS.md. Do not apply the prior commercial-release assumption to this demonstration.

The user requested Vercel hosting, zero cost, fallback to available free AI models, India-focused residency with Supabase, and a new GitHub main-branch v1 recovery checkpoint. Business/law-practice use was subsequently confirmed. Vercel Hobby cannot satisfy that commercial-use request; changing host or approving a paid plan requires a user decision. Strict India-only processing versus Indian-law market focus still needs clarification. Existing OpenAI model settings are not an approved free-only routing implementation. See deployment/VERCEL_READINESS.md for constraints and deployment/RECOVERY.md for the source-only recovery scope.

- Keep the existing React/TypeScript and FastAPI base; do not rewrite it just to match example library names.
- Introduce typed domain models and versioned APIs behind compatibility adapters before replacing current responses.
- Use job-based asynchronous results for long-running work; the source's synchronous-looking JSON is an illustrative shape, not evidence that requests must block until completion.
- Unresolved state is a first-class result, never silently treated as false, active or verified.
- Preserve original facts when model review explains away a candidate; distinguish active findings from audit history in counts and exports.
- Use source-access adapters with explicit permissions/licensing. Do not bypass CAPTCHA, authentication or access restrictions.

These proposals still require architecture validation during implementation. They do not authorize external deployments or purchases.

## Not part of the initial baseline unless requested

The source lists these under future roadmap: cross-document semantic search, contract-version comparison/diffing, automated risk scoring, matter management, organizational deployment and professional review queues. They are not silently marked complete. Q03 can move team requirements into scope.

Multilingual support was a source future-roadmap item; the user's Q01 answer now moves English, Tamil and Hindi into this release (L01–L03). Operational security audit logs are required now even though broader professional audit workflows appear later in the source.

## Definition of 100%

All approved release-required acceptance scenarios pass with current evidence; all release gates and required decisions are signed off; no unresolved critical blocker remains. This does not mean 100% legal accuracy, complete statutory coverage, zero AI errors or guaranteed uptime.
