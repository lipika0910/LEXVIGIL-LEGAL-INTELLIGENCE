import hashlib
import os
import pytest
from sqlalchemy import create_engine,text
from backend.originals import OriginalStore
from backend.encryption import OriginalCipher

def legacy(db):
    with db.begin() as con:
        con.execute(text('CREATE TABLE originals (analysis_id TEXT PRIMARY KEY, owner TEXT, filename TEXT, payload BLOB, size INTEGER, sha256 TEXT, consent_version TEXT, consented_at DOUBLE, expires DOUBLE)'))
        for aid in ('a','b'):
            data=('private '+aid).encode()
            con.execute(text('INSERT INTO originals VALUES (:id,\'owner\',\'file.txt\',:data,:size,:hash,\'original-48h-v1\',100,172900)'),{'id':aid,'data':data,'size':len(data),'hash':hashlib.sha256(data).hexdigest()})

def test_migration_preserves_deadlines_and_restarts(tmp_path):
    db=create_engine('sqlite:///'+str(tmp_path/'originals.db'))
    legacy(db)
    key=os.urandom(32)
    store=OriginalStore(db,OriginalCipher(key))
    with db.connect() as con:
        for row in con.execute(text('SELECT * FROM originals')).mappings():
            assert row['encryption_version']==1
            assert row['expires']==172900 and row['consented_at']==100
            assert bytes(row['payload']).startswith(b'LVENC1')
            assert store.decrypt(row['payload'],row['analysis_id'],'owner')==('private '+row['analysis_id']).encode()
    OriginalStore(db,OriginalCipher(key))
    db.dispose()

def test_mid_migration_failure_rolls_back_payload_and_schema(tmp_path):
    db=create_engine('sqlite:///'+str(tmp_path/'rollback.db'))
    legacy(db)
    class BrokenCipher(OriginalCipher):
        def encrypt(self,data,aid,owner):
            if aid=='b': raise RuntimeError('Injected failure')
            return super().encrypt(data,aid,owner)
    with pytest.raises(RuntimeError,match='Injected'):
        OriginalStore(db,BrokenCipher(os.urandom(32)))
    with db.connect() as con:
        assert 'encryption_version' not in {r[1] for r in con.execute(text('PRAGMA table_info(originals)'))}
        assert con.execute(text('SELECT payload FROM originals ORDER BY analysis_id')).scalars().all()==[b'private a',b'private b']
    db.dispose()
