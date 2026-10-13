import hashlib
import os
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
from app8.execution import Invocation, run_invocation


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        exe=Path(sys.executable).resolve()
        self.req=Invocation(str(exe), ("-I", "-c", "print('observed')"),
                            hashlib.sha256(exe.read_bytes()).hexdigest(), self.tmp.name,
                            network_allowed=True, mutation_allowed=True)

    def test_actual_bounded_process(self):
        o=run_invocation(self.req)
        self.assertEqual(o.status,"EXECUTED")
        self.assertEqual(o.exit_code,0)
        self.assertEqual(o.stdout_sha256,hashlib.sha256(("observed" + os.linesep).encode("utf-8")).hexdigest())
        self.assertEqual(o.reason,"OBSERVATION_ONLY_NOT_EVIDENCE")

    def test_default_isolation_fail_closed(self):
        o=run_invocation(replace(self.req,network_allowed=False,mutation_allowed=False))
        self.assertEqual((o.status,o.reason),("BLOCKED","NETWORK_ISOLATION_NOT_VERIFIED"))

    def test_mutation_isolation_fail_closed(self):
        o=run_invocation(replace(self.req,mutation_allowed=False))
        self.assertEqual(o.reason,"FILESYSTEM_ISOLATION_NOT_VERIFIED")

    def test_wrong_executable_hash_blocks(self):
        o=run_invocation(replace(self.req,expected_executable_sha256="f"*64))
        self.assertEqual(o.reason,"EXECUTABLE_HASH_MISMATCH")

    def test_missing_executable_blocks(self):
        o=run_invocation(replace(self.req,executable="/absent/executable"))
        self.assertEqual(o.status,"BLOCKED")

    def test_no_relative_binary(self):
        o=run_invocation(replace(self.req,executable="python"))
        self.assertEqual(o.reason,"INVALID_TARGET_EXECUTABLE")

    def test_output_limit_blocks(self):
        o=run_invocation(replace(self.req,max_output_bytes=3))
        self.assertEqual(o.reason,"OUTPUT_BUDGET_EXCEEDED")
        self.assertTrue(o.output_truncated)

    def test_timeout_blocks(self):
        o=run_invocation(replace(self.req,argv=("-I","-c","import time; time.sleep(2)"),timeout_seconds=1))
        self.assertEqual(o.reason,"TIMEOUT")

    def test_nonzero_exit_is_observation_not_pass(self):
        o=run_invocation(replace(self.req,argv=("-I","-c","raise SystemExit(4)")))
        self.assertEqual(o.status,"EXECUTED")
        self.assertEqual(o.exit_code,4)

    def test_invalid_budget(self):
        self.assertEqual(run_invocation(replace(self.req,timeout_seconds=True)).reason,"BAD_TIME_BUDGET")

if __name__=="__main__":unittest.main()
