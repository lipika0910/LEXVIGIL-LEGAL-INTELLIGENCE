# Production candidate — 2026-09-22

Candidate: dpl_FuSPFCoPNwavpk7GEZcjcEbnRkze
URL: https://lexvigil-k4gpmcga8-rakesh-projects.vercel.app
Source commit: cd513a9 on codex/showcase-preview.
Built with --prod --skip-domain; no explicit promotion performed.
Vercel inspection reports READY, Python api/index 59.96 MB in bom1.
The platform also reports lexvigil-rakesh-projects.vercel.app as an alias;
do not describe this build as inaccessible, private or unaliased.

Approved production configuration is present: showcase profile, canonical
APP_ORIGIN https://lexvigil.vercel.app, selected Supabase URL/publishable key,
and three restricted runtime passwords. No administrator password transferred.
Preview and production share the user's chosen database.

Verified:
- 241 backend tests passed; three skipped; two dependency deprecation warnings.
- Candidate /api/health returns correct showcase settings.
- Google OAuth start writes its PKCE flow through the real hosted auth role.
- Supabase authorize redirects to accounts.google.com (302), without completing
  any account login. This does NOT prove its final redirect allowlist or callback.
- Existing preview JavaScript asset returns 200 application/javascript.
- Initial unintended deployment dpl_AJFEaWCdChHu8HcqVBCWERJ5akMP was deleted with
  explicit user approval; preserved preview health was verified afterward.

Public-domain promotion is held pending Supabase redirect configuration and
real Google account acceptance. Also unverified: authenticated hosted upload,
report/save/delete/export, Linux subprocess timeout and containment. No complete
production-readiness claim is justified yet. Auth callback inspection/config
is not available through the connected Supabase tool set in this session.

Required dashboard check: Site URL https://lexvigil.vercel.app; allow hosted
Google and recovery callback paths with their flow query parameter. Preserve
existing local and preview URLs. Current application routes are
/api/auth/google/callback and /api/auth/recovery/callback.

Builds run on Vercel's US build infrastructure. Application function runs in
Mumbai, Supabase project is Mumbai, AI is disabled. This is not a claim that all
platform metadata, logging, backups or build processing remains inside India.
