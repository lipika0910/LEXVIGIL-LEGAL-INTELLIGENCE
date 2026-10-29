import React, { useState, useEffect } from "react";
import { Search, FileText, ArrowRight, Sparkles, Filter, BookOpen } from "lucide-react";
import { caseApi } from "../case-api";
import type { CaseDocument } from "../case-types";

interface Props {
  caseId: string;
  onOpenDocument?: (docId: string) => void;
}

export function SearchModule({ caseId, onOpenDocument }: Props) {
  const [query, setQuery] = useState("");
  const [method, setMethod] = useState("bm25");
  const [docFilter, setDocFilter] = useState("");
  const [documents, setDocuments] = useState<CaseDocument[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [searched, setSearched] = useState(false);

  useEffect(() => {
    caseApi.listDocuments(caseId).then(setDocuments).catch(() => {});
  }, [caseId]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    try {
      setBusy(true);
      const res = await caseApi.searchCase(caseId, query.trim(), method, docFilter || undefined);
      setResults(res);
      setSearched(true);
    } catch (err: any) {
      alert(err.message || "Search failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Search Header & Inputs */}
      <div
        style={{
          background: "#ffffff",
          padding: "1.5rem",
          borderRadius: "10px",
          border: "1px solid #e2e8f0",
          boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
        }}
      >
        <form onSubmit={handleSearch}>
          <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem" }}>
            <div style={{ position: "relative", flex: 1 }}>
              <Search size={18} style={{ position: "absolute", left: "12px", top: "12px", color: "#94a3b8" }} />
              <input
                type="text"
                placeholder="Enter search terms (e.g. 'milestone payment', 'section 73', 'due date', 'foundation')..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{
                  width: "100%",
                  height: "44px",
                  paddingLeft: "2.4rem",
                  paddingRight: "1rem",
                  borderRadius: "8px",
                  border: "1px solid #cbd5e1",
                  fontSize: "0.95rem",
                }}
              />
            </div>
            <button className="button primary" type="submit" disabled={busy} style={{ height: "44px", minWidth: "120px" }}>
              {busy ? "Searching…" : "Search Case"}
            </button>
          </div>

          <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap", alignItems: "center", fontSize: "0.85rem", color: "#475569" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <b>Retrieval Method:</b>
              <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                <input
                  type="radio"
                  name="method"
                  value="bm25"
                  checked={method === "bm25"}
                  onChange={() => setMethod("bm25")}
                />
                BM25 Probabilistic
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                <input
                  type="radio"
                  name="method"
                  value="tfidf"
                  checked={method === "tfidf"}
                  onChange={() => setMethod("tfidf")}
                />
                TF-IDF Vector
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                <input
                  type="radio"
                  name="method"
                  value="exact"
                  checked={method === "exact"}
                  onChange={() => setMethod("exact")}
                />
                Exact Substring
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer" }}>
                <input
                  type="radio"
                  name="method"
                  value="phrase"
                  checked={method === "phrase"}
                  onChange={() => setMethod("phrase")}
                />
                Phrase Match
              </label>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <b>Scope:</b>
              <select
                value={docFilter}
                onChange={(e) => setDocFilter(e.target.value)}
                style={{ height: "32px", borderRadius: "6px", border: "1px solid #cbd5e1", fontSize: "0.8rem", background: "#ffffff" }}
              >
                <option value="">All Case Documents</option>
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.filename}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Results List */}
      <div>
        {searched && (
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "0.9rem", fontWeight: 600, color: "#1e293b" }}>
              {results.length} document {results.length === 1 ? "match" : "matches"} found
            </span>
            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Ranked by {method.toUpperCase()} score</span>
          </div>
        )}

        {searched && results.length === 0 ? (
          <div style={{ textAlign: "center", padding: "3rem", background: "#f8fafc", borderRadius: "10px", border: "1px solid #e2e8f0", color: "#64748b" }}>
            No matching passages found for "{query}". Try broader search terms or exact matching.
          </div>
        ) : (
          <div style={{ display: "grid", gap: "1rem" }}>
            {results.map((r, idx) => (
              <div
                key={r.doc_id || idx}
                style={{
                  background: "#ffffff",
                  borderRadius: "10px",
                  border: "1px solid #e2e8f0",
                  padding: "1.25rem",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <FileText size={16} color="#2563eb" />
                    <span style={{ fontWeight: 700, fontSize: "1rem", color: "#0f172a" }}>{r.title}</span>
                    <span style={{ fontSize: "0.75rem", padding: "2px 6px", borderRadius: "4px", background: "#f1f5f9", color: "#475569" }}>
                      Score: {r.score}
                    </span>
                  </div>

                  {onOpenDocument && (
                    <button
                      className="button ghost"
                      onClick={() => onOpenDocument(r.doc_id)}
                      style={{ fontSize: "0.8rem", padding: "4px 8px" }}
                    >
                      View Source Document <ArrowRight size={14} />
                    </button>
                  )}
                </div>

                <div style={{ fontSize: "0.8rem", color: "#64748b", marginBottom: "0.75rem" }}>
                  <b>Ranking Reason:</b> {r.explanation}
                </div>

                {/* Highlighted Snippets */}
                <div style={{ display: "grid", gap: "0.5rem" }}>
                  {r.snippets?.map((snip: string, sIdx: number) => (
                    <div
                      key={sIdx}
                      style={{
                        padding: "0.6rem 0.85rem",
                        background: "#f8fafc",
                        borderRadius: "6px",
                        fontSize: "0.85rem",
                        lineHeight: "1.5",
                        color: "#334155",
                        borderLeft: "3px solid #2563eb",
                      }}
                    >
                      {snip}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
