import hashlib, hmac, json, tempfile, unittest
from pathlib import Path
from app8.evidence.attestation import AttestationGate, AttestationError
KEY=b'a-trusted-test-key-not-for-production-1234'
Z='0'*64

def canonical(obj):
    return (json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()

def evidence():
    return {'evidence_id':'ev:1','source':{'content_sha256':Z},
            'target':{'package_sha256':Z,'environment_id':'host'},
            'plan':{'plan_sha256':Z,'assertions':['ok']},
            'observation':{'execution_status':'EXECUTED','observer':'DETERMINISTIC_EXECUTION_ADAPTER',
                           'stdout_sha256':Z,'stderr_sha256':Z,'exit_code':0},
            'assessment':{'assessor_kind':'DETERMINISTIC_ASSERTION_ENGINE','verdict':'SUPPORTED'}}

def sign(ev,nonce='0'*32):
    r={'schema_version':'app8-attested-evidence-v2','evidence_sha256':hashlib.sha256(canonical(ev)).hexdigest(),
       'runner_id':'fixture-runner','policy_sha256':'a'*64,'image_sha256':'b'*64,'nonce':nonce}
    r['mac_sha256']=hmac.new(KEY,canonical(r),hashlib.sha256).hexdigest()
    return r

class AttestationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'nonce.sqlite3'
        self.gate=AttestationGate(verification_key=KEY,runner_id='fixture-runner',
                                  policy_sha256='a'*64,image_sha256='b'*64,nonce_db=self.db)
        self.addCleanup(self.gate.close)
    def test_accepted_only_after_persistent_ingestion(self):
        ev=evidence();r=sign(ev)
        self.assertFalse(self.gate.is_accepted(ev,r))
        self.gate.accept(ev,r)
        self.assertTrue(self.gate.is_accepted(ev,r))
    def test_payload_change_rejected(self):
        ev=evidence();r=sign(ev);self.gate.accept(ev,r)
        ev['target']['environment_id']='different-host'
        self.assertFalse(self.gate.is_accepted(ev,r))
    def test_forged_mac(self):
        ev=evidence();r=sign(ev);r['mac_sha256']='f'*64
        with self.assertRaises(AttestationError):self.gate.accept(ev,r)
    def test_replay(self):
        ev=evidence();r=sign(ev);self.gate.accept(ev,r)
        with self.assertRaises(AttestationError):self.gate.accept(ev,r)
    def test_wrong_image(self):
        ev=evidence();r=sign(ev);r['image_sha256']='c'*64
        self.assertFalse(self.gate.is_accepted(ev,r))
    def test_wrong_runner(self):
        ev=evidence();r=sign(ev);r['runner_id']='other'
        self.assertFalse(self.gate.is_accepted(ev,r))
    def test_block_nonexecuted(self):
        ev=evidence();ev['observation']['execution_status']='NOT_RUN'
        with self.assertRaises(AttestationError):self.gate.accept(ev,sign(ev))
    def test_block_model(self):
        ev=evidence();ev['assessment']['assessor_kind']='MODEL_PROPOSAL_ONLY'
        with self.assertRaises(AttestationError):self.gate.accept(ev,sign(ev))
    def test_reopen_store(self):
        ev=evidence();r=sign(ev);self.gate.accept(ev,r)
        with AttestationGate(verification_key=KEY,runner_id='fixture-runner',
                             policy_sha256='a'*64,image_sha256='b'*64,nonce_db=self.db) as gate:
            self.assertTrue(gate.is_accepted(ev,r))
    def test_unsupported_v1(self):
        ev=evidence();r=sign(ev);r['schema_version']='app8-observation-receipt-v1'
        self.assertFalse(self.gate.is_accepted(ev,r))
    def test_no_key(self):
        with self.assertRaises(AttestationError):
            AttestationGate(verification_key=b'123',runner_id='x',policy_sha256='a'*64,
                            image_sha256='b'*64,nonce_db=self.db)

if __name__=='__main__':unittest.main()
