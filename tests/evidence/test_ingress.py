import tempfile,unittest
from pathlib import Path
from app8.evidence.attestation import AttestationGate,AttestationError
from app8.evidence.ingress import import_signed_observation
from test_attestation import KEY,evidence,sign

class FakeStore:
    def __init__(self):self.items=[];self.events=[]
    def validator(self,kind,evidence):
        assert kind=='evidence'
        if evidence.get('invalid'):raise ValueError('invalid schema')
    def append_evidence(self,doc):
        self.items.append(doc.copy());return 'a'*64
    def append_event(self,subject,kind,body):
        self.events.append((subject,kind,body));return len(self.events)

class ImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.g=AttestationGate(verification_key=KEY,runner_id='fixture-runner',policy_sha256='a'*64,
                               image_sha256='b'*64,nonce_db=Path(self.tmp.name)/'n.db')
        self.addCleanup(self.g.close)
        self.store=FakeStore()
    def test_valid_receipt_stores_but_never_auto_exports(self):
        ev=evidence();r=sign(ev)
        x=import_signed_observation(self.store,self.g,ev,r)
        self.assertFalse(x.capability_export_ready)
        self.assertEqual(x.status,'AUTHENTICATED_OBSERVATION_NOT_RELEASE_QUALIFIED')
        self.assertEqual(len(self.store.items),1)
        self.assertEqual(self.store.events[0][1],'RUNNER_RECEIPT_AUTHENTICATED')
        self.assertTrue(self.g.is_accepted(ev,r))
    def test_unsigned_not_saved(self):
        with self.assertRaises(AttestationError):import_signed_observation(self.store,self.g,evidence(),{})
        self.assertFalse(self.store.items)
    def test_invalid_schema_not_saved_or_nonce_consumed(self):
        ev=evidence();ev['invalid']=True;r=sign(ev)
        with self.assertRaises(ValueError):import_signed_observation(self.store,self.g,ev,r)
        self.assertFalse(self.store.items)
        self.assertFalse(self.g.is_accepted(ev,r))
    def test_model_assessor_rejected(self):
        ev=evidence();ev['assessment']['assessor_kind']='MODEL_PROPOSAL_ONLY'
        with self.assertRaises(AttestationError):import_signed_observation(self.store,self.g,ev,sign(ev))
        self.assertFalse(self.store.items)
    def test_replayed_signed_evidence_cannot_duplicate(self):
        ev=evidence();r=sign(ev);import_signed_observation(self.store,self.g,ev,r)
        with self.assertRaises(AttestationError):import_signed_observation(self.store,self.g,ev,r)
        self.assertEqual(len(self.store.items),1)
if __name__=='__main__':unittest.main()
