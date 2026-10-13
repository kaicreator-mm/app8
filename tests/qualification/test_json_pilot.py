"""Offline unit cases for frozen real-host pilot construction; NOT Docker evidence."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from app8.contracts import validate_contract
from scripts.v03_cpython_json_pilot import (
    BINDING, IMAGE, COMMAND, _CASES, PilotBlocked, PilotSettings,
    GOOD_SCRIPT, BAD_SCRIPT, case_request, make_capability, execute_pilot,
    source_probe_request, _strict_sha,
)


def settings(**kw):
    options=dict(docker_client=str(Path(sys.executable).resolve()),
                 docker_client_sha256="a"*64,
                 environment_id="test-env",expected_server_version="29.1.3",
                 ledger_root=Path(tempfile.gettempdir())/"not-real-ledger")
    options.update(kw)
    return PilotSettings(**options)


class FrozenPilotUnitTests(unittest.TestCase):
    def test_all_three_cases_are_fixed_only(self):
        self.assertEqual(set(_CASES), {"P01", "N01", "F01"})
        self.assertTrue(IMAGE.startswith("library/python@sha256:"))
        self.assertEqual(COMMAND, "/usr/local/bin/python")

    def test_source_inspection_request_is_pinned(self):
        r=source_probe_request(settings())
        self.assertEqual(r.image_ref, IMAGE)
        self.assertEqual(r.command, COMMAND)
        self.assertEqual(r.argv[:2],("-I","-c"))
        self.assertFalse(r.network_allowed)
        self.assertFalse(r.mutation_allowed)

    def test_case_argv_are_constant(self):
        for case in _CASES:
            r=case_request(settings(),case)
            self.assertEqual(r.argv[:2],("-I","-c"))
            self.assertEqual(r.command,COMMAND)
            self.assertFalse(r.network_allowed)
            self.assertFalse(r.mutation_allowed)

    def test_unknown_case_does_not_execute(self):
        with self.assertRaises(PilotBlocked):
            case_request(settings(),"USER_SUPPLIED_COMMAND")

    def test_run_requires_operator_reviewed_source_and_license(self):
        with self.assertRaises(PilotBlocked):
            settings().validate(execute=True)
        with self.assertRaises(PilotBlocked):
            settings(approved_source_sha256="b"*64).validate(execute=True)
        with self.assertRaises(PilotBlocked):
            settings(approved_source_sha256="b"*64,license_review_reference="PSF-3.14 license").validate(execute=True)
        self.assertTrue(_strict_sha("f"*64))

    def test_capability_structure_is_actual_frozen_schema(self):
        source={"repository":"python/cpython","revision":"python:3.14 pinned",
                "content_sha256":"d"*64}
        target={"identity":IMAGE,"package_sha256":IMAGE.rsplit(":",1)[-1],
                "environment_id":"test-linux","mapping_relation":"SAME"}
        for case in _CASES:
            cap=make_capability(source,target,case,["ev:one"])
            self.assertEqual(validate_contract("capability",cap),cap)
            self.assertFalse(cap["readiness"]["export_ready"])
            self.assertEqual(cap["bindings"][0]["binding_id"], BINDING)

    def test_native_python_json_syntax_precheck_not_docker(self):
        p=subprocess.run((sys.executable,"-I","-c",GOOD_SCRIPT),
                         capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0)
        self.assertEqual(p.stdout.strip(),'{"a":1,"b":2}')
        n=subprocess.run((sys.executable,"-I","-c",BAD_SCRIPT),
                         capture_output=True,text=True,timeout=10)
        self.assertNotEqual(n.returncode,0)
        self.assertIn("JSONDecodeError",n.stderr)

    def test_private_ledger_cannot_be_reused_silently(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private"
            (root / "evidence").mkdir(parents=True)
            (root / "evidence" / "evidence.sqlite3").write_bytes(b"prior")
            cfg = settings(ledger_root=root, approved_source_sha256="d"*64)
            with self.assertRaisesRegex(PilotBlocked, "FRESH_PRIVATE_LEDGER_REQUIRED"):
                execute_pilot(None, cfg, {"sha256":"d"*64, "path":"/test/json.py", "version":"3.14"})

    def test_false_assertion_is_deliberately_incorrect(self):
        self.assertIn("never-produced-sentinel-9fa4",_CASES["F01"][1][-1])
        self.assertEqual(_CASES["P01"][0],_CASES["F01"][0])
        self.assertNotEqual(_CASES["P01"][2],_CASES["F01"][2])


if __name__=="__main__":
    unittest.main()
