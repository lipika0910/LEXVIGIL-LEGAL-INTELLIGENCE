"""Authenticated original encryption; development keys are DPAPI-protected on Windows."""
import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def windows_protect(data, decrypt=False):
    class Blob(ctypes.Structure):
        _fields_=[('size',wintypes.DWORD),('data',ctypes.POINTER(ctypes.c_ubyte))]
    buffer=ctypes.create_string_buffer(data)
    source=Blob(len(data),ctypes.cast(buffer,ctypes.POINTER(ctypes.c_ubyte)))
    output=Blob()
    crypt=ctypes.WinDLL('crypt32',use_last_error=True)
    function=crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    function.argtypes=[ctypes.POINTER(Blob),ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(Blob)]
    function.restype=wintypes.BOOL
    if not function(ctypes.byref(source),None,None,None,None,1,ctypes.byref(output)):
        raise RuntimeError('Windows could not unlock the local encryption key.')
    try: return ctypes.string_at(output.data,output.size)
    finally:
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.LocalFree.argtypes=[ctypes.c_void_p]
        kernel.LocalFree.restype=ctypes.c_void_p
        kernel.LocalFree(output.data)

class OriginalCipher:
    def __init__(self,key):
        if len(key)!=32: raise RuntimeError('Original encryption key must contain 32 bytes.')
        self.aes=AESGCM(key)

    @classmethod
    def load(cls, path:Path, existing_encrypted=False):
        supplied=os.getenv('ORIGINAL_ENCRYPTION_KEY')
        if supplied:
            try: return cls(base64.b64decode(supplied,validate=True))
            except (ValueError,TypeError): raise RuntimeError('Invalid original encryption key configuration.') from None
        if os.getenv('LEXVIGIL_ENV')=='production':
            raise RuntimeError('Production requires an externally managed encryption key.')
        if os.name!='nt':
            raise RuntimeError('Set ORIGINAL_ENCRYPTION_KEY outside Windows development.')
        if path.exists(): return cls(windows_protect(path.read_bytes(),decrypt=True))
        if existing_encrypted:
            raise RuntimeError('Encryption key is missing. Restore the original key; a replacement cannot decrypt existing files.')
        key=AESGCM.generate_key(bit_length=256)
        protected=windows_protect(key)
        path.parent.mkdir(parents=True,exist_ok=True)
        # Never overwrite an existing key, including during concurrent startup.
        try:
            with path.open('xb') as target:
                target.write(protected)
                target.flush()
                os.fsync(target.fileno())
        except FileExistsError:
            return cls(windows_protect(path.read_bytes(),decrypt=True))
        recovered=windows_protect(path.read_bytes(),decrypt=True)
        if recovered!=key: raise RuntimeError('Encryption key persistence verification failed.')
        return cls(recovered)

    def context(self,aid,owner):
        return json.dumps(['lexvigil-original-v1',aid,owner],separators=(',',':')).encode()

    def encrypt(self,data,aid,owner):
        nonce=os.urandom(12)
        return b'LVENC1'+nonce+self.aes.encrypt(nonce,data,self.context(aid,owner))

    def decrypt(self,data,aid,owner):
        if not data.startswith(b'LVENC1'): raise ValueError('Invalid encrypted original format.')
        return self.aes.decrypt(data[6:18],data[18:],self.context(aid,owner))
