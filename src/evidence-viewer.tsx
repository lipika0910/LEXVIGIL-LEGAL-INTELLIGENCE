import { useState } from 'react';
import './evidence-viewer.css';

export type EvidenceDocument = {
  document?: { media_type: string; extraction_method: string; units: { id: string; text: string; page: number | null; kind: string; location: Record<string, number> }[] };
  clauses: { id: string; label: string; title: string; spans?: { unit_id: string; start: number; end: number }[] }[];
};

export function EvidenceViewer({ id, report, originalAvailable }: { id: string; report: EvidenceDocument; originalAvailable: boolean }) {
  const [open,setOpen]=useState(false);
  const [unitIndex,setUnitIndex]=useState(0);
  const [clauseId,setClauseId]=useState('');
  const [showPage,setShowPage]=useState(false);
  const [imageError,setImageError]=useState(false);
  const units=report.document?.units || [];
  const unit=units[unitIndex];
  const clause=report.clauses.find(c=>c.id===clauseId);
  const ranges=(clause?.spans || []).filter(s=>s.unit_id===unit?.id).sort((a,b)=>a.start-b.start);
  // Backend offsets count Unicode code points, not JavaScript UTF-16 code units.
  const chars=Array.from(unit?.text || '');
  const parts=[];
  let cursor=0;
  for (const span of ranges) {
    parts.push(chars.slice(cursor,span.start).join(''));
    parts.push(<mark key={span.start}>{chars.slice(span.start,span.end).join('')}</mark>);
    cursor=span.end;
  }
  parts.push(chars.slice(cursor).join(''));
  function changeUnit(index:number) { setUnitIndex(index); setImageError(false); }
  if (!units.length) return <p>Source snapshot is unavailable for this older report. Re-analyze to obtain traceable source units.</p>;
  return <section className="evidence-viewer" aria-label="Evidence viewer">
    <button className="button light" aria-expanded={open} onClick={()=>setOpen(!open)}>{open?'Close evidence viewer':'Open evidence viewer'}</button>
    {open && <>
      <h3>Source evidence</h3>
      <p>Highlights refer to exact extracted text, not positions on the PDF image. DOCX and text locations are source units, not invented page numbers.</p>
      <div className="evidence-controls">
        <label>Highlight clause<select value={clauseId} onChange={e=>{
          setClauseId(e.target.value);
          const first=report.clauses.find(c=>c.id===e.target.value)?.spans?.[0];
          const index=units.findIndex(u=>u.id===first?.unit_id);
          if(index>=0) changeUnit(index);
        }}><option value="">No highlight</option>{report.clauses.map(c=><option key={c.id} value={c.id}>{c.label} {c.title}</option>)}</select></label>
        <label>Source location<select value={unitIndex} onChange={e=>changeUnit(Number(e.target.value))}>{units.map((u,i)=><option key={u.id} value={i}>{u.page ? `PDF page ${u.page}` : `Source unit ${i+1} · ${u.kind}`}</option>)}</select></label>
      </div>
      <div className="evidence-controls">
        <button className="button light" disabled={unitIndex===0} onClick={()=>changeUnit(unitIndex-1)}>Previous source</button>
        <span>{unitIndex+1} / {units.length}</span>
        <button className="button light" disabled={unitIndex===units.length-1} onClick={()=>changeUnit(unitIndex+1)}>Next source</button>
      </div>
      <p>Extraction: {report.document?.extraction_method} · {unit.page ? `PDF page ${unit.page}` : JSON.stringify(unit.location)}</p>
      {unit.location.ocr===1 && <p role="note">OCR-recognized text — compare it with the original page before relying on wording, numbers or dates.</p>}
      <pre className="evidence-text" aria-label="Extracted source text">{parts}</pre>
      {clauseId && !ranges.length && <p>This clause has no span in the selected source unit.</p>}
      {unit.page && report.document?.media_type==='application/pdf' && <>
        {originalAvailable ? <>
          <button className="button light" onClick={()=>{setShowPage(!showPage);setImageError(false);}}>{showPage?'Hide PDF page':'Show PDF page'}</button>
          {showPage && (imageError ? <p role="alert">Page preview is unavailable. The original may have expired or been deleted. Refresh the report to check.</p> : <img key={unit.page} className="evidence-page" src={`/api/analyses/${id}/original/pages/${unit.page}`} alt={`Original PDF page ${unit.page}`} onError={()=>setImageError(true)} />)}
        </> : <p>The PDF image requires an unexpired stored original. Extracted source text remains available under report retention.</p>}
      </>}
    </>}
  </section>;
}
