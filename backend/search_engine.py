"""Intelligent search engine with exact, phrase, TF-IDF, and BM25 ranked retrieval."""
import math
import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple


STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with'
}


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return re.findall(r'\b[a-zA-Z0-9_\-]+\b', text.lower())


def extract_snippets(text: str, query_tokens: Set[str], window: int = 140, max_snippets: int = 3) -> List[str]:
    """Extract snippet context windows around matched query terms."""
    if not text or not query_tokens:
        return [text[:window] + "..." if len(text) > window else text]

    snippets = []
    lower_text = text.lower()
    matches = []
    for token in query_tokens:
        for m in re.finditer(re.escape(token), lower_text):
            matches.append(m.start())

    if not matches:
        return [text[:window] + "..." if len(text) > window else text]

    matches.sort()
    merged_spans = []
    for pos in matches:
        start = max(0, pos - window // 2)
        end = min(len(text), pos + window // 2)
        if merged_spans and start <= merged_spans[-1][1]:
            merged_spans[-1] = (merged_spans[-1][0], max(merged_spans[-1][1], end))
        else:
            merged_spans.append((start, end))

    for start, end in merged_spans[:max_snippets]:
        prefix = "..." if start > 0 else ""
        suffix = "..." if end < len(text) else ""
        snippets.append(prefix + text[start:end].strip() + suffix)

    return snippets


class CaseSearchIndex:
    """In-memory BM25 & TF-IDF index for case documents."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.doc_term_freqs: Dict[str, Counter] = {}
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
        self.avg_doc_len: float = 0.0

    def add_document(self, doc_id: str, title: str, text: str, metadata: Optional[Dict[str, Any]] = None, pages: Optional[List[Dict[str, Any]]] = None):
        tokens = tokenize(text)
        self.documents[doc_id] = {
            "id": doc_id,
            "title": title,
            "text": text,
            "metadata": metadata or {},
            "pages": pages or []
        }
        self.doc_lengths[doc_id] = len(tokens)
        tf = Counter(tokens)
        self.doc_term_freqs[doc_id] = tf
        for term in tf:
            self.inverted_index[term].add(doc_id)
        self._update_stats()

    def remove_document(self, doc_id: str):
        if doc_id in self.documents:
            del self.documents[doc_id]
            del self.doc_lengths[doc_id]
            tf = self.doc_term_freqs.pop(doc_id, Counter())
            for term in tf:
                self.inverted_index[term].discard(doc_id)
                if not self.inverted_index[term]:
                    del self.inverted_index[term]
            self._update_stats()

    def _update_stats(self):
        total_len = sum(self.doc_lengths.values())
        num_docs = len(self.documents)
        self.avg_doc_len = (total_len / num_docs) if num_docs > 0 else 0.0

    def idf(self, term: str) -> float:
        n = len(self.inverted_index.get(term, set()))
        N = len(self.documents)
        if n == 0 or N == 0:
            return 0.0
        # Standard Lucene/BM25 IDF
        return math.log(1.0 + (N - n + 0.5) / (n + 0.5))

    def search_exact(self, query: str, doc_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Exact case-insensitive substring search."""
        query_clean = query.strip().lower()
        if not query_clean:
            return []
        results = []
        for doc_id, doc in self.documents.items():
            if doc_filter and doc_id != doc_filter:
                continue
            text_lower = doc["text"].lower()
            count = text_lower.count(query_clean)
            if count > 0:
                snippets = extract_snippets(doc["text"], {query_clean})
                results.append({
                    "doc_id": doc_id,
                    "title": doc["title"],
                    "score": float(count),
                    "method": "exact",
                    "match_count": count,
                    "explanation": f"Found {count} exact occurrences of '{query}'",
                    "snippets": snippets,
                    "metadata": doc["metadata"]
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def search_phrase(self, phrase: str, doc_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Phrase search enforcing token sequence."""
        return self.search_exact(phrase, doc_filter)

    def search_bm25(self, query: str, doc_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """BM25 probabilistic relevance ranking."""
        tokens = tokenize(query)
        clean_tokens = [t for t in tokens if t not in STOPWORDS] or tokens
        if not clean_tokens:
            return []

        N = len(self.documents)
        if N == 0:
            return []

        scores: Dict[str, float] = defaultdict(float)
        reasons: Dict[str, List[str]] = defaultdict(list)

        for term in clean_tokens:
            idf_val = self.idf(term)
            if idf_val <= 0:
                continue
            for doc_id in self.inverted_index.get(term, set()):
                if doc_filter and doc_id != doc_filter:
                    continue
                tf = self.doc_term_freqs[doc_id].get(term, 0)
                doc_len = self.doc_lengths.get(doc_id, 1)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                term_score = idf_val * ((tf * (self.k1 + 1.0)) / denom)
                scores[doc_id] += term_score
                reasons[doc_id].append(f"term '{term}' (tf={tf}, idf={round(idf_val, 2)})")

        results = []
        for doc_id, score in scores.items():
            doc = self.documents[doc_id]
            snippets = extract_snippets(doc["text"], set(clean_tokens))
            results.append({
                "doc_id": doc_id,
                "title": doc["title"],
                "score": round(score, 3),
                "method": "BM25",
                "explanation": f"Matched terms: {', '.join(reasons[doc_id])}",
                "snippets": snippets,
                "metadata": doc["metadata"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def search_tfidf(self, query: str, doc_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """TF-IDF ranked vector retrieval."""
        tokens = tokenize(query)
        clean_tokens = [t for t in tokens if t not in STOPWORDS] or tokens
        if not clean_tokens:
            return []

        N = len(self.documents)
        if N == 0:
            return []

        scores: Dict[str, float] = defaultdict(float)
        reasons: Dict[str, List[str]] = defaultdict(list)

        for term in clean_tokens:
            n = len(self.inverted_index.get(term, set()))
            if n == 0:
                continue
            idf_val = math.log((N + 1.0) / (n + 1.0)) + 1.0
            for doc_id in self.inverted_index.get(term, set()):
                if doc_filter and doc_id != doc_filter:
                    continue
                tf = self.doc_term_freqs[doc_id].get(term, 0)
                doc_len = self.doc_lengths.get(doc_id, 1)
                norm_tf = tf / doc_len
                tfidf = norm_tf * idf_val
                scores[doc_id] += tfidf
                reasons[doc_id].append(f"term '{term}' (tf={tf}, idf={round(idf_val, 2)})")

        results = []
        for doc_id, score in scores.items():
            doc = self.documents[doc_id]
            snippets = extract_snippets(doc["text"], set(clean_tokens))
            results.append({
                "doc_id": doc_id,
                "title": doc["title"],
                "score": round(score * 100.0, 3),
                "method": "TF-IDF",
                "explanation": f"Matched terms: {', '.join(reasons[doc_id])}",
                "snippets": snippets,
                "metadata": doc["metadata"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results
