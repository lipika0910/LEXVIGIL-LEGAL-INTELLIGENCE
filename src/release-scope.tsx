import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { api } from './api';

type Scope = { profile: string; research: boolean; ocr: boolean; original_storage: boolean; semantic_review: boolean };
const unavailable: Scope = { profile: 'unavailable', research: false, ocr: false, original_storage: false, semantic_review: false };
const ScopeContext = createContext<Scope>(unavailable);

export function ReleaseScopeProvider({ children }: { children: ReactNode }) {
  const [scope, setScope] = useState<Scope>(unavailable);
  useEffect(() => {
    const controller = new AbortController();
    api('/health', { signal: controller.signal }).then(result => {
      const s = result.release_scope;
      if (!s || !['development', 'showcase'].includes(s.profile)) return;
      setScope({ profile: s.profile, research: s.research === true, ocr: s.ocr === true,
        original_storage: s.original_storage === true, semantic_review: s.semantic_review === true });
    }).catch(() => {});
    return () => controller.abort();
  }, []);
  return <ScopeContext.Provider value={scope}>{children}</ScopeContext.Provider>;
}

export function useReleaseScope() { return useContext(ScopeContext); }
