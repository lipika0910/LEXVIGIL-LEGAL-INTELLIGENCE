from io import BytesIO
import pytest
from backend.engine import analyze, extract, DEMO

def report(text=DEMO, as_of="2026-09-12"):
    return analyze([{"page": None, "text": text}], "test.md", as_of)

def test_sample_is_evidence_linked():
    r=report()
    assert len(r["clauses"]) == 6
    assert len(r["findings"]) == 1
    assert r["findings"][0]["category"] == "Temporal"
    assert set(r["findings"][0]["evidence"]) <= {c["id"] for c in r["clauses"]}
    assert r["findings"][0]["confidence"] is None

def test_future_amendment():
    source=DEMO.replace("is hereby amended", "effective from 1 January 2027 is hereby amended")
    assert not report(source)["findings"]
    assert report(source,"2027-01-01")["findings"]

def test_missing_reference():
    r=report("1.1 Obligation\nThe Buyer shall follow Section 9.9.")
    assert r["references"][0]["status"] == "UNRESOLVED"
    assert r["findings"][0]["category"] == "Cross-reference"

def test_clean_exception_not_conflict():
    assert not report("1.1 Termination\nEither party may terminate on 60 days notice.\n1.2 Breach\nNotwithstanding Section 1.1, immediate termination is permitted for uncured material breach.")["findings"]

def test_duplicate_definitions():
    assert report('1.1 Definition\n"Period" means 30 days.\n2.1 Definition\n"Period" means 45 days.')["findings"][0]["category"] == "Definition"

def test_docx_and_pdf():
    from docx import Document
    import pymupdf
    doc=Document()
    for line in DEMO.splitlines(): doc.add_paragraph(line)
    stream=BytesIO(); doc.save(stream)
    assert len(analyze(extract(stream.getvalue(),"test.docx"),"test")["clauses"]) == 6
    pdf=pymupdf.open(); page=pdf.new_page(); page.insert_text((50,50),DEMO,fontsize=9)
    r=analyze(extract(pdf.tobytes(),"test.pdf"),"test")
    assert len(r["clauses"]) == 6
    assert all(c["page"]==1 for c in r["clauses"])
    pdf.close()

@pytest.mark.parametrize("data,name",[(b"bad","fake.pdf"),(b"bad","fake.docx"),(b"x","test.exe"),(b"\xff","test.txt")])
def test_invalid_uploads(data,name):
    with pytest.raises(ValueError): extract(data,name)

def test_unstructured_rejected():
    with pytest.raises(ValueError): report("There are no numbered clauses.")

def test_ambiguous_effective_condition_not_applied():
    source=DEMO.replace("is hereby amended","effective upon execution is hereby amended")
    r=report(source)
    assert r["amendments"][0]["active"] is False
    assert any(f["category"]=="Amendment" for f in r["findings"])
    assert not any(f["category"]=="Temporal" for f in r["findings"])

def test_multipage_provenance():
    r=analyze([{"page":1,"text":"1.1 Term\nA clause starts here."},{"page":2,"text":"This continues the same clause.\n2.1 New clause\nA different clause."}],"two-page")
    assert r["clauses"][0]["page"]==1
    assert r["clauses"][0]["page_end"]==2
