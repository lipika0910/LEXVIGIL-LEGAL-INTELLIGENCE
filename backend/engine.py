"""Bounded contract pattern engine. All findings retain exact source clauses.

Pattern coverage is deliberately explicit; ambiguous semantics remain for review.
"""
import re
from datetime import date
from .structure import snapshot, parse_structure
from .domain import validate_contract_report

TAXONOMY = ['Numeric', 'Temporal', 'Obligation', 'Permission', 'Definition', 'Scope', 'Amendment', 'Exception', 'Cross-reference', 'Deontic', 'Sequence', 'Condition']
WORDS = {'one':1,'two':2,'three':3,'five':5,'seven':7,'ten':10,'fifteen':15,'thirty':30,'forty-five':45,'sixty':60,'ninety':90}
DEMO = '''MASTER SERVICES AGREEMENT — SYNTHETIC EXAMPLE
4.2 Payment Period
"Payment Period" means thirty (30) calendar days after receipt of an undisputed invoice.
8.1 Payment obligation
The Buyer shall pay each undisputed invoice within the Payment Period defined in Section 4.2.
12.4 Late-payment charge
A late-payment charge applies after thirty (30) calendar days from receipt of an undisputed invoice.
17.3 Amendment
The Payment Period defined in Section 4.2 is hereby amended from thirty (30) days to forty-five (45) calendar days.
18.1 Termination
Either party may terminate for convenience on sixty (60) days notice.
18.2 Breach exception
Notwithstanding Section 18.1, immediate termination is permitted for an uncured material breach.
'''

def extract(data: bytes, name: str, ocr_language: str = ''):
    from .ingestion import extract_document
    return extract_document(data, name, ocr_language)

def durations(text):
    return [int(x) for x in re.findall(r'\b(\d+)\)?\s*(?:calendar\s+|business\s+|working\s+)?days?\b',text,re.I)]

