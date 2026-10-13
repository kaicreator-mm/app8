import unittest,tempfile
from pathlib import Path
from app8.evidence.attestation import AttestationGate
from app8.readiness import evaluate_readiness
from test_attestation import KEY,evidence,sign

class BindingTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.g=AttestationGate(verification_key=KEY,runner_id='fixture-runner',
                               policy_sha256='a'*64,image_sha256='b'*64,nonce_db=Path(self.t.name)/'n.db')
        self.addCleanup(self.g.close)
        self.ev=evidence()
        self.ev['source'].update(repository='fixture',revision='pin')
        self.ev['target'].update(identity='p',mapping_relation='SAME')
        self.ev['plan']['binding_id']='b'
        self.ev['assessment']['reason_codes']=['ASSERTIONS_PASSED']
        self.cap={'capability_id':'cap:example','source':self.ev['source'],'target':self.ev['target'],
                  'bindings':[{'binding_id':'b'}],'evidence_refs':['ev:1'],'readiness':{'export_ready':True}}
    def check(self,**kwargs):
        return evaluate_readiness(self.cap,[self.ev],projection_verifier=lambda _:True,**kwargs)
    def test_bare_json_never_exports(self):
        self.assertFalse(self.check().export_ready)
    def test_unauthenticated_signed_payload_never_exports(self):
        self.assertFalse(self.check(attestation_gate=self.g,signed_attestations={'ev:1':sign(self.ev)}).export_ready)
    def test_authenticated_but_no_projection(self):
        a=sign(self.ev);self.g.accept(self.ev,a)
        x=evaluate_readiness(self.cap,[self.ev],attestation_gate=self.g,signed_attestations={'ev:1':a})
        self.assertEqual(x.lifecycle_state,'EVIDENCED')
        self.assertFalse(x.export_ready)
    def test_signed_fixture_only_shows_policy_path(self):
        a=sign(self.ev);self.g.accept(self.ev,a)
        self.assertTrue(self.check(attestation_gate=self.g,signed_attestations={'ev:1':a}).export_ready)
    def test_tampered_after_ingestion_does_not_export(self):
        a=sign(self.ev);self.g.accept(self.ev,a)
        self.ev['observation']['stdout_sha256']='1'*64
        self.assertFalse(self.check(attestation_gate=self.g,signed_attestations={'ev:1':a}).export_ready)
    def test_negative_event_blocks_attested_positive(self):
        a=sign(self.ev);self.g.accept(self.ev,a)
        r=evaluate_readiness(self.cap,[self.ev],[{'kind':'REFUTED'}],projection_verifier=lambda _:True,
                             attestation_gate=self.g,signed_attestations={'ev:1':a})
        self.assertFalse(r.export_ready)
    def test_model_assessor_blocked_even_with_signature(self):
        self.ev['assessment']['assessor_kind']='MODEL_PROPOSAL_ONLY'
        self.assertFalse(self.check().export_ready)
if __name__=='__main__':unittest.main()
