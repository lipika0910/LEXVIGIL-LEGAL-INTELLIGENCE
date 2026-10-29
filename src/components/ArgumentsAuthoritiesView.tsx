import React, { useEffect, useState } from "react";
import { Scale, BookOpen, Plus, ShieldCheck, ExternalLink, ArrowRight } from "lucide-react";
import { caseApi } from "../case-api";
import type { ArgumentItem, LegalAuthority } from "../case-types";

interface Props {
  caseId: string;
}

export function ArgumentsAuthoritiesView({ caseId }: Props) {
  const [activeSubTab, setActiveSubTab] = useState<"arguments" | "authorities">("arguments");
  const [argumentsList, setArgumentsList] = useState<ArgumentItem[]>([]);
  const [authorities, setAuthorities] = useState<LegalAuthority[]>([]);
  const [loading, setLoading] = useState(true);

  // New argument modal
  const [showArgModal, setShowArgModal] = useState(false);
  const [argIssue, setArgIssue] = useState("");
  const [argText, setArgText] = useState("");
  const [argAssumptions, setArgAssumptions] = useState("");
  const [argCounter, setArgCounter] = useState("");

  // New authority modal
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authTitle, setAuthTitle] = useState("");
  const [authCitation, setAuthCitation] = useState("");
  const [authJurisdiction, setAuthJurisdiction] = useState("India (Central)");
  const [authType, setAuthType] = useState("Statute");
  const [authUrl, setAuthUrl] = useState("");
  const [authNotes, setAuthNotes] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [args, auths] = await Promise.all([
        caseApi.listArguments(caseId),
        caseApi.listAuthorities(caseId),
      ]);
      setArgumentsList(args);
      setAuthorities(auths);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [caseId]);

  const handleAddArgument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!argIssue || !argText) return;
    try {
      await caseApi.addArgument(caseId, {
        issue_title: argIssue,
        argument_text: argText,
        assumptions: argAssumptions,
        counterarguments: argCounter,
        status: "proposed",
      });
      setShowArgModal(false);
      setArgIssue("");
      setArgText("");
      setArgAssumptions("");
      setArgCounter("");
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to add argument");
    }
  };

  const handleAddAuthority = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authTitle || !authCitation) return;
    try {
      await caseApi.addAuthority(caseId, {
        title: authTitle,
        citation: authCitation,
        jurisdiction: authJurisdiction,
        authority_type: authType,
        url: authUrl,
        notes: authNotes,
        verification_status: "verified",
      });
      setShowAuthModal(false);
      setAuthTitle("");
      setAuthCitation("");
      setAuthUrl("");
      setAuthNotes("");
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to add authority");
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Subtab Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: "0.5rem", background: "#f1f5f9", padding: "4px", borderRadius: "8px" }}>
          <button
            onClick={() => setActiveSubTab("arguments")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeSubTab === "arguments" ? "#ffffff" : "transparent",
              color: activeSubTab === "arguments" ? "#2563eb" : "#64748b",
              boxShadow: activeSubTab === "arguments" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            }}
          >
            <Scale size={15} style={{ verticalAlign: "middle", marginRight: "6px" }} />
            Arguments & Counterarguments ({argumentsList.length})
          </button>
          <button
            onClick={() => setActiveSubTab("authorities")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeSubTab === "authorities" ? "#ffffff" : "transparent",
              color: activeSubTab === "authorities" ? "#2563eb" : "#64748b",
              boxShadow: activeSubTab === "authorities" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            }}
          >
            <BookOpen size={15} style={{ verticalAlign: "middle", marginRight: "6px" }} />
            Legal Authorities ({authorities.length})
          </button>
        </div>

        {activeSubTab === "arguments" ? (
          <button className="button primary" onClick={() => setShowArgModal(true)} style={{ fontSize: "0.85rem" }}>
            <Plus size={15} /> Add Argument
          </button>
        ) : (
          <button className="button primary" onClick={() => setShowAuthModal(true)} style={{ fontSize: "0.85rem" }}>
            <Plus size={15} /> Add Authority
          </button>
        )}
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>Loading records…</div>
      ) : activeSubTab === "arguments" ? (
        /* Arguments & Counterarguments Cards */
        <div style={{ display: "grid", gap: "1rem" }}>
          {argumentsList.length === 0 ? (
            <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", color: "#64748b" }}>
              No arguments created yet. Add arguments to articulate legal theories and counter-risks.
            </div>
          ) : (
            argumentsList.map((arg) => (
              <div
                key={arg.id}
                style={{
                  background: "#ffffff",
                  borderRadius: "10px",
                  border: "1px solid #e2e8f0",
                  padding: "1.25rem",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.6rem" }}>
                  <span style={{ fontSize: "0.75rem", fontWeight: 700, padding: "2px 8px", borderRadius: "4px", background: "#eff6ff", color: "#1e40af" }}>
                    LEGAL ISSUE
                  </span>
                  <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#64748b" }}>
                    [{arg.status?.toUpperCase()}]
                  </span>
                </div>

                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a", margin: "0 0 0.75rem 0" }}>
                  {arg.issue_title}
                </h3>

                {/* Affirmative Argument */}
                <div style={{ marginBottom: "0.75rem" }}>
                  <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#059669", marginBottom: "0.2rem" }}>
                    Affirmative Legal Argument:
                  </div>
                  <p style={{ fontSize: "0.85rem", color: "#1e293b", margin: 0, lineHeight: "1.45" }}>
                    {arg.argument_text}
                  </p>
                </div>

                {/* Counterargument / Risk */}
                {arg.counterarguments && (
                  <div style={{ marginBottom: "0.75rem", background: "#fef2f2", padding: "0.75rem", borderRadius: "6px" }}>
                    <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#b91c1c", marginBottom: "0.2rem" }}>
                      Opposing Counterargument / Risk Factor:
                    </div>
                    <p style={{ fontSize: "0.85rem", color: "#7f1d1d", margin: 0, lineHeight: "1.45" }}>
                      {arg.counterarguments}
                    </p>
                  </div>
                )}

                {/* Assumptions */}
                {arg.assumptions && (
                  <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.5rem" }}>
                    <b>Underlying Assumptions:</b> {arg.assumptions}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        /* Legal Authorities List */
        <div style={{ display: "grid", gap: "1rem" }}>
          {authorities.length === 0 ? (
            <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", color: "#64748b" }}>
              No legal authorities recorded. Add statutory sections or judicial precedents.
            </div>
          ) : (
            authorities.map((au) => (
              <div
                key={au.id}
                style={{
                  background: "#ffffff",
                  borderRadius: "10px",
                  border: "1px solid #e2e8f0",
                  padding: "1.25rem",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, padding: "2px 8px", borderRadius: "4px", background: "#f1f5f9", color: "#334155" }}>
                      {au.authority_type}
                    </span>
                    <span style={{ fontSize: "0.8rem", color: "#64748b" }}>• Jurisdiction: {au.jurisdiction}</span>
                  </div>

                  <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#059669" }}>
                    [VERIFIED]
                  </span>
                </div>

                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a", margin: "0 0 0.2rem 0" }}>
                  {au.title}
                </h3>
                <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "#2563eb", marginBottom: "0.6rem" }}>
                  {au.citation}
                </div>

                <p style={{ fontSize: "0.85rem", color: "#334155", margin: "0 0 0.6rem 0", lineHeight: "1.45" }}>
                  {au.notes}
                </p>

                {au.url && (
                  <a
                    href={au.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ fontSize: "0.75rem", color: "#2563eb", display: "inline-flex", alignItems: "center", gap: "4px", textDecoration: "none" }}
                  >
                    Official Portal Link <ExternalLink size={12} />
                  </a>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Add Argument Modal */}
      {showArgModal && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(15,23,42,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: "#ffffff", borderRadius: "10px", padding: "1.5rem", width: "500px" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Record Legal Argument</h3>
            <form onSubmit={handleAddArgument}>
              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Legal Issue Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Entitlement to Unpaid Milestone Balance"
                  value={argIssue}
                  onChange={(e) => setArgIssue(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Affirmative Argument *</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Detailed affirmative reasoning based on contractual clauses and performance facts…"
                  value={argText}
                  onChange={(e) => setArgText(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Counterargument / Opposition Risk</label>
                <textarea
                  rows={2}
                  placeholder="Anticipated defense or counter-allegation from opposing party…"
                  value={argCounter}
                  onChange={(e) => setArgCounter(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Underlying Assumptions</label>
                <input
                  type="text"
                  placeholder="e.g. Works complied with specs; notice delivery proved"
                  value={argAssumptions}
                  onChange={(e) => setArgAssumptions(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
                <button type="button" className="button ghost" onClick={() => setShowArgModal(false)}>Cancel</button>
                <button type="submit" className="button primary">Save Argument</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Authority Modal */}
      {showAuthModal && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(15,23,42,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: "#ffffff", borderRadius: "10px", padding: "1.5rem", width: "500px" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Record Legal Authority</h3>
            <form onSubmit={handleAddAuthority}>
              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Authority Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Section 73, Indian Contract Act, 1872"
                  value={authTitle}
                  onChange={(e) => setAuthTitle(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem", marginBottom: "0.8rem" }}>
                <div>
                  <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Citation *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Act 9 of 1872 / (2019) 5 SCC 341"
                    value={authCitation}
                    onChange={(e) => setAuthCitation(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Authority Type</label>
                  <select
                    value={authType}
                    onChange={(e) => setAuthType(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1", background: "#ffffff" }}
                  >
                    <option value="Statute">Statute</option>
                    <option value="Judicial Precedent">Judicial Precedent</option>
                    <option value="Regulation">Regulation / Notification</option>
                    <option value="Treatise">Legal Treatise / Commentary</option>
                  </select>
                </div>
              </div>
              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Official URL</label>
                <input
                  type="url"
                  placeholder="e.g. https://www.indiacode.nic.in/..."
                  value={authUrl}
                  onChange={(e) => setAuthUrl(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>Application & Notes</label>
                <textarea
                  rows={2}
                  placeholder="Summary of legal principle, relevance to this case, and applicability limits…"
                  value={authNotes}
                  onChange={(e) => setAuthNotes(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
                <button type="button" className="button ghost" onClick={() => setShowAuthModal(false)}>Cancel</button>
                <button type="submit" className="button primary">Save Authority</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
