import copy
import hashlib
import hmac
import json
import tempfile
import unittest
from pathlib import Path

from app8.evidence import ReceiptError, ReceiptVerifier

A = "a" * 64
B = "b" * 64
C = "c" * 64
D = "d" * 64
POL = "e" * 64
KEY = b"k" * 32


def make_receipt():
    return {"schema_version": "app8-observation-receipt-v1", "nonce": "0" * 32,
            "runner_id": "runner-test", "sandbox_policy_sha256": POL,
            "plan_sha256": A, "source_sha256": B, "target_sha256": C,
            "image_sha256": D, "stdout_sha256": "f" * 64,
            "stderr_sha256": "0" * 64, "exit_code": 0, "execution_status": "EXECUTED"}


def sign(doc, key=KEY):
    msg=(json.dumps(doc,sort_keys=True,separators=(",", ":"),ensure_ascii=False,allow_nan=False)+"\n").encode()
    return {"receipt": copy.deepcopy(doc), "mac_sha256": hmac.new(key,msg,hashlib.sha256).hexdigest()}


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"nonces.sqlite3"
        self.v=ReceiptVerifier(secret=KEY, runner_id="runner-test",policy_sha256=POL,nonce_db=self.db)
        self.addCleanup(self.v.close)
        self.kw={"expected_plan_sha256":A,"expected_source_sha256":B,
                 "expected_target_sha256":C,"expected_image_sha256":D}

    def test_valid_receipt_is_not_trusted_behavioral_truth(self):
        outcome=self.v.verify(sign(make_receipt()),**self.kw)
        self.assertEqual(outcome.status,"RUNNER_RECEIPT_AUTHENTICATED_NOT_BEHAVIORAL_TRUTH")
        self.assertFalse(outcome.host_sandbox_verified)
        self.assertFalse(outcome.capability_export_ready)

    def test_invalid_mac_blocks(self):
        with self.assertRaises(ReceiptError):self.v.verify(sign(make_receipt(),b"x"*32),**self.kw)

    def test_tampered_stdout_blocks(self):
        signed=sign(make_receipt()); signed["receipt"]["stdout_sha256"]="1"*64
        with self.assertRaises(ReceiptError):self.v.verify(signed,**self.kw)

    def test_wrong_target_blocks(self):
        with self.assertRaises(ReceiptError):self.v.verify(sign(make_receipt()),**dict(self.kw,expected_target_sha256="1"*64))

    def test_wrong_image_blocks(self):
        with self.assertRaises(ReceiptError):self.v.verify(sign(make_receipt()),**dict(self.kw,expected_image_sha256="1"*64))

    def test_wrong_plan_blocks(self):
        with self.assertRaises(ReceiptError):self.v.verify(sign(make_receipt()),**dict(self.kw,expected_plan_sha256="1"*64))

    def test_wrong_source_blocks(self):
        with self.assertRaises(ReceiptError):self.v.verify(sign(make_receipt()),**dict(self.kw,expected_source_sha256="1"*64))

    def test_invalid_runner_id_blocks(self):
        doc=make_receipt();doc["runner_id"]="another"
        with self.assertRaises(ReceiptError):self.v.verify(sign(doc),**self.kw)

    def test_nonexecuted_is_not_valid(self):
        doc=make_receipt();doc["execution_status"]="NOT_RUN"
        with self.assertRaises(ReceiptError):self.v.verify(sign(doc),**self.kw)

    def test_replay_blocks_across_restart(self):
        signed=sign(make_receipt());self.v.verify(signed,**self.kw)
        with ReceiptVerifier(secret=KEY,runner_id="runner-test",policy_sha256=POL,nonce_db=self.db) as v2:
            with self.assertRaises(ReceiptError):v2.verify(signed,**self.kw)

    def test_forbidden_extra_fields(self):
        doc=make_receipt();doc["ground_truth"]="true"
        with self.assertRaises(ReceiptError):self.v.verify(sign(doc),**self.kw)

    def test_short_key_denied(self):
        with self.assertRaises(ReceiptError):ReceiptVerifier(secret=b"pass",runner_id="runner-test",policy_sha256=POL,nonce_db=self.db)


if __name__=="__main__":unittest.main()
