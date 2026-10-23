"""Construct controlled experimental case from saved live stage observations."""
import argparse,datetime,json
from pathlib import Path
try:
 from tools.prototype_contract import jlines
except ModuleNotFoundError:
 from prototype_contract import jlines

def iso(t):return t.isoformat(timespec='seconds')
def main():
 p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True)
 p.add_argument('--scenario',choices=['N01','A101','A102','A201','A202','A203','A204','A205'],default='N01')
 args=p.parse_args();run=args.run
 raw=jlines(run/'raw/inventory.jsonl');disp=jlines(run/'raw/dispositions.jsonl')
 latest=max(datetime.datetime.fromisoformat(r['event_time']) for r in raw)
 cutoff=latest+datetime.timedelta(seconds=10);audit=cutoff+datetime.timedelta(minutes=10)
 out={'source_cutoff':iso(cutoff),'audit_time':iso(audit),'release_id':'release-demo-001',
      'collector_coverage_confirmed':True, # pilot collector scope only, NOT industrial completeness
      'finding_observation_scope_confirmed':True, # pilot injected finding stream only
      'inventory':raw,'dispositions':disp,'findings':[],'scenario_id':args.scenario,
      'provenance_class':'controlled_pilot_derived_from_real_health_checks'}
 if args.scenario=='A101':out['dispositions']=[d for d in disp if d['signal_id']!='health:qa']
 if args.scenario=='A102':out['dispositions']=disp+[dict(disp[1])]
 if args.scenario in ('A201','A202','A203','A204','A205'):
  finding={'finding_id':'F-DEMO-1','observed_time':iso(cutoff+datetime.timedelta(minutes=1)),
           'source_release':'release-demo-001','requirement_id':'REQ-FIX-1',
           'target_due_time':iso(cutoff+datetime.timedelta(minutes=2)),'target_verified':False}
  if args.scenario=='A201':finding['requirement_id']=None
  if args.scenario=='A203':finding['target_due_time']=iso(cutoff+datetime.timedelta(days=1))
  if args.scenario=='A204':finding['target_verified']=True
  if args.scenario=='A205':finding['source_release']=None
  out['findings']=[finding]
 (run/'case').mkdir(exist_ok=True)
 (run/'case'/'case.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 (run/'case'/'injection_record.json').write_text(json.dumps({'scenario':args.scenario,
  'injection_location':'derived_copy_only; original raw/ files unchanged',
  'ground_truth_source':'scenario_spec NOT independent_oracle'},indent=2)+'\n')
 print('case built:',run/'case/case.json')
if __name__=='__main__':main()
