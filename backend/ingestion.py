"""Bounded extraction; source offsets refer to extracted text, not binary byte positions."""
import hashlib
from io import BytesIO
from zipfile import ZipFile, BadZipFile
from .structure import ExtractedUnits, MAX_TEXT_CHARACTERS

def extract_document(data: bytes, name: str, ocr_language: str = ''):
    if ocr_language:
        from .ocr import LANGUAGES
        if ocr_language not in LANGUAGES: raise ValueError('Unsupported OCR language.')
    if len(data) > 15 * 1024 * 1024:
        raise ValueError("File exceeds the 15 MB limit.")
    suffix=name.lower().rsplit(".",1)[-1]
    units=[]; warnings=[]; total=0; ocr_pages=0
    def add(text, page=None, kind="text", location=None):
        nonlocal total
        total+=len(text)
        if total>MAX_TEXT_CHARACTERS or len(units)>=20000:
            raise ValueError("Extracted document exceeds the text or source-unit limit.")
        units.append(dict(text=text,page=page,kind=kind,location=location or {}))
    if suffix=="pdf":
        import pymupdf
        if not data.startswith(b"%PDF-"):
            raise ValueError("The file is not a valid PDF.")
        try:
            with pymupdf.open(stream=data,filetype="pdf") as document:
                if document.needs_pass:
                    raise ValueError("Unlock this PDF before uploading it.")
                if len(document)>200:
                    raise ValueError("Please upload at most 200 pages.")
                for index,page in enumerate(document):
                    text=page.get_text(sort=True)
                    if len(text.strip())<20:
                        if not text.strip() and not page.get_images() and not page.get_drawings():
                            warnings.append(f"Blank PDF page {index+1} preserved.")
                        elif ocr_language:
                            from .ocr import recognize
                            ocr_pages+=1
                            if ocr_pages>20: raise ValueError('At most 20 scanned pages can be processed per upload. No partial report was generated.')
                            text=recognize(page,ocr_language)
                            warnings.append(f'PDF page {index+1} uses local OCR ({ocr_language}); review recognized text against the original image. OCR accuracy is not guaranteed.')
                        else:
                            raise ValueError("This PDF has scanned or nearly empty pages. OCR is required before analysis; no partial report was generated.")
                    add(text,index+1,"page",{"ocr":1} if len(warnings) and warnings[-1].startswith(f'PDF page {index+1} uses local OCR') else {})
        except pymupdf.FileDataError as exc:
            raise ValueError("The file is not a readable PDF.") from exc
        media="application/pdf";method="pdf_ocr_mixed" if ocr_pages else "pdf_text"
    elif suffix=="docx":
        from docx import Document
        try:
            with ZipFile(BytesIO(data)) as archive:
                if sum(item.file_size for item in archive.infolist())>40*1024*1024:
                    raise ValueError("Unpacked document is too large.")
                if len(archive.infolist())>5000:
                    raise ValueError("DOCX archive contains too many entries.")
                if any(item.filename.lower().endswith("vbaproject.bin") for item in archive.infolist()):
                    raise ValueError("Macro-enabled documents are not supported.")
            document=Document(BytesIO(data))
        except (BadZipFile, KeyError) as exc:
            raise ValueError("Invalid DOCX file.") from exc
        # Metadata is positional in the DOCX body, never a fabricated page number.
        for block_index,block in enumerate(document.iter_inner_content(),1):
            if hasattr(block,"text"):
                add(block.text,kind="paragraph",location={"block":block_index})
                props=block._p.pPr
                if (props is not None and props.numPr is not None) or (block.style and block.style.name.startswith("List")):
                    warnings.append("DOCX automatic list numbering requires further resolution; paragraph text is preserved without inventing numbers.")
            else:
                for row_index,row in enumerate(block.rows,1):
                    for cell_index,cell in enumerate(row.cells,1):
                        add(cell.text,kind="table_cell",location={"block":block_index,"row":row_index,"cell":cell_index})
                        if cell.tables:
                            warnings.append("Nested DOCX table detected; this extraction is incomplete.")
                warnings.append("DOCX table text is preserved by cell; table-specific legal semantics are not yet evaluated.")
        media="application/vnd.openxmlformats-officedocument.wordprocessingml.document";method="docx_text"
    elif suffix in {"txt","md"}:
        try:
            add(data.decode("utf-8-sig"))
        except UnicodeDecodeError as exc:
            raise ValueError("Text uploads must use UTF-8.") from exc
        media="text/markdown" if suffix=="md" else "text/plain";method="utf8_text"
    else:
        raise ValueError("Use PDF, DOCX, TXT or Markdown.")
    return ExtractedUnits(units,sha256=hashlib.sha256(data).hexdigest(),media_type=media,
                          size_bytes=len(data),extraction_method=method,warnings=warnings)
