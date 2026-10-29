import React, { useState } from "react";
import {
  Brain,
  Compass,
  Gamepad2,
  Cpu,
  BarChart2,
  Workflow,
  Play,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  Layers,
  Database,
  Sliders,
} from "lucide-react";
import { caseApi } from "../case-api";

export function AILabPage() {
  const [activeTab, setActiveTab] = useState<
    "search" | "games" | "logic" | "csp" | "ml" | "rl"
  >("search");

  // 1. Search Lab state
  const [searchAlgo, setSearchAlgo] = useState("bfs");
  const [startNode, setStartNode] = useState("A");
  const [targetNode, setTargetNode] = useState("G");
  const [searchResult, setSearchResult] = useState<any | null>(null);
  const [searchBusy, setSearchBusy] = useState(false);
  const [searchStepIndex, setSearchStepIndex] = useState<number>(0);

  // 2. Game Lab state
  const [gameAlgo, setGameAlgo] = useState("alpha_beta");
  const [gameDepth, setGameDepth] = useState(3);
  const [gameResult, setGameResult] = useState<any | null>(null);
  const [gameBusy, setGameBusy] = useState(false);

  // 3. Logic Lab state
  const [logicMode, setLogicMode] = useState("resolution");
  const [propVars, setPropVars] = useState("P, Q, R");
  const [propFormulas, setPropFormulas] = useState("P and Q\nP implies Q");
  const [resolutionClauses, setResolutionClauses] = useState("~Breach, Damages\nBreach\n~Damages, Interest_Awarded");
  const [resolutionQuery, setResolutionQuery] = useState("Interest_Awarded");
  const [folExpr1, setFolExpr1] = useState("Obligation(?contract, ?party, INR_1250000)");
  const [folExpr2, setFolExpr2] = useState("Obligation(EPC_Contract_3B, Metro_Rail, ?amount)");
  const [logicResult, setLogicResult] = useState<any | null>(null);
  const [logicBusy, setLogicBusy] = useState(false);

  // 4. CSP Lab state
  const [cspType, setCspType] = useState("hearing_schedule");
  const [cspResult, setCspResult] = useState<any | null>(null);
  const [cspBusy, setCspBusy] = useState(false);

  // 5. ML Lab state
  const [mlMode, setMlMode] = useState<"classification" | "clustering">("classification");
  const [kClusters, setKClusters] = useState(3);
  const [mlResult, setMlResult] = useState<any | null>(null);
  const [mlBusy, setMlBusy] = useState(false);

  // 6. RL Lab state
  const [rlEpisodes, setRlEpisodes] = useState(120);
  const [rlAlpha, setRlAlpha] = useState(0.2);
  const [rlGamma, setRlGamma] = useState(0.9);
  const [rlEpsilon, setRlEpsilon] = useState(0.3);
  const [rlResult, setRlResult] = useState<any | null>(null);
  const [rlBusy, setRlBusy] = useState(false);

  // Handlers
  const handleRunSearch = async () => {
    try {
      setSearchBusy(true);
      const res = await caseApi.runLabSearch({
        algorithm: searchAlgo,
        start_node: startNode,
        target_node: targetNode,
      });
      setSearchResult(res);
      setSearchStepIndex(res.steps ? res.steps.length - 1 : 0);
    } catch (err: any) {
      alert(err.message || "Search failed");
    } finally {
      setSearchBusy(false);
    }
  };

  const handleRunGame = async () => {
    try {
      setGameBusy(true);
      const res = await caseApi.runLabGame({
        algorithm: gameAlgo,
        depth: gameDepth,
        iterations: 35,
      });
      setGameResult(res);
    } catch (err: any) {
      alert(err.message || "Game search failed");
    } finally {
      setGameBusy(false);
    }
  };

  const handleRunLogic = async () => {
    try {
      setLogicBusy(true);
      let payload: any = { mode: logicMode };
      if (logicMode === "truth_table") {
        payload.variables = propVars.split(",").map((v) => v.trim()).filter(Boolean);
        payload.formulas = propFormulas.split("\n").map((f) => f.trim()).filter(Boolean);
      } else if (logicMode === "resolution") {
        payload.clauses = resolutionClauses
          .split("\n")
          .map((c) => c.split(",").map((lit) => lit.trim()).filter(Boolean))
          .filter((c) => c.length > 0);
        payload.query = resolutionQuery.trim();
      } else {
        payload.expr1 = folExpr1.trim();
        payload.expr2 = folExpr2.trim();
      }
      const res = await caseApi.runLabLogic(payload);
      setLogicResult(res);
    } catch (err: any) {
      alert(err.message || "Logic theorem prover failed");
    } finally {
      setLogicBusy(false);
    }
  };

  const handleRunCSP = async () => {
    try {
      setCspBusy(true);
      const res = await caseApi.runLabCSP({ problem_type: cspType });
      setCspResult(res);
    } catch (err: any) {
      alert(err.message || "CSP backtracking failed");
    } finally {
      setCspBusy(false);
    }
  };

  const handleRunML = async () => {
    try {
      setMlBusy(true);
      const res = await caseApi.runLabML(mlMode, kClusters);
      setMlResult(res);
    } catch (err: any) {
      alert(err.message || "Machine learning execution failed");
    } finally {
      setMlBusy(false);
    }
  };

  const handleRunRL = async () => {
    try {
      setRlBusy(true);
      const res = await caseApi.runLabRL({
        episodes: rlEpisodes,
        alpha: rlAlpha,
        gamma: rlGamma,
        epsilon: rlEpsilon,
      });
      setRlResult(res);
    } catch (err: any) {
      alert(err.message || "Reinforcement learning failed");
    } finally {
      setRlBusy(false);
    }
  };

  return (
    <div style={{ padding: "1.5rem 2rem", maxWidth: "1400px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#2563eb", fontWeight: 700, fontSize: "0.85rem", letterSpacing: "1px" }}>
          <Brain size={18} /> INTERACTIVE COMPUTATIONAL LABORATORY
        </div>
        <h1 style={{ fontSize: "2rem", fontWeight: 800, margin: "0.2rem 0 0.4rem 0", color: "#0f172a" }}>
          AI Algorithm Lab
        </h1>
        <p style={{ color: "#475569", margin: 0, fontSize: "0.95rem" }}>
          Live, transparent executions of classic Search, Game Trees, Theorem Provers, Constraint Satisfaction, Machine Learning, and Reinforcement Learning.
        </p>
      </div>

      {/* Main Domain Selector Tabs */}
      <div
        style={{
          display: "flex",
          gap: "0.5rem",
          background: "#ffffff",
          padding: "6px",
          borderRadius: "10px",
          border: "1px solid #e2e8f0",
          marginBottom: "1.5rem",
          flexWrap: "wrap",
        }}
      >
        {[
          { id: "search", label: "Search & Pathfinding", icon: Compass },
          { id: "games", label: "Game Search & Minimax", icon: Gamepad2 },
          { id: "logic", label: "Logic & Resolution", icon: Cpu },
          { id: "csp", label: "Constraint Satisfaction (CSP)", icon: Workflow },
          { id: "ml", label: "Machine Learning (Supervised/K-Means)", icon: BarChart2 },
          { id: "rl", label: "Reinforcement Learning (Q-Learning)", icon: TrendingUp },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as any)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              padding: "0.6rem 1.1rem",
              borderRadius: "6px",
              border: "none",
              fontSize: "0.85rem",
              fontWeight: 600,
              cursor: "pointer",
              background: activeTab === t.id ? "#2563eb" : "transparent",
              color: activeTab === t.id ? "#ffffff" : "#475569",
              transition: "all 0.15s ease",
            }}
          >
            <t.icon size={16} />
            {t.label}
          </button>
        ))}
      </div>

      {/* ======================================================================== */}
      {/* 1. SEARCH & OPTIMISATION */}
      {/* ======================================================================== */}
      {activeTab === "search" && (
        <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: "1.5rem" }}>
          <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Search Configuration</h3>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                Algorithm:
              </label>
              <select
                value={searchAlgo}
                onChange={(e) => setSearchAlgo(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
              >
                <option value="bfs">Breadth-First Search (BFS)</option>
                <option value="dfs">Depth-First Search (DFS)</option>
                <option value="ucs">Uniform-Cost Search (Dijkstra)</option>
                <option value="greedy">Greedy Best-First Search</option>
                <option value="astar">A* Search (g(n) + h(n))</option>
                <option value="hill_climbing">Hill Climbing Local Search</option>
              </select>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.8rem", marginBottom: "1.2rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                  Start Node:
                </label>
                <input
                  type="text"
                  value={startNode}
                  onChange={(e) => setStartNode(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                  Target Node:
                </label>
                <input
                  type="text"
                  value={targetNode}
                  onChange={(e) => setTargetNode(e.target.value)}
                  style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                />
              </div>
            </div>

            <button
              className="button primary"
              onClick={handleRunSearch}
              disabled={searchBusy}
              style={{ width: "100%", padding: "0.6rem" }}
            >
              <Play size={16} /> {searchBusy ? "Executing Search…" : "Run Search Algorithm"}
            </button>

            <div style={{ marginTop: "1.2rem", fontSize: "0.75rem", color: "#64748b", lineHeight: "1.4" }}>
              <b>Guarantees:</b> BFS guarantees shortest step path; UCS and A* guarantee lowest cost path with cycle prevention.
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {/* Visual Graph Diagram */}
            <div
              style={{
                background: "#ffffff",
                borderRadius: "10px",
                border: "1px solid #e2e8f0",
                padding: "1rem",
                minHeight: "260px",
              }}
            >
              <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.5rem" }}>
                Problem Graph Visualization
              </div>
              <svg width="100%" height="220" viewBox="0 0 700 200">
                {/* Edges */}
                {[
                  { x1: 100, y1: 100, x2: 220, y2: 70, lbl: "w=1.0" },
                  { x1: 100, y1: 100, x2: 220, y2: 150, lbl: "w=2.0" },
                  { x1: 220, y1: 70, x2: 360, y2: 50, lbl: "w=2.5" },
                  { x1: 220, y1: 70, x2: 220, y2: 150, lbl: "w=1.5" },
                  { x1: 220, y1: 150, x2: 360, y2: 150, lbl: "w=1.0" },
                  { x1: 360, y1: 50, x2: 480, y2: 80, lbl: "w=3.0" },
                  { x1: 360, y1: 150, x2: 480, y2: 80, lbl: "w=2.0" },
                  { x1: 360, y1: 150, x2: 600, y2: 100, lbl: "w=4.5" },
                  { x1: 480, y1: 80, x2: 600, y2: 100, lbl: "w=1.5" },
                ].map((e, idx) => (
                  <g key={idx}>
                    <line x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2} stroke="#cbd5e1" strokeWidth="2" />
                    <text x={(e.x1 + e.x2) / 2} y={(e.y1 + e.y2) / 2 - 4} fontSize="9" fill="#64748b" textAnchor="middle">
                      {e.lbl}
                    </text>
                  </g>
                ))}

                {/* Nodes */}
                {[
                  ["A", 100, 100],
                  ["B", 220, 70],
                  ["C", 220, 150],
                  ["D", 360, 50],
                  ["E", 360, 150],
                  ["F", 480, 80],
                  ["G", 600, 100],
                ].map(([id, x, y]) => {
                  const inPath = searchResult?.path && searchResult.path.includes(id);
                  return (
                    <g key={id as string} transform={`translate(${x}, ${y})`}>
                      <circle r="16" fill={inPath ? "#2563eb" : "#ffffff"} stroke="#2563eb" strokeWidth="2.5" />
                      <text textAnchor="middle" y="4" fill={inPath ? "#ffffff" : "#0f172a"} fontWeight="700" fontSize="11">
                        {id}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* Results Output */}
            {searchResult && (
              <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.8rem" }}>
                  <span style={{ fontSize: "1rem", fontWeight: 700, color: "#0f172a" }}>
                    Algorithm: {searchResult.algorithm}
                  </span>
                  <span style={{ fontSize: "0.85rem", fontWeight: 700, color: searchResult.found ? "#059669" : "#dc2626" }}>
                    {searchResult.found ? `Goal Found (Length: ${searchResult.path_length})` : "Unreachable"}
                  </span>
                </div>

                {searchResult.path && (
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1rem" }}>
                    <b>Optimal Discovered Path:</b>
                    {searchResult.path.map((node: string, idx: number) => (
                      <React.Fragment key={idx}>
                        <span style={{ padding: "3px 8px", background: "#dbeafe", color: "#1e40af", fontWeight: 700, borderRadius: "4px" }}>
                          {node}
                        </span>
                        {idx < searchResult.path.length - 1 && <ArrowRight size={14} color="#64748b" />}
                      </React.Fragment>
                    ))}
                    {searchResult.path_cost !== undefined && (
                      <span style={{ marginLeft: "10px", color: "#059669", fontWeight: 600 }}>
                        (Total Cost: {searchResult.path_cost})
                      </span>
                    )}
                  </div>
                )}

                {/* Step Trace */}
                {searchResult.steps && (
                  <div>
                    <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.4rem" }}>
                      Search Traversal Steps ({searchResult.steps.length} steps):
                    </div>
                    <div style={{ maxHeight: "180px", overflowY: "auto", border: "1px solid #f1f5f9", borderRadius: "6px" }}>
                      {searchResult.steps.map((st: any) => (
                        <div key={st.step} style={{ padding: "6px 10px", borderBottom: "1px solid #f1f5f9", fontSize: "0.8rem" }}>
                          <b>Step {st.step}:</b> {st.action} | <i>Frontier: [{st.frontier?.map((x: any) => (Array.isArray(x) ? x.join(":") : x)).join(", ")}]</i>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* 2. GAME SEARCH: MINIMAX, ALPHA-BETA, MCTS */}
      {/* ======================================================================== */}
      {activeTab === "games" && (
        <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: "1.5rem" }}>
          <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Game Tree Configuration</h3>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                Game Algorithm:
              </label>
              <select
                value={gameAlgo}
                onChange={(e) => setGameAlgo(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
              >
                <option value="alpha_beta">Alpha-Beta Pruning (Branch Cutoff)</option>
                <option value="minimax">Classic Minimax Tree Search</option>
                <option value="mcts">Monte Carlo Tree Search (UCB1)</option>
                <option value="expectiminimax">Expectiminimax (Chance / Uncertainty)</option>
              </select>
            </div>

            <div style={{ marginBottom: "1.2rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                Depth / Iterations: {gameDepth}
              </label>
              <input
                type="range"
                min={1}
                max={4}
                value={gameDepth}
                onChange={(e) => setGameDepth(Number(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>

            <button
              className="button primary"
              onClick={handleRunGame}
              disabled={gameBusy}
              style={{ width: "100%", padding: "0.6rem" }}
            >
              <Play size={16} /> {gameBusy ? "Evaluating Tree…" : "Evaluate Game Decision"}
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {gameResult ? (
              <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.8rem" }}>
                  <span style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a" }}>
                    Algorithm: {gameResult.algorithm}
                  </span>
                  {gameResult.pruned_branches_count !== undefined && (
                    <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#b91c1c", background: "#fee2e2", padding: "3px 8px", borderRadius: "4px" }}>
                      Pruned Branches: {gameResult.pruned_branches_count}
                    </span>
                  )}
                </div>

                {gameResult.optimal_value !== undefined && (
                  <div style={{ fontSize: "1rem", color: "#059669", fontWeight: 700, marginBottom: "1rem" }}>
                    Optimal Value for MAX: {gameResult.optimal_value}
                  </div>
                )}

                {gameResult.recommended_action && (
                  <div style={{ fontSize: "1rem", color: "#2563eb", fontWeight: 700, marginBottom: "1rem" }}>
                    Recommended Action: {gameResult.recommended_action} (Win Rate: {gameResult.recommended_win_rate * 100}%)
                  </div>
                )}

                {/* Steps Trace */}
                <div>
                  <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.4rem" }}>
                    Evaluation Sequence:
                  </div>
                  <div style={{ maxHeight: "250px", overflowY: "auto", border: "1px solid #f1f5f9", borderRadius: "6px" }}>
                    {gameResult.steps?.map((st: any, idx: number) => (
                      <div key={idx} style={{ padding: "6px 10px", borderBottom: "1px solid #f1f5f9", fontSize: "0.8rem" }}>
                        <b>{st.node || st.selected_action}:</b> {st.action || st.simulation_result}
                        {st.alpha !== undefined && <span> [α={st.alpha}, β={st.beta}]</span>}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", border: "1px dashed #cbd5e1", color: "#64748b" }}>
                Select a game algorithm and click Evaluate Game Decision.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* 3. LOGIC & THEOREM PROVING */}
      {/* ======================================================================== */}
      {activeTab === "logic" && (
        <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: "1.5rem" }}>
          <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Logic Engine Mode</h3>

            <div style={{ marginBottom: "1rem" }}>
              <select
                value={logicMode}
                onChange={(e) => setLogicMode(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
              >
                <option value="resolution">Propositional Resolution Refutation</option>
                <option value="truth_table">Propositional Truth Table</option>
                <option value="unification">First-Order Logic Unification (MGU)</option>
              </select>
            </div>

            {logicMode === "resolution" && (
              <>
                <div style={{ marginBottom: "0.8rem" }}>
                  <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                    Knowledge Base Clauses (One per line, comma literals):
                  </label>
                  <textarea
                    rows={4}
                    value={resolutionClauses}
                    onChange={(e) => setResolutionClauses(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1", fontFamily: "monospace", fontSize: "0.8rem" }}
                  />
                </div>
                <div style={{ marginBottom: "1rem" }}>
                  <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                    Query Literal to Prove:
                  </label>
                  <input
                    type="text"
                    value={resolutionQuery}
                    onChange={(e) => setResolutionQuery(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  />
                </div>
              </>
            )}

            {logicMode === "unification" && (
              <>
                <div style={{ marginBottom: "0.8rem" }}>
                  <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                    Expression 1 (Variables start with ?):
                  </label>
                  <input
                    type="text"
                    value={folExpr1}
                    onChange={(e) => setFolExpr1(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  />
                </div>
                <div style={{ marginBottom: "1rem" }}>
                  <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                    Expression 2:
                  </label>
                  <input
                    type="text"
                    value={folExpr2}
                    onChange={(e) => setFolExpr2(e.target.value)}
                    style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
                  />
                </div>
              </>
            )}

            <button
              className="button primary"
              onClick={handleRunLogic}
              disabled={logicBusy}
              style={{ width: "100%", padding: "0.6rem" }}
            >
              <Cpu size={16} /> {logicBusy ? "Proving…" : "Execute Theorem Prover"}
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {logicResult ? (
              <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.8rem" }}>
                  <span style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a" }}>
                    {logicResult.algorithm}
                  </span>
                  {logicResult.proved !== undefined && (
                    <span
                      style={{
                        fontSize: "0.85rem",
                        fontWeight: 700,
                        padding: "3px 8px",
                        borderRadius: "4px",
                        background: logicResult.proved ? "#dcfce7" : "#fee2e2",
                        color: logicResult.proved ? "#15803d" : "#b91c1c",
                      }}
                    >
                      {logicResult.proved ? "Strictly Entailed (Q.E.D.)" : "Refutation Failed / Not Entailed"}
                    </span>
                  )}
                </div>

                <p style={{ fontSize: "0.85rem", color: "#475569", marginBottom: "1rem" }}>
                  {logicResult.explanation}
                </p>

                {/* Resolution Steps Table */}
                {logicResult.steps && (
                  <div>
                    <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.4rem" }}>
                      Derivation Trace:
                    </div>
                    <div style={{ maxHeight: "250px", overflowY: "auto", border: "1px solid #f1f5f9", borderRadius: "6px" }}>
                      {logicResult.steps.map((st: any) => (
                        <div
                          key={st.step}
                          style={{
                            padding: "6px 10px",
                            borderBottom: "1px solid #f1f5f9",
                            fontSize: "0.8rem",
                            background: st.contradiction ? "#fef2f2" : "#ffffff",
                            color: st.contradiction ? "#dc2626" : "#0f172a",
                          }}
                        >
                          <b>{st.id}:</b> {st.clause} — <i>{st.origin}</i>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Unification MGU */}
                {logicResult.substitution && (
                  <div style={{ background: "#f8fafc", padding: "0.8rem", borderRadius: "6px", fontSize: "0.85rem" }}>
                    <b>Most General Unifier (MGU):</b>
                    <pre style={{ margin: "0.3rem 0 0 0" }}>{JSON.stringify(logicResult.substitution, null, 2)}</pre>
                  </div>
                )}

                {/* Truth Table */}
                {logicResult.rows && (
                  <div style={{ maxHeight: "250px", overflowY: "auto" }}>
                    <table style={{ width: "100%", fontSize: "0.8rem", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "#f1f5f9" }}>
                          {logicResult.variables?.map((v: string) => (
                            <th key={v} style={{ padding: "6px", border: "1px solid #cbd5e1" }}>{v}</th>
                          ))}
                          {logicResult.formulas?.map((f: string) => (
                            <th key={f} style={{ padding: "6px", border: "1px solid #cbd5e1" }}>{f}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {logicResult.rows.map((r: any, rIdx: number) => (
                          <tr key={rIdx}>
                            {logicResult.variables?.map((v: string) => (
                              <td key={v} style={{ padding: "4px", textAlign: "center", border: "1px solid #e2e8f0" }}>
                                {r.assignment[v] ? "T" : "F"}
                              </td>
                            ))}
                            {logicResult.formulas?.map((f: string) => (
                              <td key={f} style={{ padding: "4px", textAlign: "center", border: "1px solid #e2e8f0", fontWeight: 700, color: r.evaluations[f] ? "#059669" : "#dc2626" }}>
                                {r.evaluations[f] ? "True" : "False"}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", border: "1px dashed #cbd5e1", color: "#64748b" }}>
                Select a logic mode and click Execute Theorem Prover.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* 4. CONSTRAINT SATISFACTION (CSP) */}
      {/* ======================================================================== */}
      {activeTab === "csp" && (
        <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: "1.5rem" }}>
          <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>CSP Problem Selection</h3>

            <div style={{ marginBottom: "1.2rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                Legal Problem Context:
              </label>
              <select
                value={cspType}
                onChange={(e) => setCspType(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
              >
                <option value="hearing_schedule">Courtroom Hearing & Trial Scheduling</option>
                <option value="event_timeline">Statutory Notice & Cure Period Temporal Constraints</option>
              </select>
            </div>

            <button
              className="button primary"
              onClick={handleRunCSP}
              disabled={cspBusy}
              style={{ width: "100%", padding: "0.6rem" }}
            >
              <Workflow size={16} /> {cspBusy ? "Propagating Constraints…" : "Solve CSP with MRV"}
            </button>

            <div style={{ marginTop: "1rem", fontSize: "0.75rem", color: "#64748b" }}>
              <b>Heuristics:</b> Backtracking search combines Minimum Remaining Values (MRV) variable ordering with Forward Checking / AC-3 domain propagation.
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {cspResult ? (
              <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.8rem" }}>
                  <span style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a" }}>
                    {cspResult.algorithm}
                  </span>
                  <span
                    style={{
                      fontSize: "0.85rem",
                      fontWeight: 700,
                      padding: "3px 8px",
                      borderRadius: "4px",
                      background: cspResult.solved ? "#dcfce7" : "#fee2e2",
                      color: cspResult.solved ? "#15803d" : "#b91c1c",
                    }}
                  >
                    {cspResult.solved ? "Consistent Solution Found" : "Unsatisfiable"}
                  </span>
                </div>

                {cspResult.solution && (
                  <div style={{ background: "#ecfdf5", border: "1px solid #a7f3d0", padding: "0.85rem", borderRadius: "6px", marginBottom: "1rem" }}>
                    <b style={{ color: "#065f46" }}>Satisfying Variable Assignment:</b>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.5rem", marginTop: "0.4rem" }}>
                      {Object.entries(cspResult.solution).map(([k, v]) => (
                        <div key={k} style={{ fontSize: "0.85rem", color: "#0f172a" }}>
                          <b>{k}:</b> Slot/Day {v as any}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Backtracking steps */}
                <div>
                  <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.4rem" }}>
                    Search and Backtracking Trace ({cspResult.steps?.length} steps):
                  </div>
                  <div style={{ maxHeight: "250px", overflowY: "auto", border: "1px solid #f1f5f9", borderRadius: "6px" }}>
                    {cspResult.steps?.map((st: any) => (
                      <div key={st.step} style={{ padding: "6px 10px", borderBottom: "1px solid #f1f5f9", fontSize: "0.8rem" }}>
                        <b>Step {st.step}:</b> {st.action}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", border: "1px dashed #cbd5e1", color: "#64748b" }}>
                Select a CSP problem and click Solve CSP.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* 5. MACHINE LEARNING: SUPERVISED & CLUSTERING */}
      {/* ======================================================================== */}
      {activeTab === "ml" && (
        <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: "1.5rem" }}>
          <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>ML Model Configuration</h3>

            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                Model Type:
              </label>
              <select
                value={mlMode}
                onChange={(e) => setMlMode(e.target.value as any)}
                style={{ width: "100%", padding: "0.5rem", borderRadius: "6px", border: "1px solid #cbd5e1" }}
              >
                <option value="classification">Supervised Naive Bayes Document Classifier</option>
                <option value="clustering">K-Means Dispute Profile Clustering</option>
              </select>
            </div>

            {mlMode === "clustering" && (
              <div style={{ marginBottom: "1.2rem" }}>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.3rem" }}>
                  Number of Clusters (K): {kClusters}
                </label>
                <input
                  type="range"
                  min={2}
                  max={4}
                  value={kClusters}
                  onChange={(e) => setKClusters(Number(e.target.value))}
                  style={{ width: "100%" }}
                />
              </div>
            )}

            <button
              className="button primary"
              onClick={handleRunML}
              disabled={mlBusy}
              style={{ width: "100%", padding: "0.6rem" }}
            >
              <BarChart2 size={16} /> {mlBusy ? "Training Model…" : "Train & Evaluate Model"}
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {mlResult ? (
              <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.25rem" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a", marginBottom: "0.8rem" }}>
                  {mlResult.algorithm}
                </h3>

                {mlMode === "classification" ? (
                  <div>
                    {/* Metrics Row */}
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginBottom: "1rem" }}>
                      <div style={{ padding: "0.75rem", background: "#f8fafc", borderRadius: "6px", textAlign: "center" }}>
                        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>TEST ACCURACY</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#059669" }}>
                          {(mlResult.accuracy * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div style={{ padding: "0.75rem", background: "#f8fafc", borderRadius: "6px", textAlign: "center" }}>
                        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>MACRO F1-SCORE</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#2563eb" }}>
                          {(mlResult.macro_f1 * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div style={{ padding: "0.75rem", background: "#f8fafc", borderRadius: "6px", textAlign: "center" }}>
                        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>VOCABULARY SIZE</div>
                        <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "#0f172a" }}>
                          {mlResult.vocabulary_size} terms
                        </div>
                      </div>
                    </div>

                    {/* Confusion Matrix Table */}
                    <div style={{ marginBottom: "1rem" }}>
                      <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.4rem" }}>
                        Evaluation Confusion Matrix:
                      </div>
                      <table style={{ width: "100%", fontSize: "0.8rem", borderCollapse: "collapse" }}>
                        <thead>
                          <tr style={{ background: "#f1f5f9" }}>
                            <th style={{ padding: "6px", border: "1px solid #cbd5e1" }}>Actual \ Predicted</th>
                            {mlResult.classes?.map((c: string) => (
                              <th key={c} style={{ padding: "6px", border: "1px solid #cbd5e1" }}>{c}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {mlResult.classes?.map((c1: string) => (
                            <tr key={c1}>
                              <td style={{ padding: "6px", border: "1px solid #cbd5e1", fontWeight: 700 }}>{c1}</td>
                              {mlResult.classes?.map((c2: string) => (
                                <td key={c2} style={{ padding: "6px", textAlign: "center", border: "1px solid #cbd5e1", fontWeight: c1 === c2 ? 700 : 400, background: c1 === c2 ? "#ecfdf5" : "#ffffff" }}>
                                  {mlResult.confusion_matrix[c1][c2]}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div>
                    {/* Clustering results */}
                    <div style={{ marginBottom: "1rem", fontSize: "0.9rem", color: "#334155" }}>
                      <b>Converged in:</b> {mlResult.iterations_to_converge} iterations • <b>Inertia:</b> {mlResult.inertia}
                    </div>
                    <div style={{ display: "grid", gap: "0.5rem" }}>
                      {mlResult.labeled_points?.map((pt: any, idx: number) => (
                        <div key={idx} style={{ padding: "6px 10px", background: "#f8fafc", borderRadius: "6px", display: "flex", justifyContent: "space-between", fontSize: "0.8rem" }}>
                          <span><b>{pt.name}</b> (Claim: ₹{pt.claim_value_lakhs}L, Duration: {pt.duration_months}m)</span>
                          <span style={{ fontWeight: 700, color: "#2563eb" }}>{pt.cluster_label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", border: "1px dashed #cbd5e1", color: "#64748b" }}>
                Click Train & Evaluate Model to run transparent local ML algorithms.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================================== */}
      {/* 6. REINFORCEMENT LEARNING: TABULAR Q-LEARNING */}
      {/* ======================================================================== */}
      {activeTab === "rl" && (
        <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: "1.5rem" }}>
          <div style={{ background: "#ffffff", padding: "1.25rem", borderRadius: "10px", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 1rem 0", fontSize: "1.1rem", fontWeight: 700 }}>Q-Learning Parameters</h3>

            <div style={{ marginBottom: "0.8rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                Training Episodes: {rlEpisodes}
              </label>
              <input
                type="range"
                min={30}
                max={300}
                value={rlEpisodes}
                onChange={(e) => setRlEpisodes(Number(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>

            <div style={{ marginBottom: "0.8rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                Learning Rate (α): {rlAlpha}
              </label>
              <input
                type="range"
                min={0.05}
                max={0.8}
                step={0.05}
                value={rlAlpha}
                onChange={(e) => setRlAlpha(Number(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>

            <div style={{ marginBottom: "0.8rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                Discount Factor (γ): {rlGamma}
              </label>
              <input
                type="range"
                min={0.5}
                max={0.99}
                step={0.05}
                value={rlGamma}
                onChange={(e) => setRlGamma(Number(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>

            <div style={{ marginBottom: "1.2rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, marginBottom: "0.2rem" }}>
                Exploration (ε): {rlEpsilon}
              </label>
              <input
                type="range"
                min={0.05}
                max={0.6}
                step={0.05}
                value={rlEpsilon}
                onChange={(e) => setRlEpsilon(Number(e.target.value))}
                style={{ width: "100%" }}
              />
            </div>

            <button
              className="button primary"
              onClick={handleRunRL}
              disabled={rlBusy}
              style={{ width: "100%", padding: "0.6rem" }}
            >
              <TrendingUp size={16} /> {rlBusy ? "Training Agent…" : "Train Q-Learning Agent"}
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {rlResult ? (
              <div style={{ background: "#ffffff", borderRadius: "10px", border: "1px solid #e2e8f0", padding: "1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.8rem" }}>
                  <span style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f172a" }}>
                    {rlResult.algorithm}
                  </span>
                  <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#059669" }}>
                    Avg Terminal Reward: {rlResult.average_final_reward}
                  </span>
                </div>

                {/* Optimal Learned Policy */}
                <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", padding: "0.85rem", borderRadius: "6px", marginBottom: "1rem" }}>
                  <b style={{ color: "#1e40af", fontSize: "0.9rem" }}>Extracted Optimal Litigation Strategy:</b>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.6rem", marginTop: "0.4rem" }}>
                    {Object.entries(rlResult.optimal_policy || {}).map(([state, opt]: [string, any]) => (
                      <div key={state} style={{ fontSize: "0.8rem", color: "#1e293b" }}>
                        <b>State: {state}</b> → <span style={{ color: "#2563eb", fontWeight: 700 }}>{opt.recommended_action}</span> (Q={opt.q_value})
                      </div>
                    ))}
                  </div>
                </div>

                {/* Q-Value Matrix Table */}
                <div style={{ marginBottom: "1rem" }}>
                  <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.4rem" }}>
                    Learned Q-Table Matrix Q(s, a):
                  </div>
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", fontSize: "0.8rem", borderCollapse: "collapse" }}>
                      <thead>
                        <tr style={{ background: "#f1f5f9" }}>
                          <th style={{ padding: "6px", border: "1px solid #cbd5e1" }}>State</th>
                          {rlResult.actions?.map((a: string) => (
                            <th key={a} style={{ padding: "6px", border: "1px solid #cbd5e1" }}>{a}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {rlResult.states?.map((s: string) => (
                          <tr key={s}>
                            <td style={{ padding: "6px", border: "1px solid #cbd5e1", fontWeight: 700 }}>{s}</td>
                            {rlResult.actions?.map((a: string) => (
                              <td key={a} style={{ padding: "6px", textAlign: "center", border: "1px solid #cbd5e1" }}>
                                {rlResult.q_table[s][a]}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ padding: "3rem", textAlign: "center", background: "#f8fafc", borderRadius: "10px", border: "1px dashed #cbd5e1", color: "#64748b" }}>
                Click Train Q-Learning Agent to simulate litigation policy optimization.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
