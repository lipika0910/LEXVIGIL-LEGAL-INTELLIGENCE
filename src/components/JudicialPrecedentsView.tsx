import React, { useState, useEffect } from "react";
import {
  BookOpen,
  Search,
  Scale,
  Sparkles,
  Copy,
  Check,
  FileText,
  Upload,
  Download,
  Filter,
  ExternalLink,
  ChevronRight,
  ShieldAlert,
  HelpCircle,
  PlusCircle,
  Quote,
  Building,
  Gavel
} from "lucide-react";
import { caseApi } from "../case-api";

interface PrecedentItem {
  id: string;
  title: string;
  citation: string;
  court: string;
  bench: string;
  year: number;
  category: string;
  relevance_tags: string[];
  ratio_decidendi: string;
  court_submission_quote: string;
  paragraph_citation: string;
  strategic_relevance: string;
  distinguishing_factor: string;
  binding_authority: string;
  full_text?: string;
  search_score?: number;
  snippet?: string;
}

export const JudicialPrecedentsView: React.FC = () => {
  const [precedents, setPrecedents] = useState<PrecedentItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedCourt, setSelectedCourt] = useState("All");
  const [searchMode, setSearchMode] = useState<"bm25" | "tfidf">("bm25");

  // Selection & Modals
  const [selectedPrec, setSelectedPrec] = useState<PrecedentItem | null>(null);
  const [copiedQuoteId, setCopiedQuoteId] = useState<string | null>(null);
  const [copiedCitationId, setCopiedCitationId] = useState<string | null>(null);

  // Ingestion Modal
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newCitation, setNewCitation] = useState("");
  const [newCourt, setNewCourt] = useState("High Court of Delhi / Commercial Division");
  const [newCategory, setNewCategory] = useState("Commercial Breach");
  const [newText, setNewText] = useState("");
  const [ingesting, setIngesting] = useState(false);

  // Submission Sheet Modal
  const [showSheetModal, setShowSheetModal] = useState(false);
  const [sheetMarkdown, setSheetMarkdown] = useState("");
  const [sheetLoading, setSheetLoading] = useState(false);

  // Active Cases for attachment
  const [cases, setCases] = useState<any[]>([]);
  const [attachCaseId, setAttachCaseId] = useState<string>("");
  const [attachingId, setAttachingId] = useState<string | null>(null);
  const [attachSuccess, setAttachSuccess] = useState<string | null>(null);

  const categories = [
    "All",
    "Liquidated Damages & Forfeiture",
    "Unilateral Deductions & Due Process",
    "Defect Liability & Site Inspection Estoppel",
    "Contractual Breach & Liquidated Damages",
    "Interim Measures in Arbitration",
    "Contract Amendments & Timeline Extension"
  ];

  const courts = [
    "All",
    "Supreme Court of India",
    "High Court of Delhi (Commercial Division)",
    "High Court of Bombay (Commercial Division)"
  ];

  const fetchPrecedents = async () => {
    setLoading(true);
    try {
      const data = await caseApi.searchPrecedents(
        searchQuery,
        selectedCategory,
        selectedCourt,
        searchMode
      );
      setPrecedents(data);
    } catch (err) {
      console.error("Failed to load judicial precedents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrecedents();
  }, [selectedCategory, selectedCourt, searchMode]);

  useEffect(() => {
    // Load cases for 1-click attachment
    caseApi.listCases().then(setCases).catch(() => {});
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPrecedents();
  };

  const handleCopyQuote = (id: string, quote: string, ref: string) => {
    const textToCopy = `"${quote}" — ${ref}`;
    navigator.clipboard.writeText(textToCopy);
    setCopiedQuoteId(id);
    setTimeout(() => setCopiedQuoteId(null), 2500);
  };

  const handleCopyCitation = (id: string, title: string, citation: string, court: string) => {
    const textToCopy = `${title}, ${citation} (${court})`;
    navigator.clipboard.writeText(textToCopy);
    setCopiedCitationId(id);
    setTimeout(() => setCopiedCitationId(null), 2500);
  };

  const handleIngestJudgment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newText.trim() || !newTitle.trim()) return;
    setIngesting(true);
    try {
      const created = await caseApi.analyzeJudgment({
        title: newTitle,
        citation: newCitation,
        court: newCourt,
        text: newText,
        category: newCategory
      });
      setShowIngestModal(false);
      setNewTitle("");
      setNewCitation("");
      setNewText("");
      fetchPrecedents();
    } catch (err) {
      alert("Failed to analyze judgment. Please verify text content.");
    } finally {
      setIngesting(false);
    }
  };

  const handleGenerateSheet = async () => {
    setShowSheetModal(true);
    setSheetLoading(true);
    try {
      const ids = precedents.map((p) => p.id);
      const res = await caseApi.generateSubmissionSheet(ids);
      setSheetMarkdown(res.markdown);
    } catch (err) {
      setSheetMarkdown("Failed to compile submission sheet.");
    } finally {
      setSheetLoading(false);
    }
  };

  const handleAttachPrecedent = async (precId: string) => {
    if (!attachCaseId) {
      alert("Please select a target case from the dropdown first.");
      return;
    }
    setAttachingId(precId);
    try {
      await caseApi.attachPrecedentToCase(attachCaseId, precId);
      setAttachSuccess(precId);
      setTimeout(() => setAttachSuccess(null), 3000);
    } catch (err) {
      alert("Failed to attach precedent to case authorities.");
    } finally {
      setAttachingId(null);
    }
  };

  return (
    <div style={{ maxWidth: 1240, margin: "0 auto", padding: "24px 16px" }}>
      {/* Top Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          marginBottom: 24,
          flexWrap: "wrap",
          gap: 16
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: 8,
                background: "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff"
              }}
            >
              <Gavel size={20} />
            </div>
            <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, color: "#0f172a" }}>
              Judicial Records & Precedent Intelligence
            </h1>
          </div>
          <p style={{ margin: 0, color: "#64748b", fontSize: 14 }}>
            Case law research engine: automated ratio decidendi extraction, binding courtroom quotes,
            distinguishing risk analysis, and 1-click submission sheet compilation.
          </p>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={() => setShowIngestModal(true)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "10px 16px",
              background: "#fff",
              border: "1px solid #cbd5e1",
              borderRadius: 8,
              fontWeight: 600,
              fontSize: 13,
              color: "#334155",
              cursor: "pointer",
              boxShadow: "0 1px 2px rgba(0,0,0,0.05)"
            }}
          >
            <Upload size={16} color="#64748b" />
            Analyze Past Judgment
          </button>

          <button
            onClick={handleGenerateSheet}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "10px 18px",
              background: "#1e3a8a",
              border: "none",
              borderRadius: 8,
              fontWeight: 600,
              fontSize: 13,
              color: "#fff",
              cursor: "pointer",
              boxShadow: "0 2px 4px rgba(30,58,138,0.25)"
            }}
          >
            <FileText size={16} />
            Court Submission Sheet
          </button>
        </div>
      </div>

      {/* Target Case Selection Banner */}
      <div
        style={{
          background: "#f8fafc",
          border: "1px solid #e2e8f0",
          borderRadius: 8,
          padding: "10px 16px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 20,
          gap: 12,
          flexWrap: "wrap"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "#475569" }}>
          <Building size={16} color="#3b82f6" />
          <span>
            <strong>Active Target Case:</strong> Link verified precedents directly into your case brief
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <select
            value={attachCaseId}
            onChange={(e) => setAttachCaseId(e.target.value)}
            style={{
              padding: "6px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 13,
              background: "#fff",
              color: "#0f172a",
              minWidth: 260
            }}
          >
            <option value="">-- Select Case to Link Authorities --</option>
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title} ({c.reference})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Search Bar & Multi-Mode Filters */}
      <div
        style={{
          background: "#fff",
          border: "1px solid #e2e8f0",
          borderRadius: 12,
          padding: "18px 20px",
          marginBottom: 24,
          boxShadow: "0 1px 3px rgba(0,0,0,0.04)"
        }}
      >
        <form onSubmit={handleSearchSubmit} style={{ display: "flex", gap: 10, marginBottom: 16 }}>
          <div style={{ position: "relative", flex: 1 }}>
            <Search
              size={18}
              style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "#94a3b8" }}
            />
            <input
              type="text"
              placeholder="Search precedents by keyword, legal ratio, case title, or neutral citation (e.g., 'unilateral deduction', 'Kailash Nath', '(2019) 5 SCC 341')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: "100%",
                padding: "11px 14px 11px 42px",
                border: "1px solid #cbd5e1",
                borderRadius: 8,
                fontSize: 14,
                boxSizing: "border-box",
                outline: "none"
              }}
            />
          </div>
          <button
            type="submit"
            style={{
              padding: "10px 22px",
              background: "#2563eb",
              border: "none",
              borderRadius: 8,
              color: "#fff",
              fontWeight: 600,
              fontSize: 14,
              cursor: "pointer"
            }}
          >
            Search Case Law
          </button>
        </form>

        {/* Filter Controls Row */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          {/* Category Chips */}
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginRight: 4 }}>Legal Issue:</span>
            {categories.slice(0, 5).map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                style={{
                  padding: "5px 10px",
                  borderRadius: 20,
                  fontSize: 12,
                  fontWeight: 500,
                  cursor: "pointer",
                  border: selectedCategory === cat ? "1px solid #2563eb" : "1px solid #e2e8f0",
                  background: selectedCategory === cat ? "#eff6ff" : "#fff",
                  color: selectedCategory === cat ? "#1d4ed8" : "#475569"
                }}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Court & Mode Selectors */}
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>Court:</span>
              <select
                value={selectedCourt}
                onChange={(e) => setSelectedCourt(e.target.value)}
                style={{
                  padding: "5px 10px",
                  borderRadius: 6,
                  border: "1px solid #cbd5e1",
                  fontSize: 12,
                  background: "#fff",
                  color: "#334155"
                }}
              >
                {courts.map((ct) => (
                  <option key={ct} value={ct}>
                    {ct}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>Ranking:</span>
              <select
                value={searchMode}
                onChange={(e) => setSearchMode(e.target.value as any)}
                style={{
                  padding: "5px 10px",
                  borderRadius: 6,
                  border: "1px solid #cbd5e1",
                  fontSize: 12,
                  background: "#fff",
                  color: "#334155"
                }}
              >
                <option value="bm25">BM25 Relevance</option>
                <option value="tfidf">TF-IDF Vector</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Precedent Cards List */}
      {loading ? (
        <div style={{ padding: 48, textAlign: "center", color: "#64748b" }}>Searching case law database...</div>
      ) : precedents.length === 0 ? (
        <div
          style={{
            background: "#fff",
            border: "1px solid #e2e8f0",
            borderRadius: 12,
            padding: 48,
            textAlign: "center"
          }}
        >
          <BookOpen size={36} color="#94a3b8" style={{ margin: "0 auto 12px" }} />
          <h3 style={{ margin: "0 0 6px", fontSize: 16, color: "#1e293b" }}>No precedents matched your query</h3>
          <p style={{ margin: "0 0 16px", color: "#64748b", fontSize: 14 }}>
            Try adjusting your search terms or reset the filters to browse all landmark authorities.
          </p>
          <button
            onClick={() => {
              setSearchQuery("");
              setSelectedCategory("All");
              setSelectedCourt("All");
            }}
            style={{
              padding: "8px 16px",
              background: "#f1f5f9",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              fontSize: 13,
              cursor: "pointer"
            }}
          >
            Reset All Filters
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          {precedents.map((p) => {
            const isBindingSupreme = p.binding_authority === "BINDING_APEX_COURT";
            const isBindingHC = p.binding_authority === "BINDING_DELHI_HC";

            return (
              <div
                key={p.id}
                style={{
                  background: "#fff",
                  border: "1px solid #e2e8f0",
                  borderRadius: 12,
                  padding: "22px 24px",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
                  transition: "border-color 0.15s ease"
                }}
              >
                {/* Header Row */}
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    marginBottom: 12,
                    flexWrap: "wrap",
                    gap: 10
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <span
                        style={{
                          fontSize: 11,
                          fontWeight: 700,
                          textTransform: "uppercase",
                          padding: "3px 8px",
                          borderRadius: 4,
                          background: isBindingSupreme ? "#fef3c7" : isBindingHC ? "#dbeafe" : "#f1f5f9",
                          color: isBindingSupreme ? "#92400e" : isBindingHC ? "#1e40af" : "#475569"
                        }}
                      >
                        {isBindingSupreme
                          ? "Supreme Court Landmark"
                          : isBindingHC
                          ? "Binding Commercial HC"
                          : "High Court Authority"}
                      </span>
                      <span style={{ fontSize: 13, color: "#64748b", fontWeight: 500 }}>
                        {p.court} ({p.year})
                      </span>
                      {p.search_score !== undefined && (
                        <span
                          style={{
                            fontSize: 11,
                            background: "#ecfdf5",
                            color: "#065f46",
                            padding: "2px 6px",
                            borderRadius: 4,
                            fontWeight: 600
                          }}
                        >
                          Score: {p.search_score.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <h3 style={{ fontSize: 18, fontWeight: 700, margin: "0 0 4px", color: "#0f172a" }}>
                      {p.title}
                    </h3>
                    <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 13, color: "#475569" }}>
                      <span>
                        Citation: <strong>{p.citation}</strong>
                      </span>
                      <span>•</span>
                      <span>Bench: {p.bench}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div style={{ display: "flex", gap: 8 }}>
                    <button
                      onClick={() => handleCopyCitation(p.id, p.title, p.citation, p.court)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 5,
                        padding: "6px 12px",
                        background: "#f8fafc",
                        border: "1px solid #cbd5e1",
                        borderRadius: 6,
                        fontSize: 12,
                        fontWeight: 600,
                        color: "#334155",
                        cursor: "pointer"
                      }}
                      title="Copy full legal citation"
                    >
                      {copiedCitationId === p.id ? <Check size={14} color="#16a34a" /> : <Copy size={14} />}
                      {copiedCitationId === p.id ? "Copied" : "Citation"}
                    </button>

                    <button
                      onClick={() => handleAttachPrecedent(p.id)}
                      disabled={attachingId === p.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 5,
                        padding: "6px 14px",
                        background: attachSuccess === p.id ? "#16a34a" : "#1e3a8a",
                        border: "none",
                        borderRadius: 6,
                        fontSize: 12,
                        fontWeight: 600,
                        color: "#fff",
                        cursor: "pointer"
                      }}
                    >
                      {attachSuccess === p.id ? (
                        <>
                          <Check size={14} /> Linked to Case
                        </>
                      ) : (
                        <>
                          <PlusCircle size={14} /> Link to Case
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Tag Pills */}
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 14 }}>
                  {p.relevance_tags.map((t) => (
                    <span
                      key={t}
                      style={{
                        fontSize: 11,
                        background: "#f1f5f9",
                        color: "#475569",
                        padding: "2px 8px",
                        borderRadius: 4
                      }}
                    >
                      #{t}
                    </span>
                  ))}
                </div>

                {/* Ratio Decidendi (Key Holding) */}
                <div
                  style={{
                    background: "#f8fafc",
                    borderLeft: "4px solid #2563eb",
                    borderRadius: "0 8px 8px 0",
                    padding: "12px 16px",
                    marginBottom: 14
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      fontSize: 12,
                      fontWeight: 700,
                      color: "#1d4ed8",
                      textTransform: "uppercase",
                      marginBottom: 4
                    }}
                  >
                    <Scale size={14} />
                    Ratio Decidendi (Core Legal Holding)
                  </div>
                  <p style={{ margin: 0, fontSize: 14, color: "#1e293b", lineHeight: 1.55 }}>
                    {p.ratio_decidendi}
                  </p>
                </div>

                {/* Court Submission Quote */}
                <div
                  style={{
                    background: "#fdf8f6",
                    border: "1px solid #fed7aa",
                    borderRadius: 8,
                    padding: "12px 16px",
                    marginBottom: 14,
                    position: "relative"
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 6
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, fontWeight: 700, color: "#c2410c" }}>
                      <Quote size={14} />
                      Courtroom Submission Quote ({p.paragraph_citation})
                    </div>
                    <button
                      onClick={() => handleCopyQuote(p.id, p.court_submission_quote, p.citation)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 4,
                        background: "none",
                        border: "none",
                        color: "#9a3412",
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: "pointer",
                        padding: 0
                      }}
                    >
                      {copiedQuoteId === p.id ? <Check size={13} color="#16a34a" /> : <Copy size={13} />}
                      {copiedQuoteId === p.id ? "Copied to Clipboard" : "Copy for Pleading"}
                    </button>
                  </div>
                  <p style={{ margin: 0, fontStyle: "italic", fontSize: 13.5, color: "#431407", lineHeight: 1.5 }}>
                    "{p.court_submission_quote}"
                  </p>
                </div>

                {/* Strategic Analysis Grid */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 12,
                    fontSize: 13,
                    background: "#fbfcfd",
                    border: "1px solid #f1f5f9",
                    borderRadius: 8,
                    padding: "12px 14px"
                  }}
                >
                  <div>
                    <strong style={{ color: "#047857", display: "flex", alignItems: "center", gap: 4, marginBottom: 2 }}>
                      <Check size={14} /> Why It Supports Your Case
                    </strong>
                    <span style={{ color: "#334155", lineHeight: 1.45 }}>{p.strategic_relevance}</span>
                  </div>
                  <div>
                    <strong style={{ color: "#b91c1c", display: "flex", alignItems: "center", gap: 4, marginBottom: 2 }}>
                      <ShieldAlert size={14} /> Opposing Distinguishing Angle
                    </strong>
                    <span style={{ color: "#475569", lineHeight: 1.45 }}>{p.distinguishing_factor}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal 1: Analyze Past Court Judgment */}
      {showIngestModal && (
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
            zIndex: 9999,
            padding: 16
          }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 12,
              maxWidth: 720,
              width: "100%",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: 24,
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <Sparkles size={20} color="#2563eb" />
                <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>Analyze & Ingest Past Court Judgment</h3>
              </div>
              <button
                onClick={() => setShowIngestModal(false)}
                style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "#64748b" }}
              >
                ×
              </button>
            </div>
            <p style={{ margin: "0 0 18px", color: "#64748b", fontSize: 13 }}>
              Paste judgment text or key judicial findings. The AI engine will automatically extract the Ratio
              Decidendi, courtroom submission quotes, and index it into your searchable authorities database.
            </p>

            <form onSubmit={handleIngestJudgment}>
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
                  Case Title & Parties *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Larsen & Toubro Ltd. v. State of Maharashtra"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: 6, fontSize: 13 }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
                <div>
                  <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
                    Neutral Citation
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. (2023) 7 SCC 410"
                    value={newCitation}
                    onChange={(e) => setNewCitation(e.target.value)}
                    style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: 6, fontSize: 13 }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
                    Court / Forum
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. High Court of Delhi"
                    value={newCourt}
                    onChange={(e) => setNewCourt(e.target.value)}
                    style={{ width: "100%", padding: "8px 12px", border: "1px solid #cbd5e1", borderRadius: 6, fontSize: 13 }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
                  Full Judgment Text or Headnote Extracts *
                </label>
                <textarea
                  required
                  rows={8}
                  placeholder="Paste the relevant paragraphs, operative findings, or full judgment text here..."
                  value={newText}
                  onChange={(e) => setNewText(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", border: "1px solid #cbd5e1", borderRadius: 6, fontSize: 13, fontFamily: "monospace" }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <button
                  type="button"
                  onClick={() => setShowIngestModal(false)}
                  style={{ padding: "8px 16px", background: "#f1f5f9", border: "none", borderRadius: 6, fontSize: 13, cursor: "pointer" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={ingesting}
                  style={{
                    padding: "8px 20px",
                    background: "#2563eb",
                    border: "none",
                    borderRadius: 6,
                    color: "#fff",
                    fontWeight: 600,
                    fontSize: 13,
                    cursor: "pointer"
                  }}
                >
                  {ingesting ? "Extracting & Indexing..." : "Analyze & Add Precedent"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: Court Submission Sheet */}
      {showSheetModal && (
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
            zIndex: 9999,
            padding: 16
          }}
        >
          <div
            style={{
              background: "#fff",
              borderRadius: 12,
              maxWidth: 820,
              width: "100%",
              maxHeight: "90vh",
              display: "flex",
              flexDirection: "column",
              padding: 24,
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <FileText size={20} color="#1e3a8a" />
                <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>
                  Court Submission Sheet & Table of Authorities
                </h3>
              </div>
              <button
                onClick={() => setShowSheetModal(false)}
                style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "#64748b" }}
              >
                ×
              </button>
            </div>

            <p style={{ margin: "0 0 14px", color: "#64748b", fontSize: 13 }}>
              Ready-to-file compilation of legal authorities, ratio decidendi, and paragraph citations formatted for
              inclusion in arbitral statements of claim or high court written submissions.
            </p>

            <div
              style={{
                flex: 1,
                overflowY: "auto",
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                borderRadius: 8,
                padding: 16,
                marginBottom: 16,
                fontFamily: "monospace",
                fontSize: 12,
                whiteSpace: "pre-wrap",
                color: "#1e293b"
              }}
            >
              {sheetLoading ? "Generating compilation..." : sheetMarkdown}
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 12, color: "#64748b" }}>
                Includes {precedents.length} verified judicial authorities
              </span>
              <div style={{ display: "flex", gap: 10 }}>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(sheetMarkdown);
                    alert("Submission sheet copied to clipboard!");
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "8px 16px",
                    background: "#f1f5f9",
                    border: "1px solid #cbd5e1",
                    borderRadius: 6,
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: "pointer"
                  }}
                >
                  <Copy size={14} /> Copy Markdown
                </button>

                <button
                  onClick={() => {
                    const blob = new Blob([sheetMarkdown], { type: "text/markdown;charset=utf-8" });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = url;
                    link.download = "LexVigil_Court_Authorities_Sheet.md";
                    link.click();
                    URL.revokeObjectURL(url);
                  }}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "8px 18px",
                    background: "#1e3a8a",
                    border: "none",
                    borderRadius: 6,
                    fontSize: 13,
                    fontWeight: 600,
                    color: "#fff",
                    cursor: "pointer"
                  }}
                >
                  <Download size={14} /> Download .md
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
