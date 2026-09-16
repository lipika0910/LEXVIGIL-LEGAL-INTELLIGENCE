import { useEffect, useState } from 'react';
import { api } from './api';
import './original.css';
import { EvidenceViewer, type EvidenceDocument } from './evidence-viewer';

export function OriginalFile({ id, report }: { id: string; report?: EvidenceDocument }) {
  const [info, setInfo] = useState<{ available: boolean; filename?: string; expires?: number } | null>(null);
  const [error, setError] = useState('');
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    api('/analyses/' + id + '/original').then(r => { if (active) setInfo(r); }).catch(e => { if (active) setError(e.message); });
    return () => { active = false; };
  }, [id]);
  return <section className="original-panel" aria-label="Original document">
    <h3>Original document</h3>
    {error && <p role="alert">{error}</p>}
    {!info && !error && <p>Checking original availability…</p>}
    {info?.available ? <>
      <p>{info.filename} · Expires {new Date(info.expires! * 1000).toLocaleString()}. Saving this report does not extend the expiry.</p>
      <a className="button light" href={'/api/analyses/' + id + '/original/download'}>Download original</a>
      <button className="button light" onClick={() => setConfirm(true)}>Delete original</button>
      {confirm && <div role="group" aria-label="Confirm original deletion">
        <p>Delete the stored original now? Completed analysis and extracted text will remain. Pending analysis that depends on this original will not publish a result. Downloaded copies are not deleted.</p>
        <button className="button light" disabled={busy} onClick={async () => {
          setBusy(true); setError('');
          try { await api('/analyses/' + id + '/original', { method: 'DELETE' }); setInfo({ available: false }); setConfirm(false); }
          catch (e) { setError((e as Error).message); }
          finally { setBusy(false); }
        }}>Confirm delete original</button>
        <button className="button light" disabled={busy} onClick={() => setConfirm(false)}>Cancel</button>
      </div>}
    </> : info && <p>No original is available: it was not stored, was deleted, or expired. Extracted evidence remains subject to report retention.</p>}
    {report && <EvidenceViewer id={id} report={report} originalAvailable={Boolean(info?.available)} />}
  </section>;
}
