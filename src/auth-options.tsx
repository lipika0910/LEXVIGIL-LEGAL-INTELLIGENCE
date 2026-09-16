import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "./api";
import "./auth-options.css";

export function LoginOptions() {
  const [managed, setManaged] = useState<boolean | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    api("/auth/options")
      .then((r) => {
        if (active) setManaged(r.managed);
      })
      .catch((e) => { if (active) setError(e.message); });
    return () => {
      active = false;
    };
  }, [attempt]);
  if (managed === null) return (
    <div className="auth-options">
      <p role={error ? "alert" : undefined} aria-live="polite">{error || "Checking sign-in options…"}</p>
      {error && <button type="button" className="button" onClick={() => { setError(""); setAttempt(a => a + 1); }}>Retry connection</button>}
    </div>
  );
  if (!managed) return <p>Local test mode. Google login and password recovery require the Supabase-enabled server.</p>;
  return (
    <div className="auth-options">
      <button
        type="button"
        className="button"
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setError("");
          try {
            const result = await api("/auth/google/start", { method: "POST" });
            window.location.assign(result.url);
          } catch (e) {
            setError((e as Error).message);
            setBusy(false);
          }
        }}
      >
        {busy ? "Opening Google…" : "Continue with Google"}
      </button>
      <Link to="/forgot-password">Forgot password?</Link>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

export function RecoveryPage({ reset = false }: { reset?: boolean }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [ready, setReady] = useState(!reset);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    setReady(!reset);
    setError("");
    setMessage("");
    setPassword("");
    setConfirm("");
    if (!reset) return;
    let active = true;
    api("/auth/recovery/status")
      .then(() => {
        if (active) setReady(true);
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [reset]);
  return (
    <div className="auth-page">
      <Link to="/login" className="overline">
        LEXVIGIL · PRIVATE WORKSPACE
      </Link>
      <form
        className="auth-form recovery-form"
        onSubmit={async (e) => {
          e.preventDefault();
          setError("");
          setMessage("");
          if (reset && password !== confirm) {
            setError("Passwords do not match.");
            return;
          }
          setBusy(true);
          try {
            const result = await api(
              reset ? "/auth/recovery/password" : "/auth/recovery/start",
              {
                method: "POST",
                body: JSON.stringify(reset ? { password } : { email }),
              },
            );
            setPassword("");
            setConfirm("");
            if (reset) {
              window.location.assign("/login?password_updated=1");
              return;
            }
            setMessage(result.message);
          } catch (e) {
            setError((e as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <h1>{reset ? "Set a new password" : "Reset your password"}</h1>
        <p>
          {reset
            ? "Choose a password used only for LexVigil."
            : "Request a secure link. Open it in this same browser within 10 minutes."}
        </p>
        {reset ? (
          <>
            <label>
              New password
              <input
                type="password"
                autoComplete="new-password"
                minLength={12}
                maxLength={128}
                required
                disabled={!ready}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>
            <label>
              Confirm new password
              <input
                type="password"
                autoComplete="new-password"
                minLength={12}
                maxLength={128}
                required
                disabled={!ready}
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </label>
          </>
        ) : (
          <label>
            Email
            <input
              type="email"
              autoComplete="email"
              required
              maxLength={254}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
        )}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        {message && <p role="status">{message}</p>}
        <button className="button primary" disabled={busy || !ready}>
          {busy
            ? "Please wait…"
            : reset
              ? "Update password"
              : "Send reset link"}
        </button>
        {reset && <Link to="/forgot-password">Request a new reset link</Link>}
        <Link to="/login">Back to sign in</Link>
      </form>
    </div>
  );
}

export function AuthResultNotice() {
  const [message] = useState(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.has("auth_error") || window.location.hash.includes("error="))
      return "The sign-in or reset link could not be completed. It may be expired, already used, or opened in a different browser. Please start again.";
    if (params.get("password_updated") === "1")
      return "Password updated. Sign in with your new password.";
    return "";
  });
  useEffect(() => {
    if (window.location.hash || window.location.search)
      window.history.replaceState(null, "", "/login");
  }, []);
  return message ? <p role="status">{message}</p> : null;
}
