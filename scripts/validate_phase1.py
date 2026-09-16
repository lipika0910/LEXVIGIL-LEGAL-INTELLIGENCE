"""Read-only Phase 1 integrity checks; not software or legal-quality certification."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs"/"phase-1"

def validate(data, release=False):
    errors=[]
    def check(ok, message):
        if not ok: errors.append(message)
    def local(path):
        target=(ROOT/path).resolve()
        if not target.is_relative_to(ROOT):
            errors.append("Path escapes workspace: "+path)
            return None
        return target
    check(data.get("schema_version")==1,"Unsupported schema version")
    sources={}
    for item in data.get("sources",[]):
        check(item["id"] not in sources,"Duplicate source: "+item["id"])
        path=local(item["path"])
        if not path or not path.is_file():
            errors.append("Missing source: "+item["path"]); continue
        raw=path.read_bytes()
        check(hashlib.sha256(raw).hexdigest()==item["sha256"],"Source fingerprint changed: "+item["path"])
        sources[item["id"]]=raw.decode("utf-8-sig")
    rows={}; scenarios=set()
    for row in data.get("requirements",[]):
        rid=row["id"]
        check(rid not in rows,"Duplicate requirement: "+rid);rows[rid]=row
        check(row["status"] in {"missing","partial","implemented_unverified","release_accepted"},"Invalid status: "+rid)
        check(row["priority"]=="release_required","Invalid priority: "+rid)
        check(bool(row["title"].strip()) and bool(row["current"].strip()),"Empty requirement: "+rid)
        source=row["source"]
        check(source["anchor"] in sources.get(source["id"],""),"Missing source anchor: "+rid)
        test=row["acceptance_test"]
        check(test["id"]=="AT-"+rid and test["id"] not in scenarios,"Bad acceptance ID: "+rid)
        scenarios.add(test["id"])
        check(bool(test["procedure"].strip()),"Empty acceptance: "+rid)
        check(test["status"] in {"planned","implemented","passed","failed"},"Invalid acceptance status: "+rid)
        for ref in test["existing_tests"]:
            file,_,function=ref.partition("::")
            path=local(file)
            check(bool(path and path.is_file()),"Missing existing test: "+ref)
            if path and path.is_file() and function:
                check("def "+function+"(" in path.read_text(encoding="utf-8"),"Missing test function: "+ref)
        if row["status"]=="release_accepted":
            check(test["status"]=="passed","Accepted requirement lacks passed scenario: "+rid)
            check(bool(row["release_evidence"]),"Accepted requirement lacks evidence: "+rid)
            for evidence in row["release_evidence"]:
                for field in ("artifact","environment","revision","executed_at","reviewer"):
                    check(bool(evidence.get(field)),"Missing evidence "+field+": "+rid)
                path=local(evidence.get("artifact",""))
                check(bool(path and path.is_file()),"Missing evidence artifact: "+rid)
    check(bool(rows),"Empty baseline")
    visited=set();visiting=set()
    def visit(rid):
        if rid in visiting:
            errors.append("Dependency cycle: "+rid);return
        if rid in visited:return
        visiting.add(rid)
        for dep in rows[rid]["depends_on"]:
            check(dep in rows,"Unknown dependency: "+rid+" -> "+dep)
            if dep in rows:visit(dep)
        visiting.remove(rid);visited.add(rid)
    for rid in rows:visit(rid)
    check(all("C"+str(i).zfill(2) in rows for i in range(1,13)),"Missing twelve-category requirement")
    check(all(i in rows for i in ("L01","L02","L03")),"Missing confirmed language requirements")
    decisions=data.get("decisions",[])
    check(len({d["id"] for d in decisions})==len(decisions),"Duplicate decision ID")
    check({d["id"] for d in decisions}=={"Q"+str(i).zfill(2) for i in range(1,11)},"Incomplete decision register")
    check(all(d["status"] in {"pending","confirmed"} for d in decisions),"Invalid decision status")
    if release:
        check(data.get("baseline_status")=="approved","Baseline is not approved")
        for d in decisions:check(d["status"]=="confirmed","Pending decision: "+d["id"])
        for rid,row in rows.items():check(row["status"]=="release_accepted","Not release accepted: "+rid)
    return errors

def catalogue_errors(data, text):
    errors=[]
    for row in data["requirements"]:
        prefix="| "+row["id"]+" | "+row["title"]+" | "+row["status"]+" |"
        if prefix not in text:errors.append("Catalogue mismatch: "+row["id"])
        if "### AT-"+row["id"]+":" not in text:errors.append("Missing readable scenario: "+row["id"])
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release",action="store_true")
    args=parser.parse_args()
    data=json.loads((BASE/"requirements.json").read_text(encoding="utf-8"))
    errors=validate(data,args.release)+catalogue_errors(data,(BASE/"requirements.md").read_text(encoding="utf-8"))
    if errors:
        print("RELEASE NOT CLEARED" if args.release else "BASELINE INTEGRITY FAILED")
        for error in errors:print("- "+error)
        return 1
    print("Traceability structure valid: "+str(len(data["requirements"]))+" requirements.")
    print("This does NOT establish implementation completeness or production readiness.")
    return 0

if __name__=="__main__":raise SystemExit(main())
