# Authentication checkpoint — 2026-09-14

Implemented Google OAuth entry and server-side, single-use PKCE callbacks. Browser-bound flows expire after ten minutes. Provider tokens stay in HTTP-only cookies rather than browser storage. Added password recovery with an isolated recovery session; completing a password change invalidates existing LexVigil application sessions. This does not claim global revocation of every Supabase provider session.

Added generic signup messaging: successful registration responses do not prove email delivery or reveal whether an account already exists.

## Development configuration

- App: http://127.0.0.1:5173/login (keep this hostname consistent).
- Supabase project: mbnwdfdxksiuptwonjev (development only).
- Google Cloud authorized redirect remains https://mbnwdfdxksiuptwonjev.supabase.co/auth/v1/callback.
- Supabase Authentication → URL Configuration Site URL: http://127.0.0.1:5173.
- Supabase development redirect allowlist must cover http://127.0.0.1:5173/api/auth/google/callback** and http://127.0.0.1:5173/api/auth/recovery/callback**. These callbacks include a random flow query parameter. Do not use broad production-domain wildcards.
- Start the API with .env.supabase.development and --no-access-log. Reverse proxies must also avoid recording authentication callback queries. No Google client secret belongs in the frontend.

## Verification and open gates

- Backend: 89 tests passed, including callback expiry, replay, state/cookie mismatch and recovery isolation.
- Browser: five workflows passed, covering existing account/upload/report/save/export/delete/privacy flows and mocked Google/recovery interactions.
- TypeScript/Vite production build passed. Mobile recovery screenshot inspected; no horizontal overflow.
- Automated tests did not send recovery email or complete a real Google login. Hosted provider configuration is not equivalent to verified end-to-end login.
- User must complete a real Google login and verify the protected workspace, reload and sign-out. Live recovery email delivery and password update remain unverified.

## Phase 1 remains open

Next implementation: explicit original-document consent, owner-scoped temporary storage, a non-extending 48-hour expiry, manual deletion and cleanup tests; then original evidence viewing and OCR for English/Tamil/Hindi. Production also requires deployment-specific database/storage security, durable jobs, rate limiting, monitoring, backups, live provider and legal-quality evaluations. Passing this authentication checkpoint is not production approval.
