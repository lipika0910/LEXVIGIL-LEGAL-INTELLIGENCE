export interface CaseItem {
  id: string;
  owner: string;
  title: string;
  reference: string;
  category: string;
  parties: string[];
  jurisdiction?: string;
  court?: string;
  description?: string;
  status: string;
  tags: string[];
  doc_count?: number;
  fact_count?: number;
  evidence_count?: number;
  inconsistency_count?: number;
  created_at: number;
  updated_at: number;
}

export interface CaseDocument {
  id: string;
  case_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: number;
  extracted_text?: string;
  pages?: { page: number; text: string }[];
  metadata?: Record<string, any>;
}

export interface CaseFact {
  id: string;
  case_id: string;
  document_id: string;
  text: string;
  entity: string;
  category: string;
  fact_type: string;
  page?: number;
  status: 'candidate' | 'confirmed' | 'rejected';
  confidence?: number;
  filename?: string;
  created_at: number;
}

export interface EvidenceItem {
  id: string;
  case_id: string;
  title: string;
  category: string;
  description: string;
  source_doc_id?: string;
  page?: number;
  status: string;
  filename?: string;
  created_at: number;
}

export interface EvidenceRelationship {
  id: string;
  case_id: string;
  source_id: string;
  target_id: string;
  relation_type: string;
  explanation: string;
  is_suggested: boolean;
  is_confirmed: boolean;
  created_at: number;
}

export interface TimelineEvent {
  id: string;
  case_id: string;
  date_str: string;
  title: string;
  description: string;
  document_id?: string;
  party: string;
  verification_status: string;
  filename?: string;
  created_at: number;
}

export interface InconsistencyItem {
  id: string;
  case_id: string;
  issue_type: string;
  title: string;
  explanation: string;
  item_a_id?: string;
  item_b_id?: string;
  status: 'flagged' | 'reviewed' | 'resolved';
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  created_at: number;
}

export interface ReasoningRule {
  id: string;
  name: string;
  description: string;
  rule: {
    premises: { predicate: string; args: string[] }[];
    conclusion: { predicate: string; args: string[] };
  };
}

export interface ArgumentItem {
  id: string;
  case_id: string;
  issue_title: string;
  argument_text: string;
  supporting_evidence_ids: string[];
  assumptions: string;
  counterarguments: string;
  status: string;
  created_at: number;
}

export interface LegalAuthority {
  id: string;
  case_id: string;
  title: string;
  citation: string;
  jurisdiction: string;
  authority_type: string;
  url: string;
  notes: string;
  verification_status: string;
  created_at: number;
}
