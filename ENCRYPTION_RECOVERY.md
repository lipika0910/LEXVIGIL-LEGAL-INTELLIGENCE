# Development original encryption and recovery

Original payloads use AES-256-GCM with a fresh random nonce and authenticated owner/document identity. The local SQLite adapter migrates version-0 original rows in one explicit transaction, verifies decrypted bytes against their existing hashes, and preserves ownership, filenames, consent and expiry timestamps. New original payloads are encrypted before insertion. Report text, filenames, metadata, historical database pages and backups are **not** encrypted by this payload migration.

## Key location and limitations

On this Windows development machine, the key is stored as a current-user Windows DPAPI-protected blob at `.runtime/original-key.dpapi`. The directory is ignored by Git. No key is printed in logs or exposed to the browser. Keep the same Windows user/profile and protect this machine. An attacker able to run code as that user may also be able to unlock the key. This is a development key-management arrangement, not a production KMS.

Never delete or regenerate that file while encrypted originals still exist. Missing keys and invalid ciphertext fail closed; no plaintext fallback is used. Startup checks existing encrypted rows with the selected key. `ORIGINAL_ENCRYPTION_KEY`, if set, overrides DPAPI and must be the correct base64-encoded 32-byte key. Do not set a new random override on an existing database.

## Recovery procedure

1. Stop both development services before restoring anything. Preserve the current database and protected key; do not run destructive reset commands.
2. If the protected key file was accidentally moved, restore the **exact original** file to `.runtime/original-key.dpapi` under the same Windows identity/profile. Restore a compatible database only from an approved backup, respecting deletion and expiry obligations.
3. Run `npm run dev`. Initialization verifies encrypted original hashes. If Windows cannot unlock the key, the wrong key is configured, or integrity checks fail, stop and investigate; do not replace the key or repeatedly rewrite data.
4. Confirm owner-authorized download/preview on an unexpired original. Expired or deleted originals must remain unavailable. Restoring old backups must never be used to bypass retention.

A copied DPAPI blob alone is **not a portable disaster-recovery backup**. Recovery after loss of the Windows profile/machine requires the relevant Windows recovery material or a separately provisioned, securely escrowed original key. No portable key export, external key escrow, or disaster-recovery backup has been configured in this step. If the key cannot be recovered, encrypted originals cannot be recovered; re-upload from an authorized source instead.

## Operational boundaries

This change does not provision production storage, change the original 48-hour maximum, encrypt saved report content, or implement durable jobs. PostgreSQL original storage remains disabled pending host/region, private storage, migrations, key management and backup policy decisions. Production needs separately managed keys, least-privilege access, key rotation and restore drills.

Verification includes tampering/wrong-owner/wrong-document/wrong-key rejection, Windows key reopen, missing-key refusal, migration rollback, unchanged expiry and existing download/preview/deletion regression tests.
