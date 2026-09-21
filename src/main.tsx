import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useNavigate,
} from "react-router-dom";
import {
  ArrowUpRight,
  ArrowRight,
  FileText,
  Search,
  ShieldCheck,
  BookOpen,
  FolderOpen,
  Scale,
  LogOut,
  Menu,
  X,
  ChevronRight,
  Activity,
  Link2,
} from "lucide-react";
import { api } from "./api";
import { ReleaseScopeProvider, useReleaseScope } from './release-scope';
import { LoginOptions, RecoveryPage, AuthResultNotice } from "./auth-options";
import {
  ContractPage,
  ResearchPage,
  HistoryPage,
  ReportPage,
} from "./workspace";
import "./styles.css";
import "./brand.css";

export function Brand() {
  return (
    <Link className="brand" to="/" aria-label="LexVigil home">
      <span className="logo-crop">
        <img src="/lexvigil-logo.png" alt="" />
      </span>
      <span>
        LEXVIGIL<small>LEGAL INTELLIGENCE</small>
      </span>
    </Link>
  );
}
function Landing() {
  const scope = useReleaseScope();
  return (
    <div className="landing">
      <header className="public-header">
        <Brand />
        <nav>
          <a href="#product">The platform</a>
          <a href="#methodology">Our approach</a>
          <a href="#privacy">Privacy</a>
        </nav>
        <Link className="button ghost" to="/login">
          Sign in <ArrowUpRight size={16} />
        </Link>
      </header>
      <main>
        <section className="hero">
          <div className="hero-copy">
            <h1>
              Clarity in the law.
              <br />
              <em>
                Confidence in
                <br />
                the evidence.
              </em>
            </h1>
            <p>
              {scope.research
                ? 'Make sense of your contracts and legal questions. Trace references, examine sources, and see how each finding connects.'
                : 'Explore your contract’s clauses, references and potential inconsistencies with evidence-linked, rule-based analysis. Human review is required.'}
            </p>
            <div className="actions">
              <Link className="button primary" to="/login">
                Open your workspace <ArrowRight size={18} />
              </Link>
              <a className="text-link" href="#product">
                Explore LexVigil <ChevronRight size={16} />
              </a>
            </div>
            <div className="hero-foot">
              <span className="small-line" />
              {scope.research ? 'Built for Indian legal research and contract review' : 'Contract-review demonstration · Not legal advice'}
            </div>
          </div>
          <div className="hero-preview">
            <div className="preview-bar">
              <span>
                <FileText size={14} /> Services agreement
              </span>
              <span className="tag">ILLUSTRATIVE EXAMPLE</span>
            </div>
            <div className="preview-document">
              <div className="doc-eyebrow">CONTRACT INTELLIGENCE</div>
              <h2>
                A reference changes.
                <br />
                The obligation follows.
              </h2>
              <div className="preview-chain">
                <div>
                  <span className="clause-label">§ 4.2</span>
                  <p>
                    Payment Period<small>Original definition</small>
                  </p>
                  <b>30 days</b>
                </div>
                <div>
                  <span className="clause-label blue">§ 17.3</span>
                  <p>
                    Amended period<small>Effective obligation</small>
                  </p>
                  <b className="blue-text">45 days</b>
                </div>
                <div>
                  <span className="clause-label coral">§ 12.4</span>
                  <p>
                    Late-payment charge<small>Unchanged trigger</small>
                  </p>
                  <b className="red-text">30 days</b>
                </div>
              </div>
              <div className="preview-finding">
                <span className="finding-dot" />
                <div>
                  <strong>A potential inconsistency</strong>
                  <p>Does the penalty begin before payment is due?</p>
                </div>
                <ArrowUpRight size={18} />
              </div>
              <div className="preview-bottom">
                <Link2 size={14} /> Traceable clauses{" "}
                <span>Human review required</span>
              </div>
            </div>
          </div>
        </section>
        <section className="product-section" id="product">
          <div className="section-intro">
            <span className="overline">ONE CONNECTED WORKSPACE</span>
            <h2>
              From a legal question
              <br />
              to the evidence behind it.
            </h2>
            <p>
              {scope.research
                ? 'Three ways to explore. One principle: every important conclusion should lead you back to a source.'
                : 'Explore contract structure and follow findings back to their clauses. Live legal research and AI review are deferred from this demonstration.'}
            </p>
          </div>
          <div className="product-rows">
            {[
              {
                icon: FileText,
                n: "01",
                title: "Contract intelligence",
                text: "Follow definitions, cross-references and amendments. Inspect potential inconsistencies alongside their original clauses.",
                url: "/app/contracts",
              },
              {
                icon: Scale,
                n: "02",
                title: "Dispute intelligence",
                text: "Organize what happened, identify missing facts and explore potentially relevant legal sources.",
                url: "/app/disputes",
              },
              {
                icon: Search,
                n: "03",
                title: "Legal research",
                text: "Ask a focused question and examine retrieved official sources with a clear view of their limitations.",
                url: "/app/research",
              },
            ].filter(i => i.n === '01' || scope.research).map((i) => (
              <Link to={i.url} key={i.n} className="product-row">
                <span className="row-number">{i.n}</span>
                <i.icon size={24} />
                <div>
                  <h3>{i.title}</h3>
                  <p>{i.text}</p>
                </div>
                <ArrowUpRight size={22} />
              </Link>
            ))}
          </div>
        </section>
        <section className="method-section" id="methodology">
          <div>
            <span className="overline">THE LEXVIGIL APPROACH</span>
            <h2>
              Structure before reasoning.
              <br />
              Evidence before answers.
            </h2>
          </div>
          <ol>
            {[
              "Read the document",
              "Connect the references",
              "Examine the relationships",
              "Review the evidence",
            ].map((x, i) => (
              <li key={x}>
                <span>0{i + 1}</span>
                {x}
              </li>
            ))}
          </ol>
          <p>
            Original text, derived findings, and AI interpretation stay
            distinguishable. Unresolved references and unavailable sources
            remain visible, so you can decide what needs a closer look.
          </p>
        </section>
        <section className="privacy-section" id="privacy">
          <ShieldCheck size={34} />
          <div>
            <h2>Your work. Your decision to save.</h2>
            <p>
              Analyses are temporary by default. Choose what to keep, export
              your report, or delete an analysis from your workspace. Temporary
              analyses expire after 24 hours and are removed when you sign out.
            </p>
          </div>
          <Link to="/login" className="button primary">
            Get started <ArrowRight size={17} />
          </Link>
        </section>
      </main>
      <footer className="public-footer">
        <Brand />
        <p>
          Legal information and research assistance.
          <br />
          Professional review remains essential.
        </p>
        <span>© {new Date().getFullYear()} LexVigil</span>
      </footer>
    </div>
  );
}
function Auth({ onLogin }: { onLogin: (email: string) => void }) {
  const [notice, setNotice] = useState("");
  const [register, setRegister] = useState(false),
    [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const navigate = useNavigate();
  return (
    <div className="auth-page">
      <Brand />
      <div className="auth-layout">
        <div>
          <span className="overline">YOUR LEGAL WORKSPACE</span>
          <h1>
            Make the complex
            <br />
            more understandable.
          </h1>
          <p>
            A clear view of your contracts, questions, and supporting evidence.
          </p>
          <div className="auth-note">
            <ShieldCheck />
            <span>
              Temporary by default.
              <br />
              Saved only when you choose.
            </span>
          </div>
        </div>
        <form
          className="auth-form"
          onSubmit={async (e) => {
            e.preventDefault();
            setError("");
            setNotice("");
            setBusy(true);
            try {
              const u = await api(
                "/auth/" + (register ? "register" : "login"),
                { method: "POST", body: JSON.stringify({ email, password }) },
              );
              if (u.requires_confirmation) {
                setNotice(u.message);
                setRegister(false);
                setPassword("");
                return;
              }
              onLogin(u.email);
              navigate("/app/contracts");
            } catch (e) {
              setError((e as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <h2>{register ? "Create your account" : "Welcome back"}</h2>
          <AuthResultNotice />
          <p>
            {register
              ? "A workspace for your next question."
              : "Sign in to continue your research."}
          </p>
          <label>
            Email
            <input
              autoComplete="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label>
            Password
            <input
              autoComplete={register ? "new-password" : "current-password"}
              type="password"
              aria-label="Password"
              aria-describedby="password-help"
              minLength={12}
              maxLength={128}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <small id="password-help">At least 12 characters</small>
          </label>
          {error && (
            <div role="alert" className="error">
              {error}
            </div>
          )}
          {notice && <p role="status">{notice}</p>}
          <button className="button primary" disabled={busy}>
            {busy ? "Please wait…" : register ? "Create account" : "Sign in"}
            <ArrowRight size={17} />
          </button>
          <p className="auth-switch">
            {register ? "Already registered?" : "New to LexVigil?"}{" "}
            <button
              type="button"
              onClick={() => {
                setRegister(!register);
                setError("");
                setNotice("");
              }}
            >
              {register ? "Sign in" : "Create an account"}
            </button>
          </p>
          <LoginOptions />
        </form>
      </div>
    </div>
  );
}
function Shell({ email, onLogout }: { email: string; onLogout: () => void }) {
  const scope = useReleaseScope();
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [healthy, setHealthy] = useState<boolean | null>(null);
  useEffect(() => {
    api("/health")
      .then((h) => setHealthy(h.ai_configured))
      .catch(() => setHealthy(null));
  }, []);
  return (
    <div className="app-shell">
      <aside className={"sidebar " + (open ? "mobile-open" : "")}>
        <Brand />
        <div className="workspace-label">WORKSPACE</div>
        <nav>
          {[
            { path: "contracts", icon: FileText, label: "Analyze contract" },
            { path: "disputes", icon: Scale, label: "Analyze dispute" },
            { path: "research", icon: Search, label: "Legal research" },
            { path: "history", icon: FolderOpen, label: "My analyses" },
          ].filter(n => !['research', 'disputes'].includes(n.path) || scope.research).map((n) => (
            <NavLink
              to={"/app/" + n.path}
              key={n.path}
              onClick={() => setOpen(false)}
            >
              <n.icon size={19} />
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="privacy-mini">
            <ShieldCheck size={20} />
            <strong>In your control</strong>
            <p>
              Temporary analyses expire in 24 hours. Save only what you need.
            </p>
          </div>
          <div className="account">
            <span className="avatar">{email[0].toUpperCase()}</span>
            <span title={email}>
              {email}
              <small>Personal workspace</small>
            </span>
            <button
              title="Sign out and delete temporary analyses"
              onClick={async () => {
                try {
                  await api("/logout", { method: "POST" });
                  onLogout();
                } catch (e) {
                  setError((e as Error).message);
                }
              }}
            >
              <LogOut size={17} />
            </button>
          </div>
          {error && <p className="error">{error}</p>}
        </div>
      </aside>
      <div className="app-main">
        <header className="app-header">
          <button
            className="mobile-menu"
            aria-label="Toggle navigation"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>
          <span>
            Workspace <ChevronRight size={14} /> Legal intelligence
          </span>
          <div className="service-status">
            <span className={"status-dot " + (healthy ? "online" : "")} />
            {healthy
              ? "Live research available"
              : healthy === false
                ? "Local contract engine"
                : "Checking connection"}
          </div>
        </header>
        <main className="workspace">
          {scope.profile === 'showcase' && <p role="status">Contract-analysis showcase · Rule-based findings require human review. Live AI research, scanned-document OCR and original-file storage are deferred.</p>}
          <Routes>
            <Route path="contracts" element={<ContractPage />} />
            <Route path="disputes" element={scope.research ? <ResearchPage kind="disputes" /> : <Navigate to="/app/contracts" replace />} />
            <Route path="research" element={scope.research ? <ResearchPage kind="research" /> : <Navigate to="/app/contracts" replace />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="analyses/:id" element={<ReportPage />} />
            <Route path="*" element={<Navigate to="contracts" replace />} />
          </Routes>
        </main>
        <footer className="app-footer">
          <span>
            <Activity size={13} /> Evidence before answers
          </span>
          <span>Legal information · Professional review recommended</span>
        </footer>
      </div>
    </div>
  );
}
function App() {
  const [user, setUser] = useState<string | null>(null),
    [loading, setLoading] = useState(true);
  useEffect(() => {
    const expired = () => setUser(null);
    window.addEventListener("lexvigil:session-expired", expired);
    return () =>
      window.removeEventListener("lexvigil:session-expired", expired);
  }, []);
  useEffect(() => {
    api("/me")
      .then((u) => setUser(u.email))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/forgot-password" element={<RecoveryPage />} />
      <Route path="/reset-password" element={<RecoveryPage reset />} />
      <Route
        path="/login"
        element={
          user ? (
            <Navigate to="/app/contracts" replace />
          ) : (
            <Auth onLogin={setUser} />
          )
        }
      />
      <Route
        path="/app/*"
        element={
          loading ? (
            <div className="loading-page">Opening workspace…</div>
          ) : user ? (
            <Shell email={user} onLogout={() => setUser(null)} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="*"
        element={
          <div className="loading-page">
            <h1>Page not found</h1>
            <Link to="/">Return to LexVigil</Link>
          </div>
        }
      />
    </Routes>
  );
}
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ReleaseScopeProvider><App /></ReleaseScopeProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
