import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  ClipboardCheck,
  Copy,
  FileText,
  LockKeyhole,
  MessageSquare,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import "./pilot.css";

const feedbackTemplate = `LexVigil pilot feedback

What I tried:
What worked well:
What was unclear or failed:
Document type (do not include confidential content):
Suggested improvement:
May LexVigil contact me about this feedback? Yes / No`;

export function PilotPage() {
  const [copied, setCopied] = useState(false);
  const templateRef = useRef<HTMLTextAreaElement>(null);

  async function copyTemplate() {
    try {
      await navigator.clipboard.writeText(feedbackTemplate);
      setCopied(true);
    } catch {
      const field = templateRef.current;
      field?.select();
      setCopied(document.execCommand("copy"));
    }
    window.setTimeout(() => setCopied(false), 2500);
  }

  return (
    <section className="pilot-page">
      <header className="pilot-heading">
        <div>
          <span className="overline">CONTROLLED PILOT</span>
          <h1>Use the evidence. Keep the judgment.</h1>
          <p>
            This early LexVigil demonstration helps you inspect text-based
            contracts. Treat every finding as a review prompt, not legal advice.
          </p>
        </div>
        <Link className="button primary" to="/app/contracts">
          Analyze a contract <ArrowRight size={17} />
        </Link>
      </header>

      <div className="pilot-layout">
        <div className="pilot-main">
          <section className="pilot-section" aria-labelledby="pilot-workflow">
            <div className="pilot-section-heading">
              <ClipboardCheck size={21} />
              <div>
                <h2 id="pilot-workflow">A focused pilot workflow</h2>
                <p>Use synthetic or non-sensitive, text-based material first.</p>
              </div>
            </div>
            <ol className="pilot-steps">
              <li>
                <span>01</span>
                <div>
                  <strong>Choose a text-based contract</strong>
                  <p>PDF, DOCX, TXT and Markdown files are supported up to 2 MB.</p>
                </div>
              </li>
              <li>
                <span>02</span>
                <div>
                  <strong>Inspect the evidence behind each finding</strong>
                  <p>Follow clauses, references, definitions and amendments before reaching a conclusion.</p>
                </div>
              </li>
              <li>
                <span>03</span>
                <div>
                  <strong>Save only reports you need</strong>
                  <p>Temporary analyses expire after 24 hours. You can export or delete a report at any time.</p>
                </div>
              </li>
            </ol>
          </section>

          <section className="pilot-section pilot-feedback" aria-labelledby="pilot-feedback">
            <div className="pilot-section-heading">
              <MessageSquare size={21} />
              <div>
                <h2 id="pilot-feedback">Share useful pilot feedback</h2>
                <p>Do not include contract text, personal data or other confidential information.</p>
              </div>
            </div>
            <textarea ref={templateRef} aria-label="Pilot feedback template" readOnly value={feedbackTemplate} />
            <div className="pilot-feedback-actions">
              <button className="button light" type="button" onClick={copyTemplate}>
                {copied ? <CheckCircle2 size={16} /> : <Copy size={16} />}
                {copied ? "Copied" : "Copy feedback template"}
              </button>
              <p role="status">
                Copy this template into your agreed pilot feedback channel.
              </p>
            </div>
          </section>
        </div>

        <aside className="pilot-rail" aria-label="Pilot scope and safeguards">
          <div className="pilot-rail-block">
            <ShieldCheck size={22} />
            <h2>What this pilot does</h2>
            <ul>
              <li>Rule-based contract analysis</li>
              <li>Clause, reference and amendment tracing</li>
              <li>Evidence-linked findings for human review</li>
              <li>Private personal workspaces</li>
            </ul>
          </div>
          <div className="pilot-rail-block muted-block">
            <Sparkles size={22} />
            <h2>Not enabled in this release</h2>
            <ul>
              <li>AI legal research or semantic review</li>
              <li>OCR for scanned documents</li>
              <li>Original-document storage</li>
              <li>Team sharing or law-firm workspaces</li>
            </ul>
          </div>
          <div className="pilot-rail-note">
            <LockKeyhole size={18} />
            <p>
              Uploaded bytes are processed in memory. Extracted report text follows the report lifecycle.
            </p>
          </div>
          <Link className="text-link" to="/app/history">
            Review my analyses <FileText size={15} />
          </Link>
        </aside>
      </div>
    </section>
  );
}
