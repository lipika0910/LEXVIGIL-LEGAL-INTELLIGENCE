import React, { useEffect, useState } from "react";
import {
  Brain,
  Play,
  HelpCircle,
  AlertCircle,
  CheckCircle2,
  GitBranch,
  ArrowRight,
  Plus,
  ShieldCheck,
  FileText,
} from "lucide-react";
import { caseApi } from "../case-api";
import type { ReasoningRule } from "../case-types";

interface Props {
  caseId: string;
}

export function ReasoningView({ caseId }: Props) {
  const [activeTab, setActiveTab] = useState<"forward" | "backward" | "rules">("forward");
  const [rules, setRules] = useState<ReasoningRule[]>([]);
  const [forwardResult, setForwardResult] = useState<any | null>(null);
  const [backwardResult, setBackwardResult] = useState<any | null>(null);
  const [forwardBusy, setForwardBusy] = useState(false);
  const [backwardBusy, setBackwardBusy] = useState(false);

  // Backward chaining inputs
  const [goalPredicate, setGoalPredicate] = useState("actionable_default");
  const [goalArgs, setGoalArgs] = useState("metro_rail, inr_2_50_000");

  useEffect(() => {
    caseApi.listRules(caseId).then(setRules).catch(() => {});
  }, [caseId]);

  const handleRunForward = async () => {
    try {
      setForwardBusy(true);
      const res = await caseApi.runForwardChaining(caseId);
      setForwardResult(res);
    } catch (err: any) {
      alert(err.message || "Forward chaining failed");
    } finally {
      setForwardBusy(false);
    }
  };

  const handleRunBackward = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalPredicate.trim()) return;
    try {
      setBackwardBusy(true);
      const argsList = goalArgs.split(",").map((a) => a.trim()).filter(Boolean);
      const res = await caseApi.runBackwardChaining(caseId, goalPredicate.trim(), argsList);
      setBackwardResult(res);
    } catch (err: any) {
      alert(err.message || "Backward chaining failed");
    } finally {
      setBackwardBusy(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Subtabs & Run controls */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div style={{ display: "flex", gap: "0.5rem", background: "#f1f5f9", padding: "4px", borderRadius: "8px" }}>
          <button
            onClick={() => setActiveTab("forward")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeTab === "forward" ? "#ffffff" : "transparent",
              color: activeTab === "forward" ? "#2563eb" : "#64748b",
              boxShadow: activeTab === "forward" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            }}
          >
            Forward Chaining Deduction
          </button>
          <button
            onClick={() => setActiveTab("backward")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeTab === "backward" ? "#ffffff" : "transparent",
              color: activeTab === "backward" ? "#2563eb" : "#64748b",
              boxShadow: activeTab === "backward" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            }}
          >
            Backward Chaining Hypothesis
          </button>
          <button
            onClick={() => setActiveTab("rules")}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeTab === "rules" ? "#ffffff" : "transparent",
              color: activeTab === "rules" ? "#2563eb" : "#64748b",
              boxShadow: activeTab === "rules" ? "0 1px 3px rgba(0,0,0,0.1)" : "none",
            }}
          >
            Active Rules ({rules.length})
          </button>
        </div>

        {activeTab === "forward" && (
          <button className="button primary" onClick={handleRunForward} disabled={forwardBusy}>
            <Play size={15} /> {forwardBusy ? "Deducing Facts…" : "Execute Forward Chaining"}
          </button>
        )}
      </div>

      {/* Tab 1: Forward Chaining */}
      {activeTab === "forward" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {!forwardResult ? (
            <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", border: "1px dashed #cbd5e1" }}>
              <Brain size={38} color="#2563eb" style={{ marginBottom: "0.75rem" }} />
              <h3 style={{ margin: "0 0 0.5rem 0", color: "#0f172a" }}>Execute Forward Inference</h3>
              <p style={{ color: "#64748b", maxWidth: "500px", margin: "0 auto 1.5rem auto", fontSize: "0.9rem" }}>
                Forward chaining evaluates all active case rules against extracted document facts, deriving new legal conclusions step-by-step.
              </p>
              <button className="button primary" onClick={handleRunForward} disabled={forwardBusy}>
                <Play size={16} /> Run Forward Chaining
              </button>
            </div>
          ) : (
            <div>
              {/* Summary Metrics */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
                <div style={{ padding: "1rem", background: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                  <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>TOTAL FACTS IN KB</div>
                  <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#0f172a" }}>{forwardResult.total_facts}</div>
                </div>
                <div style={{ padding: "1rem", background: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                  <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>NEW DERIVED FACTS</div>
                  <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#2563eb" }}>{forwardResult.new_facts_derived}</div>
                </div>
                <div style={{ padding: "1rem", background: "#ffffff", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
                  <div style={{ fontSize: "0.75rem", color: "#64748b", fontWeight: 700 }}>INFERENCE TRACES</div>
                  <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#059669" }}>{forwardResult.inference_traces?.length || 0}</div>
                </div>
              </div>

              {/* Deduction Traces */}
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700, color: "#0f172a", marginBottom: "0.75rem" }}>
                Step-by-Step Inference Traces
              </h3>
              <div style={{ display: "grid", gap: "0.75rem", marginBottom: "1.5rem" }}>
                {forwardResult.inference_traces?.map((tr: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      background: "#ffffff",
                      borderRadius: "8px",
                      border: "1px solid #e2e8f0",
                      padding: "1rem 1.25rem",
                      boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                      <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#2563eb" }}>
                        Rule: {tr.rule_name} ({tr.rule_id})
                      </span>
                      <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Iteration {tr.iteration}</span>
                    </div>

                    <div style={{ fontSize: "0.85rem", color: "#334155", marginBottom: "0.5rem" }}>
                      <b>Premises Matched:</b> {tr.premises_used?.join(" ∧ ")}
                    </div>

                    <div style={{ fontSize: "0.9rem", color: "#059669", fontWeight: 700, background: "#ecfdf5", padding: "6px 10px", borderRadius: "6px", display: "inline-block" }}>
                      Derived: {tr.derived_conclusion}
                    </div>

                    {tr.evidence?.length > 0 && (
                      <div style={{ marginTop: "0.5rem", fontSize: "0.75rem", color: "#64748b" }}>
                        <b>Supporting Evidence IDs:</b> {tr.evidence.join(", ")}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Contradictions Detected */}
              {forwardResult.contradictions_detected && forwardResult.contradictions_detected.length > 0 && (
                <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "8px", padding: "1rem", marginBottom: "1.5rem" }}>
                  <h4 style={{ color: "#991b1b", margin: "0 0 0.5rem 0", fontSize: "0.95rem", fontWeight: 700 }}>
                    Inconsistencies & Contradictions Identified
                  </h4>
                  {forwardResult.contradictions_detected.map((cd: any, idx: number) => (
                    <div key={idx} style={{ fontSize: "0.85rem", color: "#7f1d1d", marginBottom: "0.4rem" }}>
                      • <b>{cd.issue_type}:</b> {cd.explanation} (Facts: <i>{cd.fact_a}</i> vs <i>{cd.fact_b}</i>)
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Backward Chaining */}
      {activeTab === "backward" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 0.5rem 0", fontSize: "1.05rem", fontWeight: 700, color: "#0f172a" }}>
              Goal-Directed Hypothesis Proof
            </h3>
            <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0 0 1rem 0" }}>
              Enter a target legal proposition to determine whether it is entailed by current case facts and rules, or identify missing prerequisites.
            </p>
            <form onSubmit={handleRunBackward} style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: "200px" }}>
                <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "#475569", marginBottom: "0.2rem" }}>
                  Goal Predicate
                </label>
                <input
                  type="text"
                  placeholder="e.g. actionable_default or defect_claim_barred"
                  value={goalPredicate}
                  onChange={(e) => setGoalPredicate(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  required
                />
              </div>
              <div style={{ flex: 2, minWidth: "250px" }}>
                <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 600, color: "#475569", marginBottom: "0.2rem" }}>
                  Arguments (Comma-separated)
                </label>
                <input
                  type="text"
                  placeholder="e.g. metro_rail, inr_2_50_000"
                  value={goalArgs}
                  onChange={(e) => setGoalArgs(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div style={{ alignSelf: "flex-end" }}>
                <button className="button primary" type="submit" disabled={backwardBusy} style={{ height: "38px" }}>
                  {backwardBusy ? "Proving…" : "Prove Hypothesis"}
                </button>
              </div>
            </form>
          </div>

          {backwardResult && (
            <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <span style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
                  Target Hypothesis: {backwardResult.goal}
                </span>
                <span
                  style={{
                    fontSize: "0.85rem",
                    fontWeight: 700,
                    padding: "3px 10px",
                    borderRadius: "6px",
                    background: backwardResult.proven ? "#dcfce7" : "#fee2e2",
                    color: backwardResult.proven ? "#15803d" : "#b91c1c",
                  }}
                >
                  {backwardResult.proven ? "PROVEN FROM EVIDENCE" : "UNPROVEN / MISSING PREREQUISITES"}
                </span>
              </div>

              {/* Proof tree steps */}
              <h4 style={{ fontSize: "0.9rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.5rem" }}>
                Proof Derivation Steps
              </h4>
              <div style={{ display: "grid", gap: "0.4rem", marginBottom: "1rem" }}>
                {backwardResult.proof_tree?.map((step: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "0.5rem 0.8rem",
                      background: "#f8fafc",
                      borderRadius: "6px",
                      fontSize: "0.8rem",
                      marginLeft: `${step.depth * 18}px`,
                      borderLeft: "3px solid #2563eb",
                    }}
                  >
                    <b>Goal:</b> {step.goal} — <span style={{ color: "#2563eb", fontWeight: 600 }}>{step.status}</span>
                    {step.rule_name && <span> (Rule: {step.rule_name})</span>}
                  </div>
                ))}
              </div>

              {/* Missing prerequisites */}
              {backwardResult.missing_prerequisites && backwardResult.missing_prerequisites.length > 0 && (
                <div style={{ background: "#fffbeb", border: "1px solid #fde68a", padding: "0.85rem", borderRadius: "6px" }}>
                  <b style={{ color: "#b45309", fontSize: "0.85rem" }}>Missing Prerequisites to Establish Claim:</b>
                  <ul style={{ margin: "0.4rem 0 0 1.2rem", padding: 0, fontSize: "0.8rem", color: "#92400e" }}>
                    {backwardResult.missing_prerequisites.map((mp: any, idx: number) => (
                      <li key={idx}>
                        Predicate <b>{mp.predicate}({mp.args?.join(", ")})</b> — {mp.reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Rules List */}
      {activeTab === "rules" && (
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {rules.map((r) => (
            <div
              key={r.id}
              style={{
                background: "#ffffff",
                padding: "1rem 1.25rem",
                borderRadius: "8px",
                border: "1px solid #e2e8f0",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                <span style={{ fontWeight: 700, color: "#0f172a" }}>{r.name}</span>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>ID: {r.id}</span>
              </div>
              <p style={{ fontSize: "0.85rem", color: "#475569", margin: "0 0 0.6rem 0" }}>
                {r.description}
              </p>
              <div style={{ fontSize: "0.8rem", background: "#f8fafc", padding: "6px 10px", borderRadius: "6px", color: "#1e293b" }}>
                <b>IF:</b> {r.rule?.premises?.map((p: any) => `${p.predicate}(${p.args.join(", ")})`).join(" ∧ ")}
                <br />
                <b>THEN:</b> {r.rule?.conclusion?.predicate}({r.rule?.conclusion?.args.join(", ")})
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Professional Disclaimers */}
      <div style={{ fontSize: "0.75rem", color: "#64748b", background: "#f8fafc", padding: "0.75rem 1rem", borderRadius: "6px", border: "1px solid #e2e8f0" }}>
        <b>Notice on Legal Reasoning Engine:</b> Deductive outputs operate strictly on recorded case facts and configured rules. Absence of proof does not certify legal absence under judicial discretion. Output is for analytical assistance and requires professional counsel review.
      </div>
    </div>
  );
}
