"""Bounded development original storage; never exposed through a public data API."""
import hashlib
import time
from threading import RLock
from fastapi import Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import text
from pathlib import Path
from cryptography.exceptions import InvalidTag
from .encryption import OriginalCipher

TTL = 48 * 60 * 60
CONSENT_VERSION = 'original-48h-v1'

class OriginalStore:
    def __init__(self, db, cipher=None):
        self.db = db
        self.lock = RLock()
        self.enabled = db.dialect.name == 'sqlite'
        if not self.enabled: return
        binary = 'BLOB' if db.dialect.name == 'sqlite' else 'BYTEA'
        with db.begin() as con:
            con.exec_driver_sql('BEGIN IMMEDIATE')
            con.execute(text(f'CREATE TABLE IF NOT EXISTS originals (analysis_id TEXT PRIMARY KEY, owner TEXT NOT NULL, filename TEXT NOT NULL, payload {binary} NOT NULL, size INTEGER NOT NULL, sha256 TEXT NOT NULL, consent_version TEXT NOT NULL, consented_at DOUBLE PRECISION NOT NULL, expires DOUBLE PRECISION NOT NULL)'))
            con.execute(text('CREATE INDEX IF NOT EXISTS originals_expiry_idx ON originals(expires)'))
            con.execute(text('CREATE INDEX IF NOT EXISTS originals_owner_idx ON originals(owner)'))
            columns={r[1] for r in con.execute(text('PRAGMA table_info(originals)'))}
            if 'encryption_version' not in columns:
                con.execute(text('ALTER TABLE originals ADD COLUMN encryption_version INTEGER NOT NULL DEFAULT 0'))
            encrypted=con.execute(text('SELECT COUNT(*) FROM originals WHERE encryption_version=1')).scalar()
            self.cipher=cipher or OriginalCipher.load(Path(__file__).resolve().parent.parent/'.runtime'/'original-key.dpapi',bool(encrypted))
            rows=con.execute(text('SELECT analysis_id,owner,payload,sha256,encryption_version FROM originals')).mappings()
            for row in rows:
                aid,uid=row['analysis_id'],row['owner']
                if row['encryption_version']==1:
                    plain=self.cipher.decrypt(bytes(row['payload']),aid,uid)
                elif row['encryption_version']==0:
                    plain=bytes(row['payload'])
                    payload=self.cipher.encrypt(plain,aid,uid)
                    if self.cipher.decrypt(payload,aid,uid)!=plain: raise RuntimeError('Original encryption verification failed.')
                    con.execute(text('UPDATE originals SET payload=:payload,encryption_version=1 WHERE analysis_id=:aid'),{'payload':payload,'aid':aid})
                else: raise RuntimeError('Unknown original encryption version.')
                if hashlib.sha256(plain).hexdigest()!=row['sha256']: raise RuntimeError('Original content integrity check failed.')

    def decrypt(self,data,aid,uid):
        try: return self.cipher.decrypt(bytes(data),aid,uid)
        except (InvalidTag,ValueError):
            raise HTTPException(503,'Original integrity check failed. Restore the correct encryption key or contact the operator.') from None

    def put(self, aid, uid, name, data):
        if not self.enabled: raise HTTPException(503, 'Original storage is not configured for this deployment.')
        now = time.time()
        with self.lock, self.db.begin() as con:
            size = con.execute(text('SELECT COALESCE(SUM(size),0) FROM originals WHERE owner=:owner'), {'owner':uid}).scalar()
            total = con.execute(text('SELECT COALESCE(SUM(size),0) FROM originals')).scalar()
            if size + len(data) > 100*1024*1024 or total + len(data) > 1024*1024*1024:
                raise HTTPException(413, 'Temporary original storage is full. Delete originals or analyze without storing the original.')
            con.execute(text('INSERT INTO originals (analysis_id,owner,filename,payload,size,sha256,consent_version,consented_at,expires,encryption_version) VALUES (:aid,:owner,:name,:data,:size,:hash,:version,:now,:expires,1)'),
                {'aid':aid,'owner':uid,'name':name,'data':self.cipher.encrypt(data,aid,uid),'size':len(data),'hash':hashlib.sha256(data).hexdigest(),'version':CONSENT_VERSION,'now':now,'expires':now+TTL})

    def sweep(self, con):
        if not self.enabled: return
        con.execute(text('DELETE FROM originals WHERE expires<=:now OR NOT EXISTS (SELECT 1 FROM analyses WHERE analyses.id=originals.analysis_id)'), {'now':time.time()})

    def install(self, app, owner, get_record, rate):
        @app.get('/api/analyses/{aid}/original/pages/{page_number}')
        def preview(aid: str, page_number: int, uid=Depends(owner)):
            get_record(aid, uid)
            rate('preview:'+uid,30)
            if not self.enabled: raise HTTPException(404, 'Original storage is not configured.')
            with self.db.connect() as con:
                row=con.execute(text('SELECT payload FROM originals WHERE analysis_id=:aid AND owner=:owner AND expires>:now'), {'aid':aid,'owner':uid,'now':time.time()}).first()
            if not row: raise HTTPException(404, 'Original not stored, deleted or expired.')
            from .pdf_preview import render_page
            return Response(render_page(self.decrypt(row[0],aid,uid),page_number), media_type='image/png', headers={'Cache-Control':'no-store'})

        @app.get('/api/analyses/{aid}/original')
        def metadata(aid: str, uid=Depends(owner)):
            get_record(aid, uid)
            if not self.enabled: return {'available':False}
            with self.db.connect() as con:
                row = con.execute(text('SELECT filename,size,sha256,consent_version,consented_at,expires FROM originals WHERE analysis_id=:aid AND owner=:owner AND expires>:now'), {'aid':aid,'owner':uid,'now':time.time()}).mappings().first()
            return {'available':bool(row), **(dict(row) if row else {})}

        @app.get('/api/analyses/{aid}/original/download')
        def download(aid: str, uid=Depends(owner)):
            get_record(aid, uid)
            if not self.enabled: raise HTTPException(404, 'Original storage is not configured.')
            with self.db.connect() as con:
                row = con.execute(text('SELECT payload FROM originals WHERE analysis_id=:aid AND owner=:owner AND expires>:now'), {'aid':aid,'owner':uid,'now':time.time()}).first()
            if not row: raise HTTPException(404, 'Original not stored, deleted or expired.')
            # Never render untrusted uploaded bytes as HTML in the application origin.
            return Response(self.decrypt(row[0],aid,uid), media_type='application/octet-stream', headers={'Content-Disposition':'attachment; filename="lexvigil-original"','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})

        @app.delete('/api/analyses/{aid}/original')
        def delete(aid: str, uid=Depends(owner)):
            get_record(aid, uid)
            if not self.enabled: return {'deleted':True}
            with self.db.begin() as con:
                con.execute(text('DELETE FROM originals WHERE analysis_id=:aid AND owner=:owner'), {'aid':aid,'owner':uid})
            return {'deleted':True}
