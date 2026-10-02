# Controlled pilot foundation — 2026-10-02

## Implemented

- Authenticated showcase users have an in-app Pilot guide at `/app/pilot`.
- The guide describes the supported contract-review flow, evidence-first review,
  temporary-report lifecycle, manual deletion and human-review requirement.
- It explicitly lists deferred capabilities: AI legal research/semantic review,
  scanned-document OCR, original-document storage, team sharing and law-firm
  workspaces.
- A copyable feedback template is available locally in the browser. It contains
  a reminder not to include contract text, personal data or confidential
  information. The application does not transmit feedback or create a new data
  store; pilot feedback still needs an owner-approved channel.

## Verification

- `npm run build` passed.
- `npm run test:e2e` passed 9 tests; 1 managed-preview smoke test skipped by
  its existing environment guard. The test suite covered the Pilot guide,
  protected workspace, sample analysis, save/export/delete and responsive
  navigation against the isolated local server.

## Pilot entry criteria still open

1. A human verifies Google login, sample analysis, save, reopen, export,
   delete and logout on `https://lexvigil.vercel.app`.
2. The deployed source must be committed and pushed with a release identifier.
3. A feedback destination, pilot participant list, support owner, escalation
   route and privacy notice must be approved before inviting people.
4. Error monitoring and a rollback exercise need recorded evidence.

This is pilot preparation, not authorization to accept confidential legal
materials, operate as a law-practice service, or market legal advice.
