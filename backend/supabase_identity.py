"""Server-confirmed identity boundary for the upcoming managed-auth integration.

No shared user client, client-provided owner ID, or service-role key is used.
This module does not switch the application's existing authentication provider.
"""
from dataclasses import dataclass
from uuid import UUID
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException


@dataclass(frozen=True)
class PrivateIdentity:
    subject: str
    email: str

    @property
    def owner_key(self) -> str:
        # Never link old local accounts by an email-address match.
        return "supabase:" + self.subject


class SupabaseIdentityVerifier:
    def __init__(self, url: str, publishable_key: str):
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or not parsed.hostname
                or parsed.username or parsed.password or parsed.query
                or parsed.fragment or parsed.path not in ("", "/")
                or parsed.port not in (None, 443)):
            raise ValueError("Supabase requires an HTTPS project origin.")
        if not publishable_key.startswith("sb_publishable_") or any(c.isspace() for c in publishable_key):
            raise ValueError("A Supabase publishable key is required, not a secret key.")
        self.url = url.rstrip("/")
        self.key = publishable_key

    def verify(self, authorization: str, *, transport=None) -> PrivateIdentity:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer" or len(parts[1]) > 16384:
            raise HTTPException(401, "Please sign in to continue.")
        try:
            # User lookup verifies the supplied token with the configured project.
            # No redirect forwarding, retries, or persistent cross-user session.
            with httpx.Client(timeout=10, follow_redirects=False, transport=transport) as client:
                response = client.get(self.url + "/auth/v1/user", headers={
                    "apikey": self.key, "Authorization": "Bearer " + parts[1],
                })
        except httpx.RequestError:
            raise HTTPException(503, "Authentication service is temporarily unavailable.") from None
        if response.status_code in (401, 403):
            raise HTTPException(401, "Please sign in again.")
        if response.status_code != 200:
            raise HTTPException(503, "Authentication service is temporarily unavailable.")
        try:
            user = response.json()
            subject = str(UUID(user["id"]))
            email = user["email"]
            if not isinstance(email, str) or not email or len(email) > 254:
                raise ValueError()
            if user.get("is_anonymous", False) or not user.get("email_confirmed_at"):
                raise HTTPException(403, "A verified private email account is required.")
        except (ValueError, KeyError, TypeError):
            raise HTTPException(503, "Authentication service returned an invalid identity.") from None
        return PrivateIdentity(subject=subject, email=email)
