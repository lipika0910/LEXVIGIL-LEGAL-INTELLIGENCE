"""Minimal Supabase Auth REST adapter. No refresh tokens are retained."""
import httpx
from fastapi import HTTPException
from .supabase_identity import SupabaseIdentityVerifier


class ManagedAuth(SupabaseIdentityVerifier):
    def request_auth(self, method, path, body, access=None):
        headers = {"apikey": self.key}
        if access: headers["Authorization"] = "Bearer " + access
        try:
            with httpx.Client(timeout=15, follow_redirects=False) as client:
                response = client.request(method, self.url + "/auth/v1" + path, headers=headers, json=body)
        except httpx.RequestError:
            raise HTTPException(503, "Authentication service is temporarily unavailable.") from None
        if response.status_code == 429:
            raise HTTPException(429, "Too many attempts. Please try again later.")
        if response.status_code not in (200,201,204):
            raise HTTPException(400 if response.status_code < 500 else 503,
                "Authentication could not complete. Request a new link and try again.")
        if response.status_code == 204: return {}
        try:
            result = response.json()
            if not isinstance(result,dict): raise ValueError()
            return result
        except ValueError:
            raise HTTPException(503,"Authentication service returned an invalid response.") from None

    def send_recovery(self,email,callback,challenge):
        from urllib.parse import urlencode
        self.request_auth("POST","/recover?"+urlencode({"redirect_to":callback}),
            {"email":email,"code_challenge":challenge,"code_challenge_method":"s256"})

    def exchange_code(self,code,verifier):
        result=self.request_auth("POST","/token?grant_type=pkce",{"auth_code":code,"code_verifier":verifier})
        access,ttl=result.get("access_token"),result.get("expires_in")
        if not isinstance(access,str) or not access or len(access)>3800 or type(ttl) is not int or ttl<=30:
            raise HTTPException(503,"Authentication service returned an invalid session.")
        return self.verify("Bearer "+access),access,min(ttl-30,3600)

    def update_password(self,access,password):
        self.request_auth("PUT","/user",{"password":password},access)

    def credentials(self, action, email, password):
        path = "/signup" if action == "register" else "/token?grant_type=password"
        try:
            with httpx.Client(timeout=15, follow_redirects=False) as client:
                response = client.post(self.url + "/auth/v1" + path,
                    headers={"apikey": self.key}, json={"email": email, "password": password})
        except httpx.RequestError:
            raise HTTPException(503, "Authentication service is temporarily unavailable.") from None
        if response.status_code == 429:
            raise HTTPException(429, "Too many authentication attempts. Please try again later.")
        if response.status_code in (400, 401, 403, 422):
            raise HTTPException(400, "Authentication could not complete. Check your details and confirm your email before signing in.")
        if response.status_code not in (200, 201):
            raise HTTPException(503, "Authentication service is temporarily unavailable.")
        try:
            body = response.json()
            if not isinstance(body, dict):
                raise ValueError()
            access = body.get("access_token")
            if action == "register" and not access:
                return None
            ttl = body.get("expires_in")
            if not isinstance(access, str) or not access or len(access) > 3800:
                raise ValueError()
            if isinstance(ttl, bool) or not isinstance(ttl, int) or ttl <= 30:
                raise ValueError()
            identity = self.verify("Bearer " + access)
            return identity, access, min(ttl - 30, 3600)
        except (ValueError, TypeError):
            raise HTTPException(503, "Authentication service returned an invalid session.") from None

    def sign_out(self, access):
        if not access:
            return False
        try:
            with httpx.Client(timeout=10, follow_redirects=False) as client:
                response = client.post(self.url + "/auth/v1/logout?scope=local",
                    headers={"apikey": self.key, "Authorization": "Bearer " + access})
            return response.status_code in (200, 204, 401, 403)
        except httpx.RequestError:
            return False
