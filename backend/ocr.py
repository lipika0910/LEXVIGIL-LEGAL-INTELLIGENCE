"""Local-only Tesseract adapter. Image input and recognized text use pipes, not temp files."""
import os
from pathlib import Path
import shutil
import subprocess

LANGUAGES={'eng','tam','hin','eng+tam+hin'}
ROOT=Path(__file__).resolve().parent.parent

def configuration():
    executable=os.getenv('TESSERACT_CMD') or shutil.which('tesseract')
    if not executable:
        candidate=Path(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        if candidate.is_file(): executable=str(candidate)
    data=Path(os.getenv('TESSDATA_PREFIX',str(ROOT/'.runtime'/'tessdata')))
    return executable,data

def availability():
    executable,data=configuration()
    languages=[x for x in ('eng','tam','hin') if (data/(x+'.traineddata')).is_file()]
    return {'available':bool(executable and len(languages)==3),'languages':languages,'max_scanned_pages':20}

def recognize(page, language):
    if language not in LANGUAGES: raise ValueError('Unsupported OCR language.')
    executable,data=configuration()
    if not executable or any(not (data/(x+'.traineddata')).is_file() for x in language.split('+')):
        raise ValueError('Local OCR runtime or selected language pack is unavailable. Configure Tesseract before retrying.')
    import pymupdf
    width,height=page.rect.width,page.rect.height
    if width<=0 or height<=0: raise ValueError('Invalid scanned page dimensions.')
    scale=min(300/72,3000/max(width,height))
    image=page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).tobytes('png')
    try:
        result=subprocess.run([executable,'stdin','stdout','--tessdata-dir',str(data),'-l',language,'--psm','3'],
            input=image,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,check=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    except subprocess.TimeoutExpired:
        raise ValueError('OCR exceeded the 30-second page limit. No partial report was generated.') from None
    except OSError:
        raise ValueError('Local OCR could not start. Check the Tesseract installation.') from None
    if result.returncode: raise ValueError('Local OCR failed. Check scan quality and installed language packs.')
    text=result.stdout.decode('utf-8',errors='strict')
    if len(text.strip())<20: raise ValueError('OCR could not recover enough text. Upload a clearer scan; no partial report was generated.')
    return text
