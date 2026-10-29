import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Briefcase,
  FileText,
  Search,
  Plus,
  Sparkles,
  AlertTriangle,
  FolderOpen,
  ArrowRight,
  Trash2,
  Scale,
  Brain,
  CheckCircle2,
  Clock,
  Layers,
} from "lucide-react";
import { caseApi } from "../case-api";
import type { CaseItem } from "../case-types";

export function Dashboard() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [demoBusy, setDemoBusy] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // New Case Form state
  const [newTitle, setNewTitle] = useState("");
  const [newRef, setNewRef] = useState("");
  const [newCategory, setNewCategory] = useState("Commercial Dispute");
  const [newParties, setNewParties] = useState("");
  const [newJurisdiction, setNewJurisdiction] = useState("New Delhi, India");
  const [newCourt, setNewCourt] = useState("High Court of Delhi / Arbitral Tribunal");
  const [newDesc, setNewDesc] = useState("");
  const [createBusy, setCreateBusy] = useState(false);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const data = await caseApi.listCases(
        statusFilter === "all" ? undefined : statusFilter,
        search.trim() || undefined
      );
      setCases(data);
    } catch (err: any) {
      setError(err.message || "Failed to load cases");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCases();
  };

  const handleLoadDemo = async () => {
    try {
      setDemoBusy(true);
      setError("");
      const demo = await caseApi.loadDemoCase();
      navigate(`/app/cases/${demo.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to load demonstration case");
    } finally {
      setDemoBusy(false);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newRef.trim()) return;
    try {
      setCreateBusy(true);
      setError("");
      const partiesList = newParties
        .split(",")
        .map((p) => p.trim())
        .filter(Boolean);
      const created = await caseApi.createCase({
        title: newTitle,
        reference: newRef,
        category: newCategory,
        parties: partiesList,
        jurisdiction: newJurisdiction,
        court: newCourt,
        description: newDesc,
        tags: [newCategory],
      });
      setShowModal(false);
      navigate(`/app/cases/${created.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to create case");
    } finally {
      setCreateBusy(false);
    }
  };

  const handleDeleteCase = async (cid: string, title: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Are you sure you want to permanently delete case "${title}" and all its documents?`)) return;
    try {
      await caseApi.deleteCase(cid);
      setCases((prev) => prev.filter((c) => c.id !== cid));
    } catch (err: any) {
      alert(err.message || "Failed to delete case");
    }
  };

  // Aggregated metrics
  const totalDocs = cases.reduce((sum, c) => sum + (c.doc_count || 0), 0);
  const totalFacts = cases.reduce((sum, c) => sum + (c.fact_count || 0), 0);
  const totalInconsistencies = cases.reduce((sum, c) => sum + (c.inconsistency_count || 0), 0);

  return (
    <div className="dashboard-container" style={{ padding: "1.5rem 2rem", maxWidth: "1400px", margin: "0 auto" }}>
      {/* Top Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "2rem" }}>
        <div>
          <span className="overline" style={{ letterSpacing: "1.5px", fontSize: "0.8rem", color: "#64748b" }}>
            LEGAL CASE INTELLIGENCE & STRATEGY
          </span>
          <h1 style={{ fontSize: "2.1rem", fontWeight: 700, margin: "0.3rem 0 0.5rem 0", color: "#0f172a" }}>
            Case Intelligence Dashboard
          </h1>
          <p style={{ color: "#475569", margin: 0, fontSize: "0.95rem" }}>
            Manage active litigation files, trace cross-document evidence, and execute verifiable legal reasoning.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <button
            className="button primary"
            onClick={handleLoadDemo}
            disabled={demoBusy}
            style={{ display: "flex", alignItems: "center", gap: "0.5rem", background: "linear-gradient(135deg, #1e3a8a, #2563eb)" }}
            title="Load the comprehensive payment-dispute civil demonstration case"
          >
            <Sparkles size={16} />
            {demoBusy ? "Loading Demo Case…" : "Load Fictional Demo Case"}
          </button>
          <button
            className="button primary"
            onClick={() => setShowModal(true)}
            style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
          >
            <Plus size={16} /> New Case File
          </button>
          <Link
            to="/app/lab"
            className="button ghost"
            style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
          >
            <Brain size={16} /> AI Algorithm Lab
          </Link>
        </div>
      </div>

      {error && (
        <div role="alert" className="error" style={{ marginBottom: "1.5rem", padding: "0.8rem 1rem", borderRadius: "8px", background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b" }}>
          {error}
        </div>
      )}

      {/* Metrics Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <div className="card" style={{ padding: "1.25rem", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>ACTIVE CASES</span>
            <Briefcase size={18} color="#2563eb" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#0f172a", marginTop: "0.5rem" }}>{cases.length}</div>
          <div style={{ color: "#64748b", fontSize: "0.8rem", marginTop: "0.2rem" }}>Isolated client case files</div>
        </div>

        <div className="card" style={{ padding: "1.25rem", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>DOCUMENTS INGESTED</span>
            <FileText size={18} color="#059669" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#0f172a", marginTop: "0.5rem" }}>{totalDocs}</div>
          <div style={{ color: "#64748b", fontSize: "0.8rem", marginTop: "0.2rem" }}>Indexed contracts, invoices & pleadings</div>
        </div>

        <div className="card" style={{ padding: "1.25rem", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>EXTRACTED FACTS</span>
            <Layers size={18} color="#d97706" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#0f172a", marginTop: "0.5rem" }}>{totalFacts}</div>
          <div style={{ color: "#64748b", fontSize: "0.8rem", marginTop: "0.2rem" }}>Source-linked assertions & covenants</div>
        </div>

        <div className="card" style={{ padding: "1.25rem", borderRadius: "10px", background: "#ffffff", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.85rem", fontWeight: 600 }}>
            <span>FLAGGED INCONSISTENCIES</span>
            <AlertTriangle size={18} color="#dc2626" />
          </div>
          <div style={{ fontSize: "2rem", fontWeight: 700, color: "#dc2626", marginTop: "0.5rem" }}>{totalInconsistencies}</div>
          <div style={{ color: "#64748b", fontSize: "0.8rem", marginTop: "0.2rem" }}>Cross-document discrepancies requiring review</div>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap" }}>
        <form onSubmit={handleSearchSubmit} style={{ display: "flex", gap: "0.5rem", flex: "1", maxWidth: "450px" }}>
          <div style={{ position: "relative", width: "100%" }}>
            <Search size={16} style={{ position: "absolute", left: "12px", top: "12px", color: "#94a3b8" }} />
            <input
              type="text"
              placeholder="Search cases by title, reference, or description…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: "100%", paddingLeft: "2.3rem", paddingRight: "1rem", height: "40px", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            />
          </div>
          <button type="submit" className="button ghost" style={{ height: "40px" }}>
            Search
          </button>
        </form>

        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <label style={{ fontSize: "0.85rem", color: "#64748b", fontWeight: 600 }}>Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ height: "40px", borderRadius: "6px", border: "1px solid #cbd5e1", padding: "0 0.8rem", background: "#ffffff" }}
          >
            <option value="all">All Cases</option>
            <option value="active">Active Files</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Case List Table / Cards */}
      {loading ? (
        <div style={{ padding: "3rem", textAlign: "center", color: "#64748b" }}>Loading case records…</div>
      ) : cases.length === 0 ? (
        <div style={{ padding: "4rem 2rem", textAlign: "center", background: "#f8fafc", borderRadius: "12px", border: "2px dashed #cbd5e1" }}>
          <FolderOpen size={44} style={{ color: "#94a3b8", marginBottom: "1rem" }} />
          <h3 style={{ fontSize: "1.2rem", fontWeight: 600, color: "#1e293b", margin: "0 0 0.5rem 0" }}>No case files found</h3>
          <p style={{ color: "#64748b", maxWidth: "420px", margin: "0 auto 1.5rem auto", fontSize: "0.9rem" }}>
            Create your first legal case file or click below to launch the pre-populated payment dispute demo case.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
            <button className="button primary" onClick={handleLoadDemo} disabled={demoBusy}>
              <Sparkles size={16} /> Load Fictional Demo Case
            </button>
            <button className="button ghost" onClick={() => setShowModal(true)}>
              <Plus size={16} /> Create Case
            </button>
          </div>
        </div>
      ) : (
        <div style={{ display: "grid", gap: "1rem" }}>
          {cases.map((c) => (
            <div
              key={c.id}
              onClick={() => navigate(`/app/cases/${c.id}`)}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "1.25rem 1.5rem",
                background: "#ffffff",
                borderRadius: "10px",
                border: "1px solid #e2e8f0",
                boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#93c5fd")}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = "#e2e8f0")}
            >
              <div style={{ flex: "1", paddingRight: "1rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.3rem" }}>
                  <span style={{ fontSize: "0.75rem", fontWeight: 700, padding: "2px 8px", borderRadius: "4px", background: "#e0f2fe", color: "#0369a1" }}>
                    {c.reference}
                  </span>
                  <span style={{ fontSize: "0.8rem", color: "#64748b" }}>• {c.category}</span>
                  {c.id.startsWith("DEMO") && (
                    <span style={{ fontSize: "0.7rem", fontWeight: 700, padding: "2px 6px", borderRadius: "4px", background: "#fef3c7", color: "#b45309" }}>
                      FICTIONAL DEMO
                    </span>
                  )}
                </div>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 600, color: "#0f172a", margin: "0 0 0.4rem 0" }}>{c.title}</h3>
                <p style={{ fontSize: "0.85rem", color: "#475569", margin: "0 0 0.5rem 0", maxWidth: "800px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {c.description || "No description provided."}
                </p>
                <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.8rem", color: "#64748b" }}>
                  <span><b>Parties:</b> {c.parties?.join(" vs ") || "None recorded"}</span>
                  {c.jurisdiction && <span><b>Jurisdiction:</b> {c.jurisdiction}</span>}
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "0.8rem", color: "#64748b" }}>
                    <b>{c.doc_count || 0}</b> docs • <b>{c.fact_count || 0}</b> facts
                  </div>
                  {c.inconsistency_count && c.inconsistency_count > 0 ? (
                    <div style={{ fontSize: "0.75rem", color: "#dc2626", fontWeight: 600, display: "flex", alignItems: "center", gap: "3px", justifyContent: "flex-end" }}>
                      <AlertTriangle size={12} /> {c.inconsistency_count} flagged issues
                    </div>
                  ) : (
                    <div style={{ fontSize: "0.75rem", color: "#059669", display: "flex", alignItems: "center", gap: "3px", justifyContent: "flex-end" }}>
                      <CheckCircle2 size={12} /> No conflicts
                    </div>
                  )}
                </div>

                <button
                  className="button ghost"
                  onClick={(e) => handleDeleteCase(c.id, c.title, e)}
                  style={{ color: "#94a3b8", padding: "6px" }}
                  title="Delete case file"
                >
                  <Trash2 size={16} />
                </button>

                <div style={{ color: "#2563eb", display: "flex", alignItems: "center" }}>
                  <ArrowRight size={20} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* New Case Creation Modal */}
      {showModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(15, 23, 42, 0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "1rem",
          }}
        >
          <div
            style={{
              background: "#ffffff",
              borderRadius: "12px",
              padding: "2rem",
              width: "100%",
              maxWidth: "600px",
              maxHeight: "90vh",
              overflowY: "auto",
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
            }}
          >
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700, margin: "0 0 1rem 0", color: "#0f172a" }}>
              Open New Legal Case File
            </h2>
            <form onSubmit={handleCreateCase}>
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Case Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Construction Ltd. v. Metro Transport Authority"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{ width: "100%", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                    Internal Reference / Docket *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. ARB/2024/DEL/101"
                    value={newRef}
                    onChange={(e) => setNewRef(e.target.value)}
                    style={{ width: "100%", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                    Category
                  </label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    style={{ width: "100%", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1", background: "#ffffff" }}
                  >
                    <option value="Commercial Dispute">Commercial Dispute</option>
                    <option value="Construction & EPC">Construction & EPC</option>
                    <option value="Contract Breach">Contract Breach</option>
                    <option value="Debt Recovery">Debt Recovery</option>
                    <option value="Arbitration">Arbitration</option>
                    <option value="General Civil">General Civil</option>
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Parties (Comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Acme Construction Ltd. (Claimant), Metro Transport Authority (Respondent)"
                  value={newParties}
                  onChange={(e) => setNewParties(e.target.value)}
                  style={{ width: "100%", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                    Jurisdiction
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. New Delhi, India"
                    value={newJurisdiction}
                    onChange={(e) => setNewJurisdiction(e.target.value)}
                    style={{ width: "100%", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                    Forum / Court
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Arbitral Tribunal / Commercial Court"
                    value={newCourt}
                    onChange={(e) => setNewCourt(e.target.value)}
                    style={{ width: "100%", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: "1.5rem" }}>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "#334155", marginBottom: "0.3rem" }}>
                  Case Description & Brief
                </label>
                <textarea
                  rows={3}
                  placeholder="Overview of core claims, dispute background, and key transactions…"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  style={{ width: "100%", padding: "0.6rem 0.8rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
                <button type="button" className="button ghost" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="button primary" disabled={createBusy}>
                  {createBusy ? "Creating Case…" : "Initialize Case File"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
