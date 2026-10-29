import React, { useEffect, useState } from "react";
import {
  Share2,
  Navigation,
  Info,
  CheckCircle2,
  AlertCircle,
  FileText,
  ArrowRight,
  Filter,
  Plus,
  Compass,
} from "lucide-react";
import { caseApi } from "../case-api";
import type { EvidenceItem, EvidenceRelationship } from "../case-types";

interface Props {
  caseId: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  Contract: "#2563eb",
  Invoice: "#059669",
  Payment: "#10b981",
  Communication: "#8b5cf6",
  Pleading: "#d97706",
  Certificate: "#0284c7",
  Documentary: "#475569",
};

export function EvidenceGraphView({ caseId }: Props) {
  const [items, setItems] = useState<EvidenceItem[]>([]);
  const [relationships, setRelationships] = useState<EvidenceRelationship[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<EvidenceItem | null>(null);

  // Pathfinding state
  const [startNode, setStartNode] = useState<string>("");
  const [targetNode, setTargetNode] = useState<string>("");
  const [algorithm, setAlgorithm] = useState<string>("bfs");
  const [pathResult, setPathResult] = useState<any | null>(null);
  const [pathBusy, setPathBusy] = useState(false);

  // Add Item / Rel modals
  const [showAddRel, setShowAddRel] = useState(false);
  const [newRelSource, setNewRelSource] = useState("");
  const [newRelTarget, setNewRelTarget] = useState("");
  const [newRelType, setNewRelType] = useState("supports");
  const [newRelExpl, setNewRelExpl] = useState("");

  const loadGraphData = async () => {
    try {
      setLoading(true);
      const [evList, relList] = await Promise.all([
        caseApi.listEvidence(caseId),
        caseApi.listRelationships(caseId),
      ]);
      setItems(evList);
      setRelationships(relList);
      if (evList.length >= 2) {
        setStartNode(evList[0].id);
        setTargetNode(evList[evList.length - 1].id);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraphData();
  }, [caseId]);

  const handleRunPathfinding = async () => {
    if (!startNode || !targetNode) return;
    try {
      setPathBusy(true);
      const res = await caseApi.runPathfinding(caseId, {
        algorithm,
        source_id: startNode,
        target_id: targetNode,
      });
      setPathResult(res);
    } catch (err: any) {
      alert(err.message || "Pathfinding search failed");
    } finally {
      setPathBusy(false);
    }
  };

  const handleAddRelationship = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRelSource || !newRelTarget || newRelSource === newRelTarget) {
      alert("Select two distinct evidence items");
      return;
    }
    try {
      await caseApi.createRelationship(caseId, {
        source_id: newRelSource,
        target_id: newRelTarget,
        relation_type: newRelType,
        explanation: newRelExpl || `Relation: ${newRelType}`,
      });
      setShowAddRel(false);
      setNewRelExpl("");
      loadGraphData();
    } catch (err: any) {
      alert(err.message || "Failed to create relation");
    }
  };

  // Node coordinates layout (circular layout for clarity)
  const nodePositions: Record<string, { x: number; y: number }> = {};
  const cx = 380;
  const cy = 250;
  const r = 180;
  items.forEach((item, i) => {
    const angle = (2 * Math.PI * i) / (items.length || 1);
    nodePositions[item.id] = {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  });

  const pathSet = new Set(pathResult?.path || []);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "1.5rem", minHeight: "680px" }}>
      {/* Main Graph & Pathfinding Area */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {/* Pathfinding Control Bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: "#ffffff",
            padding: "0.85rem 1.25rem",
            borderRadius: "10px",
            border: "1px solid #e2e8f0",
            flexWrap: "wrap",
            gap: "0.75rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 600, color: "#1e293b", fontSize: "0.9rem" }}>
            <Compass size={18} color="#2563eb" />
            <span>Evidence Pathfinding:</span>
          </div>

          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <select
              value={startNode}
              onChange={(e) => setStartNode(e.target.value)}
              style={{ fontSize: "0.8rem", padding: "0.4rem 0.6rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            >
              {items.map((it) => (
                <option key={it.id} value={it.id}>
                  From: {it.title.slice(0, 26)}…
                </option>
              ))}
            </select>

            <ArrowRight size={14} color="#64748b" />

            <select
              value={targetNode}
              onChange={(e) => setTargetNode(e.target.value)}
              style={{ fontSize: "0.8rem", padding: "0.4rem 0.6rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
            >
              {items.map((it) => (
                <option key={it.id} value={it.id}>
                  To: {it.title.slice(0, 26)}…
                </option>
              ))}
            </select>

            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              style={{ fontSize: "0.8rem", padding: "0.4rem 0.6rem", borderRadius: "6px", border: "1px solid #cbd5e1", background: "#f8fafc" }}
            >
              <option value="bfs">BFS (Shortest Hops)</option>
              <option value="dfs">DFS (Depth-First)</option>
              <option value="ucs">Uniform-Cost (Lowest Weight)</option>
              <option value="astar">A* Search (Heuristic Guided)</option>
              <option value="greedy">Greedy Best-First</option>
            </select>

            <button
              className="button primary"
              onClick={handleRunPathfinding}
              disabled={pathBusy}
              style={{ padding: "0.4rem 0.85rem", fontSize: "0.85rem" }}
            >
              {pathBusy ? "Searching…" : "Find Path"}
            </button>
          </div>

          <button
            className="button ghost"
            onClick={() => setShowAddRel(true)}
            style={{ fontSize: "0.8rem", display: "flex", alignItems: "center", gap: "4px" }}
          >
            <Plus size={14} /> Add Link
          </button>
        </div>

        {/* SVG Graph Visualizer */}
        <div
          style={{
            position: "relative",
            background: "#ffffff",
            borderRadius: "12px",
            border: "1px solid #e2e8f0",
            overflow: "hidden",
            boxShadow: "inset 0 0 10px rgba(0,0,0,0.02)",
            minHeight: "520px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {loading ? (
            <div style={{ color: "#64748b" }}>Loading evidence graph…</div>
          ) : items.length === 0 ? (
            <div style={{ textAlign: "center", color: "#64748b", padding: "2rem" }}>
              No evidence records found. Ingest case documents or load the demonstration case.
            </div>
          ) : (
            <svg width="100%" height="520" viewBox="0 0 760 500" style={{ userSelect: "none" }}>
              <defs>
                <marker
                  id="arrow"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
                </marker>
                <marker
                  id="arrow-path"
                  viewBox="0 0 10 10"
                  refX="18"
                  refY="5"
                  markerWidth="7"
                  markerHeight="7"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
                </marker>
              </defs>

              {/* Render Relationships / Edges */}
              {relationships.map((rel) => {
                const s = nodePositions[rel.source_id];
                const t = nodePositions[rel.target_id];
                if (!s || !t) return null;

                const isPathEdge =
                  pathResult?.path &&
                  pathResult.path.includes(rel.source_id) &&
                  pathResult.path.includes(rel.target_id);

                const isContradiction = rel.relation_type.toLowerCase().includes("contradict");

                return (
                  <g key={rel.id}>
                    <line
                      x1={s.x}
                      y1={s.y}
                      x2={t.x}
                      y2={t.y}
                      stroke={isPathEdge ? "#2563eb" : isContradiction ? "#ef4444" : "#cbd5e1"}
                      strokeWidth={isPathEdge ? 3.5 : isContradiction ? 2.5 : 1.5}
                      strokeDasharray={isContradiction ? "5,5" : undefined}
                      markerEnd={isPathEdge ? "url(#arrow-path)" : "url(#arrow)"}
                    />
                    <text
                      x={(s.x + t.x) / 2}
                      y={(s.y + t.y) / 2 - 6}
                      fill={isPathEdge ? "#1e40af" : isContradiction ? "#b91c1c" : "#64748b"}
                      fontSize="10"
                      fontWeight={isPathEdge ? 700 : 500}
                      textAnchor="middle"
                      style={{ background: "#ffffff", padding: "1px 4px" }}
                    >
                      {rel.relation_type}
                    </text>
                  </g>
                );
              })}

              {/* Render Evidence Nodes */}
              {items.map((it) => {
                const pos = nodePositions[it.id];
                if (!pos) return null;
                const isSelected = selectedNode?.id === it.id;
                const isInPath = pathSet.has(it.id);
                const color = CATEGORY_COLORS[it.category] || "#475569";

                return (
                  <g
                    key={it.id}
                    transform={`translate(${pos.x}, ${pos.y})`}
                    onClick={() => setSelectedNode(it)}
                    style={{ cursor: "pointer" }}
                  >
                    <circle
                      r={isInPath ? 24 : isSelected ? 22 : 18}
                      fill={isInPath ? "#eff6ff" : "#ffffff"}
                      stroke={isInPath ? "#2563eb" : color}
                      strokeWidth={isInPath ? 4 : isSelected ? 3 : 2}
                    />
                    <circle r={6} fill={color} />
                    <text
                      y={30}
                      textAnchor="middle"
                      fill="#0f172a"
                      fontSize="11"
                      fontWeight={isSelected || isInPath ? 700 : 500}
                    >
                      {it.title.length > 20 ? it.title.slice(0, 18) + "…" : it.title}
                    </text>
                    <text y={42} textAnchor="middle" fill="#64748b" fontSize="9">
                      {it.category}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}

          {/* Graph Legend */}
          <div
            style={{
              position: "absolute",
              bottom: "12px",
              left: "14px",
              background: "rgba(255,255,255,0.9)",
              padding: "6px 12px",
              borderRadius: "6px",
              fontSize: "0.75rem",
              color: "#64748b",
              display: "flex",
              gap: "12px",
              border: "1px solid #e2e8f0",
            }}
          >
            <span>● Blue: Contract</span>
            <span>● Green: Payment/Invoice</span>
            <span>● Purple: Communication</span>
            <span>-- Red: Contradiction</span>
          </div>
        </div>

        {/* Path Search Trace Output */}
        {pathResult && (
          <div
            style={{
              background: "#ffffff",
              borderRadius: "10px",
              border: "1px solid #e2e8f0",
              padding: "1rem 1.25rem",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
              <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b" }}>
                Path Result: {pathResult.algorithm}
              </span>
              <span style={{ fontSize: "0.75rem", color: pathResult.found ? "#059669" : "#dc2626", fontWeight: 600 }}>
                {pathResult.found ? `Path Discovered (${pathResult.path_length} nodes)` : "No path connects these evidence items"}
              </span>
            </div>

            {pathResult.found && (
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap", fontSize: "0.85rem", marginBottom: "0.75rem" }}>
                <b>Chain:</b>
                {pathResult.path_nodes?.map((pNode: any, idx: number) => (
                  <React.Fragment key={pNode.id}>
                    <span
                      onClick={() => setSelectedNode(pNode)}
                      style={{
                        padding: "3px 8px",
                        borderRadius: "4px",
                        background: "#dbeafe",
                        color: "#1e40af",
                        fontWeight: 600,
                        cursor: "pointer",
                      }}
                    >
                      {pNode.title || pNode.id}
                    </span>
                    {idx < pathResult.path_nodes.length - 1 && <ArrowRight size={14} color="#64748b" />}
                  </React.Fragment>
                ))}
              </div>
            )}

            {pathResult.steps && (
              <details style={{ fontSize: "0.8rem", color: "#475569" }}>
                <summary style={{ cursor: "pointer", fontWeight: 600 }}>
                  View Search Steps & Frontier States ({pathResult.steps.length} steps)
                </summary>
                <div style={{ maxHeight: "160px", overflowY: "auto", marginTop: "0.5rem" }}>
                  {pathResult.steps.map((st: any) => (
                    <div key={st.step} style={{ padding: "3px 0", borderBottom: "1px solid #f1f5f9" }}>
                      <b>Step {st.step}:</b> {st.action} — <i>Frontier: [{st.frontier?.join(", ") || "empty"}]</i>
                    </div>
                  ))}
                </div>
              </details>
            )}
          </div>
        )}
      </div>

      {/* Side Detail Inspector */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div
          style={{
            background: "#ffffff",
            borderRadius: "10px",
            border: "1px solid #e2e8f0",
            padding: "1.25rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: 700, color: "#0f172a", marginBottom: "0.75rem" }}>
            <Info size={18} color="#2563eb" />
            <span>Evidence Details</span>
          </div>

          {selectedNode ? (
            <div>
              <span
                style={{
                  fontSize: "0.7rem",
                  fontWeight: 700,
                  padding: "2px 6px",
                  borderRadius: "4px",
                  background: "#f1f5f9",
                  color: CATEGORY_COLORS[selectedNode.category] || "#475569",
                }}
              >
                {selectedNode.category}
              </span>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 600, margin: "0.4rem 0 0.5rem 0", color: "#0f172a" }}>
                {selectedNode.title}
              </h3>
              <p style={{ fontSize: "0.85rem", color: "#334155", lineHeight: "1.4" }}>
                {selectedNode.description || "No detailed description recorded."}
              </p>

              <div style={{ marginTop: "1rem", paddingTop: "0.8rem", borderTop: "1px solid #f1f5f9", fontSize: "0.8rem", color: "#64748b" }}>
                <div><b>Item ID:</b> {selectedNode.id}</div>
                {selectedNode.filename && (
                  <div style={{ marginTop: "4px", display: "flex", alignItems: "center", gap: "4px" }}>
                    <FileText size={14} /> <b>Source File:</b> {selectedNode.filename}
                  </div>
                )}
                {selectedNode.page && <div><b>Page Reference:</b> Page {selectedNode.page}</div>}
              </div>

              {/* Connected Relationships */}
              <div style={{ marginTop: "1rem" }}>
                <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.4rem" }}>
                  Connected Links:
                </div>
                {relationships
                  .filter((r) => r.source_id === selectedNode.id || r.target_id === selectedNode.id)
                  .map((r) => {
                    const isOutgoing = r.source_id === selectedNode.id;
                    const otherId = isOutgoing ? r.target_id : r.source_id;
                    const otherItem = items.find((it) => it.id === otherId);
                    return (
                      <div
                        key={r.id}
                        style={{
                          fontSize: "0.75rem",
                          padding: "6px 8px",
                          borderRadius: "4px",
                          background: "#f8fafc",
                          marginBottom: "4px",
                          border: "1px solid #e2e8f0",
                        }}
                      >
                        <span style={{ fontWeight: 600, color: "#2563eb" }}>
                          {isOutgoing ? `→ ${r.relation_type} →` : `← ${r.relation_type} ←`}
                        </span>{" "}
                        {otherItem?.title || otherId}
                        <div style={{ color: "#64748b", marginTop: "2px" }}>{r.explanation}</div>
                      </div>
                    );
                  })}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center", color: "#64748b", fontSize: "0.85rem", padding: "2rem 0" }}>
              Click any evidence node on the graph to inspect its properties and relationships.
            </div>
          )}
        </div>
      </div>

      {/* Add Relationship Modal */}
      {showAddRel && (
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
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Connect Evidence Items</h3>
            <form onSubmit={handleAddRelationship}>
              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Source Item:
                </label>
                <select
                  value={newRelSource}
                  onChange={(e) => setNewRelSource(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  required
                >
                  <option value="">Select source…</option>
                  {items.map((it) => (
                    <option key={it.id} value={it.id}>{it.title}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Relationship Type:
                </label>
                <select
                  value={newRelType}
                  onChange={(e) => setNewRelType(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                >
                  <option value="supports">supports</option>
                  <option value="contradicts">contradicts</option>
                  <option value="governs">governs</option>
                  <option value="triggered">triggered</option>
                  <option value="partially_satisfied_by">partially_satisfied_by</option>
                  <option value="depends_on">depends_on</option>
                  <option value="refers_to">refers_to</option>
                </select>
              </div>

              <div style={{ marginBottom: "0.8rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Target Item:
                </label>
                <select
                  value={newRelTarget}
                  onChange={(e) => setNewRelTarget(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  required
                >
                  <option value="">Select target…</option>
                  {items.map((it) => (
                    <option key={it.id} value={it.id}>{it.title}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: "1rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                  Factual Explanation:
                </label>
                <textarea
                  rows={2}
                  value={newRelExpl}
                  onChange={(e) => setNewRelExpl(e.target.value)}
                  placeholder="Explain why these two items are connected…"
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
                <button type="button" className="button ghost" onClick={() => setShowAddRel(false)}>
                  Cancel
                </button>
                <button type="submit" className="button primary">
                  Save Connection
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
