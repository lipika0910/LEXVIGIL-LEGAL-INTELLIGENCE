import pytest
import pymupdf
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.pdf_preview import render_page
from backend.test_api import app, db, register, clean, release_database

def pdf():
    with pymupdf.open() as doc:
        for line in ('1.1 Services\nThe supplier shall provide services.', '2.1 Payment\nPayment is due within thirty days.'):
            page=doc.new_page(); page.insert_text((60,60),line)
        return doc.tobytes()

def test_bounded_render_and_invalid_pages():
    image=render_page(pdf(),2)
    assert image.startswith(b'\x89PNG')
    pix=pymupdf.Pixmap(image)
    assert max(pix.width,pix.height)<=1600
    for page in (0,3):
        with pytest.raises(HTTPException) as e: render_page(pdf(),page)
        assert e.value.status_code==404
    with pytest.raises(HTTPException) as e: render_page(b'not a pdf',1)
    assert e.value.status_code==415

def test_preview_is_private_and_expires():
    with TestClient(app) as a, TestClient(app) as b:
        register(a,'preview-a@example.com'); register(b,'preview-b@example.com')
        aid=a.post('/api/contracts/analyze',files={'file':('sample.pdf',pdf(),'application/pdf')},data={'store_original':'true'}).json()['id']
        url=f'/api/analyses/{aid}/original/pages/1'
        assert b.get(url).status_code==404
        result=a.get(url)
        assert result.status_code==200 and result.headers['content-type']=='image/png'
        assert result.headers['cache-control']=='no-store'
        with db.begin() as con: con.execute(text('UPDATE originals SET expires=0'))
        assert a.get(url).status_code==404
