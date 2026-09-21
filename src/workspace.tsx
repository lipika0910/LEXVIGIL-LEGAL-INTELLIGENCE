import { useEffect, useState } from "react";
import { useReleaseScope } from './release-scope';
import { SemanticReviewButton, PrintContract } from "./review";
import { OriginalFile } from "./original";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  ArrowRight,
  ArrowUpRight,
  Upload,
  FileText,
  ShieldCheck,
  Search,
  Check,
  Clock,
  Download,
  Trash2,
  Bookmark,
  ChevronRight,
  Link2,
  AlertTriangle,
  LoaderCircle,
  BookOpen,
} from "lucide-react";
import {
  api,
  type Job,
  type Contract,
  type Research,
  type Finding,
} from "./api";

export function ContractPage() {
  const scope = useReleaseScope();
  const uploadLimitMB = scope.profile === 'development' ? 15 : 2;
  const [storeOriginal, setStoreOriginal] = useState(false);
  const [ocrLanguage, setOcrLanguage] = useState('');
  const [ocrReady, setOcrReady] = useState(false);
  useEffect(() => {
    let active=true;
    api('/ocr/options').then(r=>{if(active)setOcrReady(r.available);}).catch(()=>{});
    return ()=>{active=false;};
  },[]);
  const [file, setFile] = useState<File | null>(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [asOf, setAsOf] = useState(new Date().toLocaleDateString("en-CA"));
  const navigate = useNavigate();
  async function submit(sample = false) {
    if (!sample && !file) return;
    if (!sample && file && (file.size === 0 || file.size > uploadLimitMB * 1024 * 1024)) {
      setError(`Choose a nonempty document up to ${uploadLimitMB} MB.`);
      return;
    }
    setBusy(true);
    setError("");
    try {
      const form = new FormData();
      if (file) form.append("file", file);
      form.append("as_of", asOf);
      form.append("store_original", String(scope.original_storage && storeOriginal));
      form.append("ocr_language", scope.ocr ? ocrLanguage : '');
      const job = await api(
        sample ? "/contracts/sample" : "/contracts/analyze",
        { method: "POST", ...(sample ? {} : { body: form }) },
      );
      navigate("/app/analyses/" + job.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">CONTRACT INTELLIGENCE</span>
          <h1>Read between the references.</h1>
          <p>
            Upload a contract to explore its clauses, dependencies, and
            potential inconsistencies.
          </p>
        </div>
        <span className="outline-label">
          <ShieldCheck size={15} /> Temporary by default
        </span>
      </div>
      <div className="intake-layout">
        <section className="intake-panel">
          <div className="panel-title">
            <span className="number-circle">01</span>
            <h2>Add your contract</h2>
          </div>
          <label
            className={"upload-zone " + (file ? "has-file" : "")}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              setFile(e.dataTransfer.files[0] || null);
              setStoreOriginal(false);
            }}
          >
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md"
              aria-label="Choose contract file"
              onChange={(e) => { setFile(e.target.files?.[0] || null); setStoreOriginal(false); }}
            />
            <span className="upload-icon">
              <Upload size={28} />
            </span>
            <h3>{file ? file.name : "Drop your contract here"}</h3>
            <p>
              {file
                ? `${(file.size / 1024).toFixed(0)} KB · Click to choose another file`
                : "or browse files on your device"}
            </p>
            <span className="file-formats">
              PDF · DOCX · TXT · MD <span>Up to {uploadLimitMB} MB · 200 PDF pages</span>
            </span>
          </label>
          {scope.profile === 'showcase' && <p>
            Text-based documents only. This demonstration uses rule-based analysis,
            not AI legal advice. OCR and original-file storage are not enabled.
            Up to 10 reports per account; delete an old report when capacity is reached.
          </p>}
          <div className="intake-options">
            <label>
              Analyze as of
              <input
                type="date"
                value={asOf}
                onChange={(e) => setAsOf(e.target.value)}
                required
              />
            </label>
            <p>
              Future-dated amendments remain inactive until their effective
              date.
            </p>
          </div>
          {scope.ocr && <label className="original-consent">
            <span>Scanned PDF OCR (local processing)
              <select aria-label="Scanned PDF OCR language" value={ocrLanguage} disabled={!ocrReady} onChange={e=>setOcrLanguage(e.target.value)}>
                <option value="">Off — text PDFs only</option>
                <option value="eng">English</option><option value="tam">Tamil</option><option value="hin">Hindi</option><option value="eng+tam+hin">English + Tamil + Hindi</option>
              </select>
              <small>{ocrReady ? 'Up to 20 scanned pages, 30 seconds per page. Recognized text requires review. Pages with an existing text layer keep that layer; images on those pages are not separately read.' : 'OCR runtime is unavailable or could not be checked.'}</small>
            </span>
          </label>}
          {scope.original_storage && <label className="original-consent">
            <input type="checkbox" checked={storeOriginal} onChange={e => setStoreOriginal(e.target.checked)} />
            I consent to private temporary storage of this original for up to 48 hours, with earlier manual deletion. Saving the report does not extend this time. Deleting the report or signing out of an unsaved report removes it earlier. This does not authorize sending it to an AI provider.
          </label>}
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <button
            className="button primary full"
            disabled={!file || busy || !asOf}
            onClick={() => submit()}
          >
            {busy ? (
              <LoaderCircle className="spin" size={18} />
            ) : (
              <Search size={18} />
            )}
            Analyze contract
            <ArrowRight size={18} />
          </button>
          <p className="privacy-caption">
            <ShieldCheck size={14} /> Without consent, original bytes are processed in memory only. Extracted text follows report retention. Deletion does not remove downloaded copies or historical backups.
          </p>
        </section>
        <aside className="intake-guide">
          <span className="overline">A CLEARER REVIEW</span>
          <h2>
            Follow the evidence.
            <br />
            See the full context.
          </h2>
          <div className="guide-steps">
            {[
              [
                "Document structure",
                "Numbered clauses and their original text.",
              ],
              [
                "Connected references",
                "Definitions, term usage and amendment links.",
              ],
              [
                "Potential findings",
                "Inspect the source text behind every candidate.",
              ],
            ].map(([a, b], i) => (
              <div key={a}>
                <span>0{i + 1}</span>
                <div>
                  <h3>{a}</h3>
                  <p>{b}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="sample-panel">
            <BookOpen size={21} />
            <h3>Take a closer look</h3>
            <p>
              Try a synthetic services agreement with a payment-period
              amendment.
            </p>
            <button
              className="text-link"
              disabled={busy}
              onClick={() => submit(true)}
            >
              Analyze sample contract <ArrowUpRight size={16} />
            </button>
          </div>
          <p className="muted small">
            Scanned PDFs require OCR before upload. Current pattern coverage is
            disclosed in every report.
          </p>
        </aside>
      </div>
    </>
  );
}

export function ResearchPage({ kind }: { kind: "disputes" | "research" }) {
  const [description, setDescription] = useState(""),
    [state, setState] = useState(""),
    [district, setDistrict] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [configured, setConfigured] = useState<boolean | null>(null);
  const navigate = useNavigate();
  useEffect(() => {
    api("/health")
      .then((h) => setConfigured(h.ai_configured))
      .catch(() => setConfigured(false));
  }, []);
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">
            {kind === "disputes"
              ? "DISPUTE INTELLIGENCE"
              : "OFFICIAL-SOURCE RESEARCH"}
          </span>
          <h1>
            {kind === "disputes"
              ? "Start with what happened."
              : "A better question. A clearer source."}
          </h1>
          <p>
            {kind === "disputes"
              ? "Organize the facts and explore the legal questions they raise."
              : "Research Indian legal questions with links to retrieved official material."}
          </p>
        </div>
      </div>
      <div className="intake-layout">
        <form
          className="intake-panel research-form"
          onSubmit={async (e) => {
            e.preventDefault();
            setBusy(true);
            setError("");
            try {
              const job = await api("/" + kind + "/analyze", {
                method: "POST",
                body: JSON.stringify({ description, state, district }),
              });
              navigate("/app/analyses/" + job.id);
            } catch (e) {
              setError((e as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <label>
            {kind === "disputes"
              ? "Describe your situation"
              : "Your research question"}
            <textarea
              required
              minLength={20}
              maxLength={12000}
              rows={9}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder={
                kind === "disputes"
                  ? "What happened? Who was involved? Include relevant dates and the questions you need to understand."
                  : "For example: How do courts interpret a force majeure clause when the agreement specifies the triggering events?"
              }
            />
          </label>
          <div className="two-fields">
            <label>
              State (optional)
              <input
                value={state}
                onChange={(e) => setState(e.target.value)}
                placeholder="e.g. Tamil Nadu"
                maxLength={100}
              />
            </label>
            <label>
              District (optional)
              <input
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                placeholder="e.g. Chennai"
                maxLength={100}
              />
            </label>
          </div>
          <p className="small muted">
            Jurisdiction depends on the facts and applicable law, not location
            alone.
          </p>
          {configured === false && (
            <div className="notice">
              <AlertTriangle size={18} />
              <span>
                <strong>Live research awaits configuration</strong>
                <br />
                The server needs an OpenAI API key before it can retrieve
                sources and produce this report.
              </span>
            </div>
          )}
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <button
            className="button primary full"
            disabled={busy || configured !== true}
          >
            {busy
              ? "Starting research…"
              : kind === "disputes"
                ? "Explore this dispute"
                : "Research official sources"}
            <ArrowRight size={18} />
          </button>
        </form>
        <aside className="intake-guide">
          <span className="overline">RESEARCH WITH CONTEXT</span>
          <h2>
            Sources you can open.
            <br />
            Limits you can see.
          </h2>
          <div className="guide-steps">
            {[
              [
                "Your stated facts",
                "Keep assumptions separate from what you know.",
              ],
              [
                "Official material",
                "Research legislation and court repositories.",
              ],
              [
                "Questions that remain",
                "See missing facts and the limits of the evidence.",
              ],
            ].map(([a, b], i) => (
              <div key={a}>
                <span>0{i + 1}</span>
                <div>
                  <h3>{a}</h3>
                  <p>{b}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="sample-panel">
            <ShieldCheck size={22} />
            <h3>Keep sensitive details minimal</h3>
            <p>
              Provide the facts needed for your question. Avoid unnecessary
              personal identifiers. Live research sends your description to the
              configured AI provider.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}

export function HistoryPage() {
  const [jobs, setJobs] = useState<Job[]>([]),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(true),
    [filter, setFilter] = useState("all"),
    [query, setQuery] = useState("");
  useEffect(() => {
    api<Job[]>("/analyses")
      .then(setJobs)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);
  const rows = jobs.filter(
    (j) =>
      (filter === "all" || !!j.saved) &&
      j.title.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="overline">YOUR WORKSPACE</span>
          <h1>My analyses</h1>
          <p>Return to your evidence, or start with a new question.</p>
        </div>
        <Link to="/app/contracts" className="button primary">
          New analysis <ArrowRight size={16} />
        </Link>
      </div>
      <section className="history-panel">
        <div className="table-toolbar">
          <div className="tabs">
            <button
              className={filter === "all" ? "active" : ""}
              onClick={() => setFilter("all")}
            >
              All analyses
            </button>
            <button
              className={filter === "saved" ? "active" : ""}
              onClick={() => setFilter("saved")}
            >
              Saved
            </button>
          </div>
          <label className="search-field">
            <Search size={16} />
            <input
              aria-label="Search analyses"
              placeholder="Search analyses"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </label>
        </div>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
        {loading ? (
          <div className="empty">
            <LoaderCircle className="spin" />
            Loading analyses…
          </div>
        ) : rows.length ? (
          <div className="history-list">
            {rows.map((j) => (
              <Link
                key={j.id}
                className="history-row"
                to={"/app/analyses/" + j.id}
              >
                <span className="document-icon">
                  <FileText />
                </span>
                <div>
                  <h3>{j.title}</h3>
                  <p>
                    {j.kind === "contract"
                      ? "Contract analysis"
                      : j.kind === "disputes"
                        ? "Dispute analysis"
                        : "Legal research"}{" "}
                    · {new Date(j.created * 1000).toLocaleDateString()}
                  </p>
                </div>
                <span className={"tag " + (j.saved ? "teal" : "")}>
                  {j.saved ? "SAVED" : "TEMPORARY"}
                </span>
                <span className="job-status">{j.status}</span>
                <ChevronRight size={18} />
              </Link>
            ))}
          </div>
        ) : (
          <div className="empty">
            <FolderIcon />
            <h2>
              {query ? "No matching analyses" : "Room for your next insight"}
            </h2>
            <p>
              {query
                ? "Try another search."
                : "Your analyses appear here after you upload a contract or research a question."}
            </p>
            <Link to="/app/contracts" className="text-link">
              Analyze a contract <ArrowRight size={16} />
            </Link>
          </div>
        )}
      </section>
    </>
  );
}
function FolderIcon() {
  return <BookOpen size={32} />;
}

export function ReportPage() {
  const scope = useReleaseScope();
  const { id } = useParams();
  const [job, setJob] = useState<Job | null>(null),
    [error, setError] = useState(""),
    [action, setAction] = useState(false),
    [confirmDelete, setConfirmDelete] = useState(false);
  const navigate = useNavigate();
  useEffect(() => {
    let disposed = false;
    let timer: ReturnType<typeof setTimeout>;
    setJob(null);
    setError("");
    async function poll() {
      try {
        const result = await api<Job>("/analyses/" + id);
        if (disposed) return;
        setJob(result);
        if (["queued", "processing"].includes(result.status))
          timer = setTimeout(poll, 1200);
      } catch (e) {
        if (!disposed) setError((e as Error).message);
      }
    }
    poll();
    return () => {
      disposed = true;
      clearTimeout(timer);
    };
  }, [id]);
  async function save() {
    setAction(true);
    try {
      await api("/analyses/" + id + "/save", { method: "POST" });
      setJob((j) => (j ? { ...j, saved: 1 } : j));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setAction(false);
    }
  }
  async function remove() {
    setAction(true);
    try {
      await api("/analyses/" + id, { method: "DELETE" });
      navigate("/app/history");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setAction(false);
    }
  }
  function download() {
    if (!job?.result) return;
    const blob = new Blob(
      [
        JSON.stringify(
          {
            title: job.title,
            generated_at: new Date(job.created * 1000).toISOString(),
            report: job.result,
          },
          null,
          2,
        ),
      ],
      { type: "application/json" },
    );
    const url = URL.createObjectURL(blob),
      a = document.createElement("a");
    a.href = url;
    a.download = "lexvigil-" + id + ".json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }
  return (
    <>
      <Link className="back-link" to="/app/history">
        My analyses <ChevronRight size={14} /> Report
      </Link>
      <div className="report-heading">
        <div>
          <h1>{job?.title || "Opening analysis…"}</h1>
          <p>
            <span className="status-dot online" />
            {job?.status || "Loading"} <span>·</span>{" "}
            {job?.saved
              ? "Saved to your workspace"
              : "Temporary · expires after 24 hours"}
          </p>
        </div>
        <div className="actions no-print">
          {scope.semantic_review && job?.result?.kind === "contract" && (
            <SemanticReviewButton
              id={id!}
              reviewed={job.result.verification === "AI_REVIEWED"}
            />
          )}
          <button
            className="button light"
            disabled={!job?.result || !!job.saved || action}
            onClick={save}
          >
            {job?.saved ? <Check size={16} /> : <Bookmark size={16} />}{" "}
            {job?.saved ? "Saved" : "Save analysis"}
          </button>
          <button
            className="button light"
            disabled={!job?.result}
            onClick={download}
          >
            <Download size={16} />
            Export JSON
          </button>
          <button
            className="button light"
            disabled={!job?.result}
            onClick={() => window.print()}
          >
            Print / PDF
          </button>
          <button
            className="icon-button danger"
            aria-label="Delete analysis"
            disabled={!job || action}
            onClick={() => setConfirmDelete(true)}
          >
            <Trash2 size={17} />
          </button>
        </div>
      </div>
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}
      {confirmDelete && (
        <div
          className="confirm-delete"
          role="alertdialog"
          aria-label="Delete this analysis?"
        >
          <strong>Delete this analysis and its extracted text?</strong>
          <p>
            This removes the report from your workspace. Export it first if you
            need a copy.
          </p>
          <button
            className="button danger-solid"
            disabled={action}
            onClick={remove}
          >
            Delete analysis
          </button>
          <button
            className="button light"
            onClick={() => setConfirmDelete(false)}
          >
            Keep analysis
          </button>
        </div>
      )}
      {scope.original_storage && job?.kind === "contract" && <OriginalFile key={job.id} id={job.id} report={job.result ? job.result as Contract : undefined} />}
      {job?.status === "failed" ? (
        <div className="empty">
          <AlertTriangle />
          <h2>Analysis needs attention</h2>
          <p>{job.error}</p>
          <Link
            className="button primary"
            to={job.kind === "contract" ? "/app/contracts" : "/app/" + job.kind}
          >
            Try again
          </Link>
        </div>
      ) : job?.result ? (
        job.result.kind === "contract" ? (
          <>
            <div className="screen-report">
              <ContractReport report={job.result as Contract} />
            </div>
            <PrintContract report={job.result as Contract} />
          </>
        ) : (
          <ResearchReport report={job.result as Research} />
        )
      ) : (
        !error && (
          <div className="processing">
            <LoaderCircle className="spin" size={36} />
            <h2>Following the evidence…</h2>
            {job?.kind === "contract" && job.processing && (
              <p role="status">
                {job.processing.durable
                  ? `Restart recovery enabled. Processing attempt ${job.processing.attempts || 0} of 3. Recovery requires an available original and report; their expiry times do not change.`
                  : "Memory-only processing. If the server restarts, upload the document again."}
              </p>
            )}
            <p>
              The analysis runs on the server. You can return to this page while
              it completes.
            </p>
            <div>
              <Clock size={16} />{" "}
              {job?.status === "queued"
                ? "Waiting for an available worker"
                : "Processing your input"}
            </div>
          </div>
        )
      )}
    </>
  );
}

function ContractReport({ report }: { report: Contract }) {
  const [selected, setSelected] = useState(report.findings[0]?.id || ""),
    [tab, setTab] = useState("findings"),
    [query, setQuery] = useState(""),
    [severity, setSeverity] = useState("all");
  const finding = report.findings.find((f) => f.id === selected);
  const filtered = report.findings.filter(
    (f) =>
      (severity === "all" || f.severity === severity) &&
      (f.title + " " + f.category).toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <div className="stats-strip">
        {[
          ["Clauses", "clauses"],
          ["References resolved", "resolved"],
          ["Defined terms", "definitions"],
          ["Amendments", "amendments"],
          ["Potential findings", "conflicts"],
        ].map(([label, key]) => (
          <div key={key}>
            <b>{report.summary[key]}</b>
            <span>{label}</span>
          </div>
        ))}
      </div>
      <div className="report-tabs tabs">
        <button
          className={tab === "findings" ? "active" : ""}
          onClick={() => setTab("findings")}
        >
          Findings <span>{report.findings.length}</span>
        </button>
        <button
          className={tab === "clauses" ? "active" : ""}
          onClick={() => setTab("clauses")}
        >
          Source clauses
        </button>
        <button
          className={tab === "graph" ? "active" : ""}
          onClick={() => setTab("graph")}
        >
          References & terms
        </button>
        <button
          className={tab === "coverage" ? "active" : ""}
          onClick={() => setTab("coverage")}
        >
          Coverage & limitations
        </button>
      </div>
      {tab === "findings" ? (
        <div className="findings-workbench">
          <aside className="findings-rail">
            <div className="rail-heading">
              <h2>Potential findings</h2>
              <span>{report.findings.length}</span>
            </div>
            <label className="search-field">
              <Search size={15} />
              <input
                placeholder="Search findings"
                aria-label="Search findings"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </label>
            <select
              aria-label="Filter by severity"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            >
              <option value="all">All severities</option>
              <option>HIGH</option>
              <option>MEDIUM</option>
              <option>LOW</option>
            </select>
            {filtered.map((f) => (
              <button
                className={
                  "finding-row " + (selected === f.id ? "selected" : "")
                }
                key={f.id}
                onClick={() => setSelected(f.id)}
              >
                <span className="finding-row-top">
                  <small>{f.id}</small>
                  <span className={"severity " + f.severity.toLowerCase()}>
                    {f.severity}
                  </span>
                </span>
                <strong>{f.title}</strong>
                <span>
                  {f.category} <span>·</span> {f.evidence.length} source clauses
                </span>
              </button>
            ))}
            {!filtered.length && (
              <p className="muted small">No findings match this view.</p>
            )}
            <div className="rail-note">
              <ShieldCheck size={17} />
              <p>
                Every candidate links to its source. Review the surrounding
                context.
              </p>
            </div>
          </aside>
          <div className="finding-detail">
            {finding ? (
              <FindingDetail finding={finding} report={report} />
            ) : (
              <div className="empty">
                <Check size={30} />
                <h2>No candidates detected</h2>
                <p>
                  The current patterns found no candidates. This does not
                  certify that the contract is free of conflicts. Review
                  coverage and original clauses.
                </p>
                <button
                  className="button light"
                  onClick={() => setTab("coverage")}
                >
                  View coverage
                </button>
              </div>
            )}
          </div>
        </div>
      ) : tab === "clauses" ? (
        <section className="source-list">
          {report.clauses.map((c) => (
            <article key={c.id} id={c.id}>
              <span className="clause-label">§ {c.label}</span>
              <div>
                <h3>{c.title}</h3>
                <pre>{c.text}</pre>
                <small>
                  {c.page
                    ? `Original PDF · Page ${c.page}${c.page_end && c.page_end !== c.page ? "–" + c.page_end : ""}`
                    : "Original text · clause location"}
                </small>
              </div>
            </article>
          ))}
        </section>
      ) : tab === "graph" ? (
        <section className="graph-view">
          <h2>Defined terms & effective values</h2>
          {report.definitions.length ? (
            report.definitions.map((d, i) => (
              <div className="definition-row" key={i}>
                <strong>{d.term}</strong>
                <span>{d.value}</span>
                <ArrowRight size={16} />
                <span>{d.effective_value}</span>
              </div>
            ))
          ) : (
            <p>No supported definition patterns found.</p>
          )}
          <h2>Dependency relationships</h2>
          <p className="muted">
            Explicit references, term usage, and amendments extracted from this
            document.
          </p>
          {report.references.map((e, i) => (
            <div className="edge-row" key={i}>
              <span>
                § {report.clauses.find((c) => c.id === e.source)?.label}
              </span>
              <span className="edge-line" />
              <small>{e.type}</small>
              <ArrowRight size={16} />
              <span>
                {e.target
                  ? "§ " + report.clauses.find((c) => c.id === e.target)?.label
                  : e.label}
              </span>
              <span
                className={
                  "tag " + (e.status === "RESOLVED" ? "teal" : "amber")
                }
              >
                {e.status}
              </span>
            </div>
          ))}
        </section>
      ) : (
        <section className="coverage">
          <h2>Read this report within its coverage</h2>
          {report.limitations.map((l) => (
            <p key={l}>
              <AlertTriangle size={18} />
              {l}
            </p>
          ))}
          <p>
            <Clock size={18} />
            Analysis date: {report.as_of}
          </p>
          <p>
            <ShieldCheck size={18} />
            Confidence is not calibrated. No percentage is assigned to these
            rule candidates.
          </p>
          <p>
            <BookOpen size={18} />
            {report.verification === "AI_REVIEWED"
              ? "AI semantic review completed. Its assessments remain interpretations requiring professional review."
              : "AI verification has not run for this contract. Findings are deterministic candidates requiring review."}
          </p>
        </section>
      )}
    </>
  );
}
function FindingDetail({
  finding,
  report,
}: {
  finding: Finding;
  report: Contract;
}) {
  const sources = finding.evidence
    .map((id) => report.clauses.find((c) => c.id === id))
    .filter((c) => !!c);
  return (
    <>
      <div className="detail-top">
        <span className={"severity " + finding.severity.toLowerCase()}>
          {finding.severity}
        </span>
        <span className="muted small">
          {finding.id} · {finding.category}
        </span>
        <span className="review-tag">
          <AlertTriangle size={13} /> Human review required
        </span>
      </div>
      <h2>{finding.title}</h2>
      <p className="finding-explanation">{finding.explanation}</p>
      <div className="detail-section-title">
        <Link2 size={17} />
        <h3>Evidence chain</h3>
        <span>Original clauses</span>
      </div>
      <div className="evidence-path">
        {sources.map((c, i) => (
          <span key={c!.id}>
            <a href={"#source-" + c!.id}>§ {c!.label}</a>
            {i < sources.length - 1 && <ChevronRight size={15} />}
          </span>
        ))}
      </div>
      <div className="detail-section-title">
        <FileText size={17} />
        <h3>Read the source</h3>
      </div>
      <div className="source-cards">
        {sources.map((c) => (
          <article id={"source-" + c!.id} key={c!.id}>
            <header>
              <span>§ {c!.label}</span>
              <strong>{c!.title}</strong>
            </header>
            <pre>{c!.text}</pre>
            <footer>
              <FileText size={13} />
              {c!.page
                ? `Page ${c!.page}${c!.page_end && c!.page_end !== c!.page ? "–" + c!.page_end : ""} · Original PDF`
                : "Original text · Clause " + c!.label}
            </footer>
          </article>
        ))}
      </div>
      <div className="verification-box">
        <ShieldCheck size={20} />
        <div>
          <h3>
            {finding.semantic
              ? "AI assessment · " + finding.semantic.verdict
              : "Deterministic candidate"}
          </h3>
          <p>
            {finding.semantic
              ? finding.semantic.explanation
              : "Extracted relationships and pattern rules support this finding. AI semantic verification has not run. Its legal significance needs review."}
          </p>
        </div>
      </div>
    </>
  );
}
function ResearchReport({ report }: { report: Research }) {
  return (
    <div className="research-report">
      <article>
        <span className="overline">
          {report.kind === "disputes" ? "DISPUTE ANALYSIS" : "LEGAL RESEARCH"}
        </span>
        <h2>Your question</h2>
        <p>{report.description}</p>
        <p className="muted">
          {[report.state, report.district].filter(Boolean).join(" · ")}
        </p>
        <hr />
        <h2>Research findings</h2>
        <div className="research-answer">{report.answer}</div>
        <div className="notice">
          <AlertTriangle size={18} />
          <div>
            {report.limitations.map((l) => (
              <p key={l}>{l}</p>
            ))}
          </div>
        </div>
      </article>
      <aside>
        <h3>
          <BookOpen size={18} /> Source inspector
        </h3>
        {report.sources.map((s) => (
          <section key={s.url}>
            <span className="tag amber">RETRIEVED · REVIEW REQUIRED</span>
            <h4>{s.title}</h4>
            <p>{new URL(s.url).hostname}</p>
            <p>Retrieved {s.retrieved_at}</p>
            <a
              className="text-link"
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Open source <ArrowUpRight size={15} />
            </a>
          </section>
        ))}
      </aside>
    </div>
  );
}
