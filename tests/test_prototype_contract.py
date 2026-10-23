import datetime,unittest
from tools.prototype_contract import verify
class PrototypeContractTests(unittest.TestCase):
 def setUp(self):
  base=datetime.datetime(2026,10,1,10,0,tzinfo=datetime.timezone.utc)
  self.case={'source_cutoff':(base+datetime.timedelta(minutes=2)).isoformat(),
    'audit_time':(base+datetime.timedelta(hours=2)).isoformat(),
    'release_id':'r1','collector_coverage_confirmed':True,'finding_observation_scope_confirmed':True,
    'inventory':[{'signal_id':'a','event_time':base.isoformat()}],
    'dispositions':[{'signal_id':'a','decision_time':(base+datetime.timedelta(minutes=1)).isoformat(),'decision':'PASS'}],
    'findings':[]}
 def test_normal_closed(self):self.assertEqual('CLOSED',verify(self.case)['machine_decision'])
 def test_missing_disposition(self):
  self.case['dispositions']=[]
  self.assertEqual('OPEN',verify(self.case)['machine_decision'])
 def test_missing_link_nfi(self):
  f={'observed_time':(datetime.datetime(2026,10,1,10,5,tzinfo=datetime.timezone.utc)).isoformat(),
     'source_release':'r1','requirement_id':None,'target_due_time':self.case['audit_time'],'target_verified':False}
  self.case['findings']=[f]
  self.assertEqual('NFI',verify(self.case)['evidence_status'])
 def test_pending_target(self):
  f={'observed_time':'2026-10-01T10:05:00+00:00','source_release':'r1','requirement_id':'REQ1',
   'target_due_time':'2026-10-02T10:05:00+00:00','target_verified':False}
  self.case['findings']=[f]
  self.assertEqual('PENDING',verify(self.case)['evidence_status'])
if __name__=='__main__':unittest.main()