def analyze(pages, name, as_of=None):
    as_of = date.fromisoformat(as_of) if as_of else date.today()
    document = snapshot(pages, name)
    parsed, unassigned = parse_structure(document)
    clauses = [c.model_dump() for c in parsed]
    mapping={}
    for c in clauses: mapping.setdefault(c['label'],[]).append(c)
    references=[]; definitions=[]; findings=[]; amendments=[]
    def finding(kind,title,a,b,reason,chain=None,severity='MEDIUM'):
        ids=list(dict.fromkeys(chain or [a['id'],b['id']]))
        key=(kind,tuple(sorted(ids)))
        if any((f['category'],tuple(sorted(f['evidence'])))==key for f in findings): return
        findings.append({'id':f'LV-{len(findings)+1:04d}','category':kind,'title':title,'severity':severity,'explanation':reason,'evidence':ids,'review_required':True,'verification':'NOT_RUN','confidence':None})
    for c in clauses:
        for target in re.findall(r'\b(?:section|clause)\s+(\d+(?:\.\d+)*(?:\([a-z]\))?)',c['text'],re.I):
            candidates=mapping.get(target,[])
            resolved=candidates[0]['id'] if len(candidates)==1 else None
            references.append({'source':c['id'],'target':resolved,'label':target,'type':'references','status':'RESOLVED' if resolved else 'UNRESOLVED'})
            if not resolved: finding('Cross-reference',f'Unresolved reference to §{target}',c,c,'The target is missing or its numbering is ambiguous. No target was guessed.',severity='LOW')
        for term,value in re.findall(r'["“]([^"”]+)["”]\s+(?:shall\s+)?means?\s+([^\n]+)',c['text'],re.I):
            definitions.append({'term':term,'value':value,'source':c['id'],'effective_value':value,'amendment':None})
    for definition in definitions:
        for c in clauses:
            if c['id']==definition['source']: continue
            if definition['term'].lower() in c['text'].lower():
                references.append({'source':c['id'],'target':definition['source'],'label':definition['term'],'type':'uses','status':'RESOLVED'})
            if definition['term'].lower() not in c['text'].lower() or not re.search(r'\bamend(?:ed|ment|s)?\b',c['text'],re.I): continue
            ds=durations(c['text'])
            if not ds: continue
            effective_match=re.search(r'(?:effect from|effective(?: from)?)\s+(\d{1,2}\s+\w+\s+\d{4}|\d{4}-\d{2}-\d{2})',c['text'],re.I)
            effective=None
            if effective_match:
                from datetime import datetime
                for fmt in ('%d %B %Y','%Y-%m-%d'):
                    try: effective=datetime.strptime(effective_match[1],fmt).date(); break
                    except ValueError: pass
            ambiguous_date=bool(re.search(r'\b(?:effective|effect from|subject to|upon execution|on signing)\b',c['text'],re.I)) and effective is None
            active=(not effective or effective<=as_of) and not ambiguous_date
            if ambiguous_date:
                finding('Amendment','Amendment activation requires review',c,c,'The effective date or condition could not be resolved. This amendment was not applied automatically.')
            amendments.append({'source':c['id'],'target':definition['source'],'value':f'{ds[-1]} days','active':active,'effective_date':str(effective) if effective else None})
            references.append({'source':c['id'],'target':definition['source'],'label':definition['term'],'type':'amends','status':'RESOLVED'})
            if active:
                if definition['amendment']:
                    finding('Amendment','Multiple amendments require precedence review',c,next(x for x in clauses if x['id']==definition['amendment']),'Multiple active amendments were found; their priority is unresolved.')
                    definition['effective_value']='Unresolved precedence'
                else: definition['effective_value']=f'{ds[-1]} days'
                definition['amendment']=c['id']
    for d in definitions:
        values=durations(d['effective_value'])
        if 'payment' not in d['term'].lower() or not d['amendment'] or not values: continue
        a=next(c for c in clauses if c['id']==d['amendment'])
        for b in clauses:
            if not re.search(r'late.payment|overdue|late charge|penalt',b['text'],re.I): continue
            ds=durations(b['text'])
            if ds and ds[0]<values[-1]:
                chain=[d['source']]+[e['source'] for e in references if e['type']=='uses' and e['target']==d['source']]+[a['id'],b['id']]
                finding('Temporal','Payment-term inconsistency',a,b,f'The active amendment specifies {values[-1]} days; this clause has a {ds[0]}-day late-payment trigger. Confirm that both use the same trigger event and invoice scope.',chain,'HIGH')
    for i,a in enumerate(definitions):
        for b in definitions[i+1:]:
            if a['term'].lower()==b['term'].lower() and a['value']!=b['value']:
                ca=next(c for c in clauses if c['id']==a['source']); cb=next(c for c in clauses if c['id']==b['source'])
                finding('Definition',f'Differing definitions of {a["term"]}',ca,cb,'This term has different definitions. Scope and precedence require review.')
    result = {'kind':'contract','title':name,'as_of':str(as_of),'clauses':clauses,'references':references,'definitions':definitions,'amendments':amendments,'findings':findings,'summary':{'clauses':len(clauses),'references':len(references),'resolved':sum(e['status']=='RESOLVED' for e in references),'definitions':len(definitions),'amendments':len(amendments),'conflicts':len(findings)},'limitations':['Pattern engine coverage: payment amendments, differing definitions and unresolved numbered references. Other taxonomy categories require further implementation and evaluation.','No finding does not certify that the contract is conflict-free.','DOCX and plain text use clause provenance; page numbers are not invented.'],'verification':'NOT_CONFIGURED'}
    result.update(schema_version="1.0", rule_version="patterns-0.1.0", document=document.model_dump(), unassigned_spans=[s.model_dump() for s in unassigned])
    result["limitations"].extend(document.warnings)
    if any(script in document.scripts for script in ("Tamil", "Devanagari", "Other")):
        result["limitations"].append("Non-Latin text is preserved. Current deterministic semantic patterns are primarily English; multilingual OCR and legal reasoning have not been validated.")
    return validate_contract_report(result)
