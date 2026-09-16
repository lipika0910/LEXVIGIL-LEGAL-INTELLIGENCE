import json
import unittest
from validate_phase1 import BASE, validate, catalogue_errors

class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((BASE/"requirements.json").read_text(encoding="utf-8"))

    def test_valid_baseline(self):
        self.assertEqual(validate(self.data),[])

    def test_release_is_not_cleared(self):
        errors=validate(self.data,release=True)
        self.assertIn("Baseline is not approved",errors)
        self.assertTrue(any("Not release accepted" in e for e in errors))

    def test_unknown_dependency(self):
        self.data["requirements"][0]["depends_on"]=["UNKNOWN"]
        self.assertTrue(any("Unknown dependency" in e for e in validate(self.data)))

    def test_cycle(self):
        self.data["requirements"][0]["depends_on"]=["P02"]
        self.data["requirements"][1]["depends_on"]=["P01"]
        self.assertTrue(any("Dependency cycle" in e for e in validate(self.data)))

    def test_false_acceptance(self):
        self.data["requirements"][0]["status"]="release_accepted"
        self.assertTrue(any("lacks evidence" in e for e in validate(self.data)))

    def test_source_drift(self):
        self.data["sources"][0]["sha256"]="0"*64
        self.assertTrue(any("fingerprint changed" in e for e in validate(self.data)))

    def test_catalogue(self):
        text=(BASE/"requirements.md").read_text(encoding="utf-8")
        self.assertEqual(catalogue_errors(self.data,text),[])

if __name__=="__main__":unittest.main()
