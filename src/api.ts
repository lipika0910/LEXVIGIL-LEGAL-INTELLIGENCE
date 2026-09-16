export async function api<T = any>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  let response: Response;
  try { response = await fetch("/api" + path, {
    credentials: "same-origin",
    ...init,
    headers: {
      ...(init.body && !(init.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...init.headers,
    },
    signal: init.signal ?? AbortSignal.timeout(30000),
  }); } catch {
    throw new Error("Cannot reach the LexVigil service. Check your connection and ensure the API is running, then retry.");
  }
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("/auth/")) {
      window.dispatchEvent(new Event("lexvigil:session-expired"));
    }
    let message = response.status >= 500
      ? "The LexVigil service is unavailable. Ensure the API is running, then retry."
      : "Request failed. Please try again.";
    try {
      const body = await response.json();
      message =
        typeof body.detail === "string"
          ? body.detail
          : "Please check the submitted fields.";
    } catch {}
    throw new Error(message);
  }
  return response.json();
}
export type Clause = {
  id: string;
  label: string;
  title: string;
  text: string;
  page: number | null;
  page_end?: number | null;
};
export type Finding = {
  id: string;
  category: string;
  title: string;
  severity: string;
  explanation: string;
  evidence: string[];
  review_required: boolean;
  verification: string;
  confidence: number | null;
  semantic?: { verdict: string; explanation: string };
};
export type Contract = {
  kind: "contract";
  title: string;
  as_of: string;
  clauses: Clause[];
  references: {
    source: string;
    target: string | null;
    label: string;
    type: string;
    status: string;
  }[];
  definitions: {
    term: string;
    value: string;
    effective_value: string;
    source: string;
    amendment: string | null;
  }[];
  amendments: any[];
  findings: Finding[];
  summary: Record<string, number>;
  limitations: string[];
  verification: string;
};
export type Research = {
  kind: "disputes" | "research";
  title: string;
  description: string;
  answer: string;
  state: string;
  district: string;
  sources: {
    title: string;
    url: string;
    status: string;
    retrieved_at: string;
  }[];
  limitations: string[];
};
export type Job = {
  processing?: { durable: boolean; state?: string; attempts?: number };
  id: string;
  title: string;
  status: string;
  saved: number;
  created: number;
  expires: number;
  error: string | null;
  result: Contract | Research | null;
  kind: string;
};
