import { api } from "./api";
import type {
  CaseItem,
  CaseDocument,
  CaseFact,
  EvidenceItem,
  EvidenceRelationship,
  TimelineEvent,
  InconsistencyItem,
  ReasoningRule,
  ArgumentItem,
  LegalAuthority,
} from "./case-types";

export const caseApi = {
  // Case Management
  listCases: (status?: string, search?: string) => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (search) params.set("search", search);
    const q = params.toString();
    return api<CaseItem[]>(`/cases${q ? `?${q}` : ""}`);
  },
  getCase: (cid: string) => api<CaseItem>(`/cases/${cid}`),
  createCase: (data: Partial<CaseItem>) =>
    api<CaseItem>("/cases", { method: "POST", body: JSON.stringify(data) }),
  updateCase: (cid: string, data: Partial<CaseItem>) =>
    api<CaseItem>(`/cases/${cid}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteCase: (cid: string) =>
    api<{ deleted: boolean }>(`/cases/${cid}`, { method: "DELETE" }),
  loadDemoCase: () => api<CaseItem>("/cases/demo", { method: "POST" }),

  // Documents
  listDocuments: (cid: string) => api<CaseDocument[]>(`/cases/${cid}/documents`),
  getDocument: (cid: string, did: string) =>
    api<CaseDocument>(`/cases/${cid}/documents/${did}`),
  uploadDocument: (cid: string, form: FormData) =>
    api<CaseDocument>(`/cases/${cid}/documents`, { method: "POST", body: form }),
  deleteDocument: (cid: string, did: string) =>
    api<{ deleted: boolean }>(`/cases/${cid}/documents/${did}`, { method: "DELETE" }),

  // Facts
  listFacts: (cid: string, category?: string, status?: string) => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (status) params.set("status", status);
    const q = params.toString();
    return api<CaseFact[]>(`/cases/${cid}/facts${q ? `?${q}` : ""}`);
  },
  createFact: (cid: string, fact: Partial<CaseFact>) =>
    api<CaseFact>(`/cases/${cid}/facts`, { method: "POST", body: JSON.stringify(fact) }),
  updateFactStatus: (cid: string, fid: string, status: string) =>
    api<{ updated: boolean }>(`/cases/${cid}/facts/${fid}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  // Evidence & Relationships
  listEvidence: (cid: string) => api<EvidenceItem[]>(`/cases/${cid}/evidence`),
  createEvidence: (cid: string, item: Partial<EvidenceItem>) =>
    api<EvidenceItem>(`/cases/${cid}/evidence`, { method: "POST", body: JSON.stringify(item) }),
  listRelationships: (cid: string) =>
    api<EvidenceRelationship[]>(`/cases/${cid}/evidence/relationships`),
  createRelationship: (cid: string, rel: Partial<EvidenceRelationship>) =>
    api<EvidenceRelationship>(`/cases/${cid}/evidence/relationships`, {
      method: "POST",
      body: JSON.stringify(rel),
    }),
  getEvidenceGraph: (cid: string) =>
    api<{ nodes: any[]; edges: any[] }>(`/cases/${cid}/evidence/graph`),
  runPathfinding: (cid: string, body: { algorithm: string; source_id: string; target_id: string }) =>
    api<any>(`/cases/${cid}/evidence/pathfinding`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Intelligent Search
  searchCase: (cid: string, query: string, method = "bm25", documentFilter?: string) =>
    api<any[]>(`/cases/${cid}/search`, {
      method: "POST",
      body: JSON.stringify({ query, method, document_filter: documentFilter }),
    }),

  // Timeline & Inconsistencies
  listTimeline: (cid: string) => api<TimelineEvent[]>(`/cases/${cid}/timeline`),
  addTimelineEvent: (cid: string, event: Partial<TimelineEvent>) =>
    api<TimelineEvent>(`/cases/${cid}/timeline`, { method: "POST", body: JSON.stringify(event) }),
  listInconsistencies: (cid: string) =>
    api<InconsistencyItem[]>(`/cases/${cid}/inconsistencies`),
  addInconsistency: (cid: string, item: Partial<InconsistencyItem>) =>
    api<InconsistencyItem>(`/cases/${cid}/inconsistencies`, {
      method: "POST",
      body: JSON.stringify(item),
    }),
  updateInconsistencyStatus: (cid: string, iid: string, status: string) =>
    api<{ updated: boolean }>(`/cases/${cid}/inconsistencies/${iid}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  // Reasoning
  listRules: (cid: string) => api<ReasoningRule[]>(`/cases/${cid}/reasoning/rules`),
  createRule: (cid: string, rule: any) =>
    api<any>(`/cases/${cid}/reasoning/rules`, { method: "POST", body: JSON.stringify(rule) }),
  runForwardChaining: (cid: string) =>
    api<any>(`/cases/${cid}/reasoning/forward`, { method: "POST" }),
  runBackwardChaining: (cid: string, goal_predicate: string, goal_args: string[]) =>
    api<any>(`/cases/${cid}/reasoning/backward`, {
      method: "POST",
      body: JSON.stringify({ goal_predicate, goal_args }),
    }),

  // Arguments & Authorities
  listArguments: (cid: string) => api<ArgumentItem[]>(`/cases/${cid}/arguments`),
  addArgument: (cid: string, arg: Partial<ArgumentItem>) =>
    api<ArgumentItem>(`/cases/${cid}/arguments`, { method: "POST", body: JSON.stringify(arg) }),
  listAuthorities: (cid: string) => api<LegalAuthority[]>(`/cases/${cid}/authorities`),
  addAuthority: (cid: string, auth: Partial<LegalAuthority>) =>
    api<LegalAuthority>(`/cases/${cid}/authorities`, { method: "POST", body: JSON.stringify(auth) }),

  // Reports
  generateReport: (cid: string) => api<any>(`/cases/${cid}/report`),

  // AI Lab (Under-the-hood engine)
  runLabSearch: (body: any) =>
    api<any>("/lab/search", { method: "POST", body: JSON.stringify(body) }),
  runLabGame: (body: any) =>
    api<any>("/lab/game", { method: "POST", body: JSON.stringify(body) }),
  runLabLogic: (body: any) =>
    api<any>("/lab/logic", { method: "POST", body: JSON.stringify(body) }),
  runLabCSP: (body: any) =>
    api<any>("/lab/csp", { method: "POST", body: JSON.stringify(body) }),
  runLabML: (mode = "classification", k = 3) =>
    api<any>(`/lab/ml?mode=${mode}&k=${k}`, { method: "POST" }),
  runLabRL: (body: any) =>
    api<any>("/lab/rl", { method: "POST", body: JSON.stringify(body) }),

  // Judicial Precedents & Court Record Intelligence
  searchPrecedents: (q = "", category = "All", court = "All", mode = "bm25") =>
    api<any[]>(`/precedents?q=${encodeURIComponent(q)}&category=${encodeURIComponent(category)}&court=${encodeURIComponent(court)}&mode=${mode}`),
  getPrecedent: (pid: string) => api<any>(`/precedents/${pid}`),
  analyzeJudgment: (data: { title: string; citation: string; court: string; text: string; category?: string }) =>
    api<any>("/precedents/extract", { method: "POST", body: JSON.stringify(data) }),
  generateSubmissionSheet: (precedent_ids: string[]) =>
    api<{ markdown: string }>("/precedents/submission-sheet", { method: "POST", body: JSON.stringify({ precedent_ids }) }),
  attachPrecedentToCase: (cid: string, pid: string) =>
    api<any>(`/cases/${cid}/precedents/${pid}/attach`, { method: "POST" }),
};
