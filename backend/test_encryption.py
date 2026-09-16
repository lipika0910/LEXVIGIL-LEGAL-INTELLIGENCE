import os
import pytest
from cryptography.exceptions import InvalidTag
from backend.encryption import OriginalCipher

def test_roundtrip_is_random_and_bound_to_owner_and_document():
    cipher=OriginalCipher(os.urandom(32)); plain=b'private contract text'
    first=cipher.encrypt(plain,'a','owner')
    assert first!=cipher.encrypt(plain,'a','owner') and plain not in first
    assert cipher.decrypt(first,'a','owner')==plain
    for aid,owner in [('b','owner'),('a','other')]:
        with pytest.raises(InvalidTag): cipher.decrypt(first,aid,owner)
    damaged=first[:-1]+bytes([first[-1]^1])
    with pytest.raises(InvalidTag): cipher.decrypt(damaged,'a','owner')
    with pytest.raises(InvalidTag): OriginalCipher(os.urandom(32)).decrypt(first,'a','owner')

@pytest.mark.skipif(os.name!='nt',reason='Windows development key protection')
def test_protected_key_survives_restart_and_missing_key_fails(tmp_path,monkeypatch):
    monkeypatch.delenv('ORIGINAL_ENCRYPTION_KEY',raising=False)
    monkeypatch.delenv('LEXVIGIL_ENV',raising=False)
    path=tmp_path/'key.dpapi'
    first=OriginalCipher.load(path)
    encrypted=first.encrypt(b'contract','a','owner')
    assert OriginalCipher.load(path,existing_encrypted=True).decrypt(encrypted,'a','owner')==b'contract'
    with pytest.raises(RuntimeError,match='missing'):
        OriginalCipher.load(tmp_path/'absent.dpapi',existing_encrypted=True)
