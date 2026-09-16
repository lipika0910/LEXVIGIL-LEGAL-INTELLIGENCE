from pathlib import Path
import subprocess
import pytest
import pymupdf
from backend.ocr import recognize, availability
from backend.ingestion import extract_document

def scan(text, font=False):
    with pymupdf.open() as source:
        page=source.new_page()
        if font:
            page.insert_htmlbox(pymupdf.Rect(50,50,545,750),text,
                css="@font-face {font-family: localfont; src: url(Nirmala.ttc);} body {font-family: localfont; font-size:22pt;}", archive=pymupdf.Archive(r'C:\Windows\Fonts'))
        else: page.insert_text((60,80),text,fontsize=20)
        image=page.get_pixmap(matrix=pymupdf.Matrix(2,2)).tobytes('png')
    with pymupdf.open() as result:
        page=result.new_page(); page.insert_image(page.rect,stream=image)
        return result.tobytes(deflate=True)

def test_scan_still_requires_explicit_ocr():
    with pytest.raises(ValueError,match='OCR is required'): extract_document(scan('Payment must be made within thirty days.'),'scan.pdf')

def test_ocr_timeout_is_not_partial_success(monkeypatch):
    import backend.ocr as ocr
    monkeypatch.setattr(ocr,'configuration',lambda:('tesseract',Path('.runtime/tessdata')))
    monkeypatch.setattr(Path,'is_file',lambda self: True)
    def timeout(*args,**kwargs): raise subprocess.TimeoutExpired('tesseract',30)
    monkeypatch.setattr(ocr.subprocess,'run',timeout)
    with pymupdf.open(stream=scan('Payment must be made within thirty days.'),filetype='pdf') as doc:
        with pytest.raises(ValueError,match='30-second'): recognize(doc[0],'eng')

@pytest.mark.skipif(not availability()['available'],reason='Local Tesseract and three language packs required')
def test_real_english_scan_and_provenance():
    units=extract_document(scan('1.1 Payment\nPayment must be made within thirty days.'),'scan.pdf','eng')
    assert 'Payment' in units[0]['text']
    assert units[0]['location']['ocr']==1 and units[0]['page']==1
    assert units.metadata['extraction_method']=='pdf_ocr_mixed'
    assert any('review' in w for w in units.metadata['warnings'])

@pytest.mark.skipif(not availability()['available'] or not Path(r'C:\Windows\Fonts\Nirmala.ttc').exists(),reason='Local multilingual fixture font/runtime required')
@pytest.mark.parametrize('language,sentence,expected',[
    ('tam','பணம் முப்பது நாட்களில் செலுத்த வேண்டும்.','பணம்'),
    ('hin','भुगतान तीस दिनों के भीतर किया जाना चाहिए।','भुगतान'),
])
def test_real_indian_language_scans(language,sentence,expected):
    units=extract_document(scan(sentence,True),'scan.pdf',language)
    assert expected in units[0]['text'], units[0]['text']
