import React, { useEffect, useState } from "react";
import {
  Clock,
  AlertTriangle,
  CheckCircle,
  FileText,
  Calendar,
  ShieldAlert,
  ChevronRight,
  Filter,
  Plus,
  RefreshCw,
} from "lucide-react";
import { caseApi } from "../case-api";
import type { TimelineEvent, InconsistencyItem } from "../case-types";

interface Props {
  caseId: string;
}

export function TimelineInconsistenciesView({ caseId }: Props) {
  const [activeSubTab, setActiveSubTab] = useState<"timeline" | "inconsistencies">("timeline");
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [inconsistencies, setInconsistencies] = useState<InconsistencyItem[]>([]);
  const [loading, setLoading] = useState(true);

  // New event modal
  const [showEventModal, setShowEventModal] = useState(false);
  const [newDate, setNewDate] = useState("");
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newParty, setNewParty] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const [tl, inc] = await Promise.all([
        caseApi.listTimeline(caseId),
        caseApi.listInconsistencies(caseId),
      ]);
      setTimeline(tl);
      setInconsistencies(inc);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [caseId]);

  const handleUpdateStatus = async (iid: string, newStatus: string) => {
    try {
      await caseApi.updateInconsistencyStatus(caseId, iid, newStatus);
      setInconsistencies((prev) =>
        prev.map((item) => (item.id === iid ? { ...item, status: newStatus as any } : item))
      );
    } catch (err: any) {
      alert(err.message || "Failed to update status");
    }
  };

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDate || !newTitle) return;
    try {
      await caseApi.addTimelineEvent(caseId, {
        date_str: newDate,
        title: newTitle,
        description: newDesc,
        party: newParty,
        verification_status: "verified",
      });
      setShowEventModal(false);
      setNewTitle("");
      setNewDesc("");
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to add event");
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Subtab selector */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: "0.5rem", background: "#f1f5f9", padding: "4px", borderRadius: "8px", width: "fit-content" }}>
          <button
            onClick={() => setActiveSubTab("timeline")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeSubTab === "timeline" ? "#ffffff" : "transparent",
              color: activeSubTab === "timeline" ? "#0f172a" : "#64748b",
              boxShadow: activeSubTab === "timeline" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            }}
          >
            <Clock size={15} style={{ verticalAlign: "middle", marginRight: "6px" }} />
            Event Chronology ({timeline.length})
          </button>
          <button
            onClick={() => setActiveSubTab("inconsistencies")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeSubTab === "inconsistencies" ? "#ffffff" : "transparent",
              color: activeSubTab === "inconsistencies" ? "#dc2626" : "#64748b",
              boxShadow: activeSubTab === "inconsistencies" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            }}
          >
            <AlertTriangle size={15} style={{ verticalAlign: "middle", marginRight: "6px" }} />
            Flagged Discrepancies ({inconsistencies.length})
          </button>
        </div>

        {activeSubTab === "timeline" ? (
          <button className="button primary" onClick={() => setShowEventModal(true)} style={{ fontSize: "0.85rem" }}>
            <Plus size={15} /> Add Timeline Event
          </button>
        ) : (
          <button className="button ghost" onClick={loadData} style={{ fontSize: "0.85rem" }}>
            <RefreshCw size={14} /> Refresh Discrepancies
          </button>
        )}
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "3rem", color: "#64748b" }}>Loading timeline data…</div>
      ) : activeSubTab === "timeline" ? (
        /* Chronological Timeline Track */
        <div style={{ position: "relative", paddingLeft: "2.5rem", borderLeft: "3px solid #cbd5e1", marginLeft: "1rem" }}>
          {timeline.length === 0 ? (
            <div style={{ color: "#64748b", padding: "2rem" }}>No events on the timeline. Add events or load the demo case.</div>
          ) : (
            timeline.map((evt, idx) => (
              <div key={evt.id || idx} style={{ position: "relative", marginBottom: "2rem" }}>
                {/* Node pin */}
                <div
                  style={{
                    position: "absolute",
                    left: "-3.15rem",
                    top: "4px",
                    width: "18px",
                    height: "18px",
                    borderRadius: "50%",
                    background: "#2563eb",
                    border: "3px solid #ffffff",
                    boxShadow: "0 0 0 2px #93c5fd",
                  }}
                />

                <div
                  style={{
                    background: "#ffffff",
                    borderRadius: "10px",
                    border: "1px solid #e2e8f0",
                    padding: "1rem 1.25rem",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                      <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e40af", background: "#eff6ff", padding: "2px 8px", borderRadius: "4px" }}>
                        {evt.date_str}
                      </span>
                      {evt.party && (
                        <span style={{ fontSize: "0.8rem", color: "#64748b" }}>• Party: {evt.party}</span>
                      )}
                    </div>
                    <span
                      style={{
                        fontSize: "0.75rem",
                        fontWeight: 600,
                        color: evt.verification_status === "verified" ? "#059669" : "#d97706",
                      }}
                    >
                      {evt.verification_status.toUpperCase()}
                    </span>
                  </div>

                  <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "#0f172a", margin: "0 0 0.4rem 0" }}>
                    {evt.title}
                  </h3>
                  <p style={{ fontSize: "0.85rem", color: "#334155", margin: 0, lineHeight: "1.4" }}>
                    {evt.description}
                  </p>

                  {evt.filename && (
                    <div style={{ marginTop: "0.6rem", fontSize: "0.75rem", color: "#64748b", display: "flex", alignItems: "center", gap: "4px" }}>
                      <FileText size={12} /> Source: {evt.filename}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      ) : (
        /* Inconsistencies & Contradictions Explorer */
        <div style={{ display: "grid", gap: "1rem" }}>
          {inconsistencies.length === 0 ? (
            <div style={{ textAlign: "center", padding: "3rem", background: "#f8fafc", borderRadius: "10px", color: "#059669" }}>
              <CheckCircle size={32} style={{ marginBottom: "0.5rem" }} />
              <div style={{ fontWeight: 600 }}>No unresolved inconsistencies detected.</div>
            </div>
          ) : (
            inconsistencies.map((inc) => {
              const isHigh = inc.severity === "HIGH";
              const isMedium = inc.severity === "MEDIUM";
              const statusColor =
                inc.status === "resolved" ? "#059669" : inc.status === "reviewed" ? "#2563eb" : "#dc2626";

              return (
                <div
                  key={inc.id}
                  style={{
                    background: "#ffffff",
                    borderRadius: "10px",
                    border: `1px solid ${isHigh ? "#fecaca" : isMedium ? "#fed7aa" : "#e2e8f0"}`,
                    padding: "1.25rem",
                    borderLeft: `5px solid ${isHigh ? "#dc2626" : isMedium ? "#f97316" : "#64748b"}`,
                    boxShadow: "0 1px 3px rgba(0,0,0,0.03)",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span
                        style={{
                          fontSize: "0.7rem",
                          fontWeight: 700,
                          padding: "2px 6px",
                          borderRadius: "4px",
                          background: isHigh ? "#fee2e2" : "#ffedd5",
                          color: isHigh ? "#b91c1c" : "#c2410c",
                        }}
                      >
                        {inc.severity} SEVERITY
                      </span>
                      <span style={{ fontSize: "0.8rem", color: "#64748b" }}>• {inc.issue_type}</span>
                    </div>

                    <div style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                      <span style={{ fontSize: "0.75rem", fontWeight: 700, color: statusColor, marginRight: "4px" }}>
                        [{inc.status.toUpperCase()}]
                      </span>
                      {inc.status !== "reviewed" && (
                        <button
                          className="button ghost"
                          onClick={() => handleUpdateStatus(inc.id, "reviewed")}
                          style={{ fontSize: "0.75rem", padding: "3px 7px" }}
                        >
                          Mark Reviewed
                        </button>
                      )}
                      {inc.status !== "resolved" && (
                        <button
                          className="button ghost"
                          onClick={() => handleUpdateStatus(inc.id, "resolved")}
                          style={{ fontSize: "0.75rem", padding: "3px 7px", color: "#059669" }}
                        >
                          Resolve
                        </button>
                      )}
                    </div>
                  </div>

                  <h3 style={{ fontSize: "1.05rem", fontWeight: 600, color: "#0f172a", margin: "0 0 0.4rem 0" }}>
                    {inc.title}
                  </h3>
                  <p style={{ fontSize: "0.85rem", color: "#334155", margin: 0, lineHeight: "1.4" }}>
                    {inc.explanation}
                  </p>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Add Event Modal */}
      {showEventModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(15,23,42,0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div style={{ background: "#ffffff", borderRadius: "10px", padding: "1.5rem", width: "450px" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Record Timeline Event</h3>
            <form onSubmit={handleAddEvent}>
              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Date (YYYY-MM-DD) *
                </label>
                <input
                  type="date"
                  required
                  value={newDate}
                  onChange={(e) => setNewDate(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Event Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Tax Invoice Issued or Notice Served"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Party Involved
                </label>
                <input
                  type="text"
                  placeholder="e.g. Claimant, Respondent, Joint Team"
                  value={newParty}
                  onChange={(e) => setNewParty(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Description & Context
                </label>
                <textarea
                  rows={2}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Specific details of the transaction or event…"
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
                <button type="button" className="button ghost" onClick={() => setShowEventModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="button primary">
                  Save Event
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
