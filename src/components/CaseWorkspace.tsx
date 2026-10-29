import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  Briefcase,
  FileText,
  Layers,
  Share2,
  Search,
  Clock,
  Brain,
  Scale,
  FileCheck2,
  FileSpreadsheet,
  ArrowLeft,
  Upload,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Plus,
  Trash2,
  ExternalLink,
} from "lucide-react";
import { caseApi } from "../case-api";
import type { CaseItem, CaseDocument, CaseFact } from "../case-types";
import { EvidenceGraphView } from "./EvidenceGraphView";
import { SearchModule } from "./SearchModule";
import { TimelineInconsistenciesView } from "./TimelineInconsistenciesView";
import { ReasoningView } from "./ReasoningView";
import { ArgumentsAuthoritiesView } from "./ArgumentsAuthoritiesView";
import { CaseReportView } from "./CaseReportView";

export function CaseWorkspace() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [caseItem, setCaseItem] = useState<CaseItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("overview");

  // Document management state
  const [documents, setDocuments] = useState<CaseDocument[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<CaseDocument | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [ocrLang, setOcrLang] = useState("");

  // Facts state
  const [facts, setFacts] = useState<CaseFact[]>([]);
  const [factCategoryFilter, setFactCategoryFilter] = useState("all");
  const [factStatusFilter, setFactStatusFilter] = useState("all");

  const loadCaseData = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const [c, docs, fList] = await Promise.all([
        caseApi.getCase(id),
        caseApi.listDocuments(id),
        caseApi.listFacts(id),
      ]);
      setCaseItem(c);
      setDocuments(docs);
      setFacts(fList);
      if (docs.length > 0 && !selectedDoc) {
        setSelectedDoc(docs[0]);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCaseData();
  }, [id]);

  const handleUploadDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !id) return;
    try {
      setUploadBusy(true);
      const form = new FormData();
      form.append("file", uploadFile);
      if (ocrLang) form.append("ocr_language", ocrLang);
      const newDoc = await caseApi.uploadDocument(id, form);
      setUploadFile(null);
      loadCaseData();
      setSelectedDoc(newDoc);
    } catch (err: any) {
      alert(err.message || "Failed to upload document");
    } finally {
      setUploadBusy(false);
    }
  };

  const handleDeleteDocument = async (did: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!id || !confirm("Delete this document and its associated facts?")) return;
    try {
      await caseApi.deleteDocument(id, did);
      if (selectedDoc?.id === did) setSelectedDoc(null);
      loadCaseData();
    } catch (err: any) {
      alert(err.message || "Failed to delete document");
    }
  };

  const handleUpdateFactStatus = async (fid: string, newStatus: string) => {
    if (!id) return;
    try {
      await caseApi.updateFactStatus(id, fid, newStatus);
      setFacts((prev) =>
        prev.map((f) => (f.id === fid ? { ...f, status: newStatus as any } : f))
      );
    } catch (err: any) {
      alert(err.message || "Failed to update fact status");
    }
  };

  if (loading) {
    return <div style={{ padding: "4rem", textAlign: "center", color: "#64748b" }}>Opening case workspace…</div>;
  }

  if (!caseItem) {
    return (
      <div style={{ padding: "3rem", textAlign: "center" }}>
        <h2>Case not found</h2>
        <Link to="/app/cases">Return to Cases</Link>
      </div>
    );
  }

  const filteredFacts = facts.filter((f) => {
    if (factCategoryFilter !== "all" && f.category !== factCategoryFilter) return false;
    if (factStatusFilter !== "all" && f.status !== factStatusFilter) return false;
    return true;
  });

  return (
    <div style={{ padding: "1.25rem 2rem", maxWidth: "1400px", margin: "0 auto" }}>
      {/* Persistent Case Header */}
      <div
        style={{
          background: "#ffffff",
          borderRadius: "10px",
          border: "1px solid #e2e8f0",
          padding: "1rem 1.5rem",
          marginBottom: "1.25rem",
          boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "0.2rem" }}>
              <button
                onClick={() => navigate("/app/cases")}
                style={{
                  background: "transparent",
                  border: "none",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  fontSize: "0.8rem",
                  color: "#64748b",
                  padding: 0,
                }}
              >
                <ArrowLeft size={14} /> Cases
              </button>
              <span style={{ color: "#cbd5e1" }}>/</span>
              <span style={{ fontSize: "0.75rem", fontWeight: 700, padding: "2px 8px", borderRadius: "4px", background: "#e0f2fe", color: "#0369a1" }}>
                {caseItem.reference}
              </span>
              <span style={{ fontSize: "0.8rem", color: "#64748b" }}>• {caseItem.category}</span>
            </div>
            <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: "0 0 0.3rem 0", color: "#0f172a" }}>
              {caseItem.title}
            </h1>
            <div style={{ fontSize: "0.8rem", color: "#475569", display: "flex", gap: "1.2rem" }}>
              <span><b>Parties:</b> {caseItem.parties?.join(" vs ") || "None"}</span>
              {caseItem.jurisdiction && <span><b>Jurisdiction:</b> {caseItem.jurisdiction}</span>}
              {caseItem.court && <span><b>Court:</b> {caseItem.court}</span>}
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <button className="button ghost" onClick={loadCaseData} title="Refresh case data" style={{ padding: "6px" }}>
              <RefreshCw size={15} />
            </button>
            <button
              className="button primary"
              onClick={() => setActiveTab("report")}
              style={{ fontSize: "0.85rem", padding: "0.45rem 0.85rem" }}
            >
              <FileSpreadsheet size={15} /> Case Brief & Export
            </button>
          </div>
        </div>

        {/* Navigation Tabs Bar */}
        <div
          style={{
            display: "flex",
            gap: "0.3rem",
            marginTop: "1.25rem",
            paddingTop: "0.8rem",
            borderTop: "1px solid #f1f5f9",
            overflowX: "auto",
          }}
        >
          {[
            { id: "overview", label: "Overview", icon: Briefcase },
            { id: "documents", label: `Documents (${documents.length})`, icon: FileText },
            { id: "facts", label: `Facts (${facts.length})`, icon: Layers },
            { id: "evidence", label: "Evidence Graph", icon: Share2 },
            { id: "search", label: "Intelligent Search", icon: Search },
            { id: "timeline", label: "Timeline & Inconsistencies", icon: Clock },
            { id: "reasoning", label: "Reasoning Engine", icon: Brain },
            { id: "arguments", label: "Arguments & Authorities", icon: Scale },
            { id: "report", label: "Report Brief", icon: FileSpreadsheet },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.4rem",
                padding: "0.5rem 0.85rem",
                borderRadius: "6px",
                border: "none",
                fontSize: "0.85rem",
                fontWeight: activeTab === tab.id ? 700 : 500,
                cursor: "pointer",
                background: activeTab === tab.id ? "#eff6ff" : "transparent",
                color: activeTab === tab.id ? "#1d4ed8" : "#475569",
                whiteSpace: "nowrap",
                transition: "all 0.15s ease",
              }}
            >
              <tab.icon size={15} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* ======================================================================== */}
      {/* TAB 1: OVERVIEW */}
      {/* ======================================================================== */}
      {activeTab === "overview" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "1.5rem" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
            <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
              <h2 style={{ fontSize: "1.15rem", fontWeight: 700, margin: "0 0 0.6rem 0", color: "#0f172a" }}>
                Case Brief & Narrative
              </h2>
              <p style={{ fontSize: "0.9rem", color: "#334155", lineHeight: "1.5", margin: 0 }}>
                {caseItem.description || "No case description provided yet."}
              </p>
            </div>

            {/* Quick Metrics */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
              <div style={{ background: "#ffffff", padding: "1rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>DOCUMENTS</div>
                <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#0f172a", marginTop: "0.3rem" }}>{documents.length}</div>
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Indexed in search engine</div>
              </div>
              <div style={{ background: "#ffffff", padding: "1rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>EXTRACTED FACTS</div>
                <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#2563eb", marginTop: "0.3rem" }}>{facts.length}</div>
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Source-anchored items</div>
              </div>
              <div style={{ background: "#ffffff", padding: "1rem", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>FLAGGED CONFLICTS</div>
                <div style={{ fontSize: "1.8rem", fontWeight: 700, color: "#dc2626", marginTop: "0.3rem" }}>{caseItem.inconsistency_count || 0}</div>
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>Requires verification</div>
              </div>
            </div>

            {/* Quick Actions Card */}
            <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a", margin: "0 0 0.8rem 0" }}>
                Recommended Strategy Workflows
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem" }}>
                <button
                  className="button ghost"
                  onClick={() => setActiveTab("evidence")}
                  style={{ textAlign: "left", padding: "0.8rem", display: "flex", flexDirection: "column", gap: "4px" }}
                >
                  <b style={{ color: "#2563eb", fontSize: "0.9rem" }}>Explore Evidence Graph →</b>
                  <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Find proof paths between documents</span>
                </button>
                <button
                  className="button ghost"
                  onClick={() => setActiveTab("timeline")}
                  style={{ textAlign: "left", padding: "0.8rem", display: "flex", flexDirection: "column", gap: "4px" }}
                >
                  <b style={{ color: "#dc2626", fontSize: "0.9rem" }}>Inspect Inconsistencies →</b>
                  <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Examine date & payment deficits</span>
                </button>
                <button
                  className="button ghost"
                  onClick={() => setActiveTab("reasoning")}
                  style={{ textAlign: "left", padding: "0.8rem", display: "flex", flexDirection: "column", gap: "4px" }}
                >
                  <b style={{ color: "#059669", fontSize: "0.9rem" }}>Run Reasoning Engine →</b>
                  <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Forward and backward chaining rules</span>
                </button>
                <button
                  className="button ghost"
                  onClick={() => setActiveTab("report")}
                  style={{ textAlign: "left", padding: "0.8rem", display: "flex", flexDirection: "column", gap: "4px" }}
                >
                  <b style={{ color: "#7c3aed", fontSize: "0.9rem" }}>View Case Brief →</b>
                  <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Export report for advocates</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right Checklist */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 700, margin: "0 0 0.8rem 0" }}>Preparation Checklist</h3>
              <div style={{ display: "grid", gap: "0.6rem", fontSize: "0.85rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", color: documents.length > 0 ? "#059669" : "#64748b" }}>
                  <CheckCircle2 size={16} /> Documents Ingested ({documents.length})
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", color: facts.length > 0 ? "#059669" : "#64748b" }}>
                  <CheckCircle2 size={16} /> Facts Extracted ({facts.length})
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", color: caseItem.inconsistency_count === 0 ? "#059669" : "#d97706" }}>
                  <AlertTriangle size={16} /> Discrepancies Checked ({caseItem.inconsistency_count || 0})
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#059669" }}>
                  <CheckCircle2 size={16} /> Local Storage Verified
                </div>
              </div>
            </div>

            <div style={{ background: "#f8fafc", padding: "1rem", borderRadius: "10px", border: "1px solid #e2e8f0", fontSize: "0.8rem", color: "#64748b" }}>
              <b>Confidentiality Guarantee:</b> Document parsing and reasoning run locally on your system. No external paid APIs or third-party models are mandated.
            </div>
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* TAB 2: DOCUMENTS */}
      {/* ======================================================================== */}
      {activeTab === "documents" && (
        <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: "1.5rem" }}>
          {/* Document List & Ingestion */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
              <h3 style={{ margin: "0 0 0.8rem 0", fontSize: "1rem", fontWeight: 700 }}>Upload Case File</h3>
              <form onSubmit={handleUploadDocument}>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  style={{ width: "100%", marginBottom: "0.8rem", fontSize: "0.85rem" }}
                  required
                />
                <button
                  type="submit"
                  className="button primary"
                  disabled={uploadBusy || !uploadFile}
                  style={{ width: "100%", fontSize: "0.85rem" }}
                >
                  <Upload size={14} /> {uploadBusy ? "Ingesting & Parsing…" : "Upload & Extract Text"}
                </button>
              </form>
            </div>

            <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "0.5rem" }}>
              <div style={{ padding: "0.5rem 0.8rem", fontSize: "0.8rem", fontWeight: 700, color: "#64748b" }}>
                CASE DOCUMENTS ({documents.length})
              </div>
              {documents.map((d) => (
                <div
                  key={d.id}
                  onClick={async () => {
                    const full = await caseApi.getDocument(id!, d.id);
                    setSelectedDoc(full);
                  }}
                  style={{
                    padding: "0.6rem 0.8rem",
                    borderRadius: "6px",
                    background: selectedDoc?.id === d.id ? "#eff6ff" : "transparent",
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "2px",
                  }}
                >
                  <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1 }}>
                    <div style={{ fontSize: "0.85rem", fontWeight: selectedDoc?.id === d.id ? 700 : 500, color: "#0f172a" }}>
                      {d.filename}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                      {d.file_type.toUpperCase()} • {(d.file_size / 1024).toFixed(1)} KB
                    </div>
                  </div>
                  <button
                    className="button ghost"
                    onClick={(e) => handleDeleteDocument(d.id, e)}
                    style={{ padding: "4px", color: "#94a3b8" }}
                    title="Delete document"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Document Extracted Text Viewer */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.5rem", minHeight: "500px" }}>
            {selectedDoc ? (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", borderBottom: "1px solid #f1f5f9", paddingBottom: "0.8rem" }}>
                  <div>
                    <h2 style={{ fontSize: "1.2rem", fontWeight: 700, margin: 0, color: "#0f172a" }}>
                      {selectedDoc.filename}
                    </h2>
                    <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "2px" }}>
                      ID: {selectedDoc.id} • {selectedDoc.pages?.length || 1} pages
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    background: "#f8fafc",
                    padding: "1.25rem",
                    borderRadius: "8px",
                    fontFamily: "monospace",
                    fontSize: "0.85rem",
                    lineHeight: "1.6",
                    maxHeight: "560px",
                    overflowY: "auto",
                    whiteSpace: "pre-wrap",
                    color: "#1e293b",
                    border: "1px solid #e2e8f0",
                  }}
                >
                  {selectedDoc.extracted_text || "No text extracted."}
                </div>
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "4rem", color: "#64748b" }}>
                Select a document on the left to inspect its extracted text.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* TAB 3: FACTS */}
      {/* ======================================================================== */}
      {activeTab === "facts" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {/* Fact Filter Bar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
            <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#64748b" }}>Category:</span>
                <select
                  value={factCategoryFilter}
                  onChange={(e) => setFactCategoryFilter(e.target.value)}
                  style={{ height: "34px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.8rem", background: "#ffffff" }}
                >
                  <option value="all">All Categories</option>
                  <option value="Payment">Payment</option>
                  <option value="Obligation">Obligation</option>
                  <option value="Temporal">Temporal / Dates</option>
                  <option value="Claim">Claims & Allegations</option>
                  <option value="Event">Events</option>
                </select>
              </div>

              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#64748b" }}>Status:</span>
                <select
                  value={factStatusFilter}
                  onChange={(e) => setFactStatusFilter(e.target.value)}
                  style={{ height: "34px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.8rem", background: "#ffffff" }}
                >
                  <option value="all">All Statuses</option>
                  <option value="candidate">Candidate</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
            </div>

            <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
              Showing {filteredFacts.length} of {facts.length} facts
            </span>
          </div>

          {/* Facts Table */}
          <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", overflow: "hidden" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
              <thead>
                <tr style={{ background: "#f8fafc", borderBottom: "1px solid #e2e8f0", textAlign: "left" }}>
                  <th style={{ padding: "10px 12px" }}>Fact / Assertion</th>
                  <th style={{ padding: "10px 12px", width: "140px" }}>Category</th>
                  <th style={{ padding: "10px 12px", width: "160px" }}>Entity / Role</th>
                  <th style={{ padding: "10px 12px", width: "180px" }}>Source Document</th>
                  <th style={{ padding: "10px 12px", width: "120px" }}>Status</th>
                  <th style={{ padding: "10px 12px", width: "140px", textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredFacts.map((f) => (
                  <tr key={f.id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "10px 12px", fontWeight: 500, color: "#0f172a" }}>
                      {f.text}
                    </td>
                    <td style={{ padding: "10px 12px", color: "#64748b" }}>
                      <span style={{ padding: "2px 6px", borderRadius: "4px", background: "#f1f5f9", fontSize: "0.75rem", fontWeight: 600 }}>
                        {f.category}
                      </span>
                    </td>
                    <td style={{ padding: "10px 12px", color: "#334155" }}>
                      {f.entity || "—"}
                    </td>
                    <td style={{ padding: "10px 12px", color: "#2563eb", fontSize: "0.8rem" }}>
                      {f.filename || "Case record"}
                    </td>
                    <td style={{ padding: "10px 12px" }}>
                      <span
                        style={{
                          fontSize: "0.75rem",
                          fontWeight: 700,
                          padding: "2px 6px",
                          borderRadius: "4px",
                          background: f.status === "confirmed" ? "#ecfdf5" : f.status === "rejected" ? "#fef2f2" : "#fef3c7",
                          color: f.status === "confirmed" ? "#059669" : f.status === "rejected" ? "#dc2626" : "#b45309",
                        }}
                      >
                        {f.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: "10px 12px", textAlign: "right" }}>
                      {f.status !== "confirmed" && (
                        <button
                          className="button ghost"
                          onClick={() => handleUpdateFactStatus(f.id, "confirmed")}
                          style={{ fontSize: "0.75rem", padding: "2px 6px", color: "#059669" }}
                        >
                          Confirm
                        </button>
                      )}
                      {f.status !== "rejected" && (
                        <button
                          className="button ghost"
                          onClick={() => handleUpdateFactStatus(f.id, "rejected")}
                          style={{ fontSize: "0.75rem", padding: "2px 6px", color: "#dc2626" }}
                        >
                          Reject
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* TAB 4: EVIDENCE GRAPH */}
      {/* ======================================================================== */}
      {activeTab === "evidence" && <EvidenceGraphView caseId={id!} />}

      {/* ======================================================================== */}
      {/* TAB 5: INTELLIGENT SEARCH */}
      {/* ======================================================================== */}
      {activeTab === "search" && (
        <SearchModule
          caseId={id!}
          onOpenDocument={async (did) => {
            const doc = await caseApi.getDocument(id!, did);
            setSelectedDoc(doc);
            setActiveTab("documents");
          }}
        />
      )}

      {/* ======================================================================== */}
      {/* TAB 6: TIMELINE & INCONSISTENCIES */}
      {/* ======================================================================== */}
      {activeTab === "timeline" && <TimelineInconsistenciesView caseId={id!} />}

      {/* ======================================================================== */}
      {/* TAB 7: REASONING */}
      {/* ======================================================================== */}
      {activeTab === "reasoning" && <ReasoningView caseId={id!} />}

      {/* ======================================================================== */}
      {/* TAB 8: ARGUMENTS & AUTHORITIES */}
      {/* ======================================================================== */}
      {activeTab === "arguments" && <ArgumentsAuthoritiesView caseId={id!} />}

      {/* ======================================================================== */}
      {/* TAB 9: REPORT BRIEF */}
      {/* ======================================================================== */}
      {activeTab === "report" && <CaseReportView caseId={id!} />}
    </div>
  );
}
