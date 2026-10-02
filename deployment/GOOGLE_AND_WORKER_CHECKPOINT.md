# Hosted acceptance checkpoint — 2026-09-24

- Google sign-in previously failed before app session creation. Supabase logs identified `invalid_client`: invalid Google client secret. User corrected provider credentials and confirmed successful login.
- Callback diagnostics log only fixed stages/status/boolean presence, never credentials, identities, query strings, or provider messages.
- User then reported sample analysis error on the authenticated preview.
- Browser connector could not initialize (Windows error 1058); no claim of browser verification.
- Worker environment sanitization omitted runtime-added Python import paths. Added resolved absolute parent interpreter paths to child PYTHONPATH, without copying raw PYTHONPATH or database credentials. Regression test covers runtime-only dependency and credential exclusion.
- Missing dependencies and memory limits now produce fixed diagnostic categories, not traceback or document contents.
- Hosted sample processing still requires user acceptance after preview update; do not mark deployment production-ready based on unit tests or health alone.
