# Approved sprint showcase

The user approved a reduced personal, non-commercial demonstration:
Google sign-in/private accounts; text-based contract ingestion; rule-based
analysis with evidence; saved reports, export and manual deletion.
Live AI research, semantic AI review and scanned-document OCR are deferred.
Original storage is conditional on verified hosted encryption and retention,
and is disabled in the initial showcase profile.

Set `LEXVIGIL_RELEASE_PROFILE=showcase` on the backend for this profile.
This is separate from `LEXVIGIL_ENV`; it does not weaken production settings
or bypass the Vercel startup guard. Invalid profile names fail startup.

The health response publishes the scope; the React provider defaults to
disabled optional features if that response is unavailable. Navigation,
deferred research routes, OCR/original-upload controls and semantic-review
controls honor this scope. Backend admission independently rejects deferred
research, semantic review, OCR and original-storage requests before creating
jobs. The development profile retains existing behavior.

Remaining deployment-critical work: restricted login provisioning; hosted
auth/report persistence; synchronous bounded text processing or verified
durable dispatch; account/global admission limits; report cleanup; Vercel
Mumbai runtime configuration; OAuth callbacks; live deployed workflow tests.
No deployment has been created by this scope-control change.

Remaining presentation checks include the full landing-page wording,
privacy copy, upload limits and browser verification in showcase mode.
Do not describe this limited release as completion of the full platform.
