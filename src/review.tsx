import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api, type Contract } from "./api";
import "./review.css";
export function SemanticReviewButton({
  id,
  reviewed,
}: {
  id: string;
  reviewed: boolean;
}) {
  const [configured, setConfigured] = useState(false),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const navigate = useNavigate();
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (consent) dialog.current?.showModal();
    else dialog.current?.close();
  }, [consent]);
  useEffect(() => {
    api("/health")
      .then((h) => setConfigured(h.ai_configured))
      .catch(() => {});
  }, []);
  async function run() {
    setBusy(true);
    try {
      const job = await api("/analyses/" + id + "/verify", { method: "POST" });
      navigate("/app/analyses/" + job.id);
      setConsent(false);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <button
        className="button light"
        disabled={!configured || reviewed}
        title={
          !configured ? "Configure the server API key to enable AI review" : ""
        }
        onClick={() => setConsent(true)}
      >
        {reviewed ? "AI reviewed" : "Request AI review"}
      </button>
      <dialog
        ref={dialog}
        className="review-consent"
        onCancel={() => setConsent(false)}
        aria-label="Send contract for AI review"
      >
        <h3>Send extracted contract text for AI review?</h3>
        <p>
          This optional step sends the extracted clauses to OpenAI. Up to three
          configured models may be used for uncertain assessments, incurring
          provider usage. A separate temporary report is created; the original
          is preserved.
        </p>
        <p>Only send material you are authorized to share with the provider.</p>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        <button className="button primary" disabled={busy} onClick={run}>
          {busy ? "Starting…" : "Consent and review"}
        </button>
        <button className="button light" onClick={() => setConsent(false)}>
          Cancel
        </button>
      </dialog>
    </>
  );
}
export function PrintContract({ report }: { report: Contract }) {
  return (
    <section className="print-report">
      <h2>Complete contract analysis</h2>
      <p>
        Analysis date: {report.as_of} · {report.clauses.length} clauses ·{" "}
        {report.findings.length} potential findings
      </p>
      <h2>Findings</h2>
      {report.findings.map((f) => (
        <article key={f.id}>
          <h3>
            {f.id}: {f.title} — {f.severity}
          </h3>
          <p>{f.explanation}</p>
          <p>
            Evidence:{" "}
            {f.evidence
              .map((id) => report.clauses.find((c) => c.id === id)?.label)
              .join(", ")}
          </p>
          {f.semantic && (
            <p>
              AI assessment: {f.semantic.verdict} — {f.semantic.explanation}
            </p>
          )}
        </article>
      ))}
      <h2>Original clauses</h2>
      {report.clauses.map((c) => (
        <article key={c.id}>
          <h3>
            § {c.label} {c.page ? "— Page " + c.page : ""}
          </h3>
          <pre>{c.text}</pre>
        </article>
      ))}
      <h2>Limitations</h2>
      {report.limitations.map((l) => (
        <p key={l}>{l}</p>
      ))}
      <p>Legal information only. Professional review required.</p>
    </section>
  );
}
