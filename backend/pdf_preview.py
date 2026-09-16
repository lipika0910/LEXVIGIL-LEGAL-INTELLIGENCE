"""Render bounded PDF pages as passive PNG; do not embed uploaded PDF scripts."""
from fastapi import HTTPException

def render_page(data: bytes, page_number: int):
    import pymupdf
    if not data.startswith(b'%PDF-'):
        raise HTTPException(415, 'Page preview is available for PDF originals only.')
    try:
        with pymupdf.open(stream=data, filetype='pdf') as doc:
            if doc.needs_pass: raise HTTPException(422, 'Unlock this PDF before previewing.')
            if len(doc)>200: raise HTTPException(422, 'PDF exceeds the 200-page preview limit.')
            if page_number < 1 or page_number > len(doc): raise HTTPException(404, 'PDF page not found.')
            page=doc[page_number-1]
            width,height=page.rect.width,page.rect.height
            if width<=0 or height<=0: raise HTTPException(422, 'Invalid PDF page dimensions.')
            scale=min(1.5,1600/max(width,height))
            return page.get_pixmap(matrix=pymupdf.Matrix(scale,scale), alpha=False, annots=True).tobytes('png')
    except (pymupdf.FileDataError, RuntimeError, ValueError):
        raise HTTPException(422, 'This PDF page could not be rendered.') from None
