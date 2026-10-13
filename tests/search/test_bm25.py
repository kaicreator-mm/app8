import unittest
from app8.readiness import Readiness
from app8.search import CapabilityIndex
from app8.search.bm25 import tokenize


def item(cid,words,ready=False,revision=1):
    c={"capability_id":cid, "revision":revision,
       "semantic":{"name":words,"purpose":words,"user_job":words,"variants":[],"constraints":[],"negative_boundaries":[],"failure_modes":[]},
       "source":{"revision":"frozen-source"},"target":{"identity":"release-1"}}
    r=Readiness("EXPORT_READY" if ready else "HYPOTHESIZED",ready,(),())
    c["readiness"]={"export_ready":True}  # untrusted model field must not affect results
    return c,r


class SearchTests(unittest.TestCase):
    def test_nfkc_tokenization_reused(self):
        self.assertEqual(tokenize("ＣＳＶ parser, X9!"),["csv","parser","x9"])

    def test_matches_semantic_job(self):
        q=CapabilityIndex([item("cap:one","parse csv"),item("cap:two","convert video")])
        self.assertEqual(q.search("csv")[0].capability_id,"cap:one")

    def test_negative_boundary_search(self):
        c,r=item("cap:one","data")
        c["semantic"]["negative_boundaries"]=["missing input"]
        self.assertEqual(CapabilityIndex([(c,r)]).search("missing")[0].capability_id,"cap:one")

    def test_unready_not_promoted_by_input(self):
        index=CapabilityIndex([item("cap:one","csv",ready=False)])
        self.assertFalse(index.search("csv")[0].export_ready)
        self.assertEqual(index.search("csv",only_export_ready=True),[])

    def test_currentness_attached(self):
        r=CapabilityIndex([item("cap:one","csv",ready=True)]).search("csv")[0]
        self.assertEqual((r.source_revision,r.target_identity),("frozen-source","release-1"))
        self.assertTrue(r.export_ready)

    def test_duplicate_revision_refused(self):
        with self.assertRaises(ValueError):CapabilityIndex([item("cap:one","a"),item("cap:one","b")])

    def test_ranking_tie_stable(self):
        a=CapabilityIndex([item("cap:zulu","same"),item("cap:alpha","same")])
        self.assertEqual([x.capability_id for x in a.search("same")],["cap:alpha","cap:zulu"])

    def test_empty_and_unknown(self):
        index=CapabilityIndex([item("cap:one","csv")])
        self.assertEqual(index.search(""),[])
        self.assertEqual(index.search("impossible"),[])

    def test_invalid_top_k(self):
        with self.assertRaises(ValueError):CapabilityIndex([]).search("text",top_k=0)
        with self.assertRaises(ValueError):CapabilityIndex([]).search("text",top_k=True)

if __name__=="__main__":unittest.main()
