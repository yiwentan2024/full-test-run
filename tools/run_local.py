"""One-command local training: actual HTTP probes + controlled pilot verifier."""
import argparse,datetime,hashlib,json,os,signal,socket,subprocess,sys,time,uuid
from pathlib import Path
try:
 from tools.check_stages import collect
 from tools.prepare_case import iso
 from tools.prototype_contract import verify,jlines
except ModuleNotFoundError:
 from check_stages import collect
 from prepare_case import iso
 from prototype_contract import verify,jlines

root=Path(__file__).resolve().parents[1]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def port():
 s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--scenario',choices=['N01','B01','A101','A102','A201','A202','A203','A204','A205'],default='N01')
 parser.add_argument('--out',type=Path,default=None);a=parser.parse_args()
 runid=f'LOCAL-{a.scenario}-{datetime.datetime.now(datetime.timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:5]}'
 out=a.out or (root/'runs'/runid);out.mkdir(parents=True,exist_ok=True)
 start=time.perf_counter();procs=[];logs=[]
 ports=[port() for _ in range(3)]
 preflight={'run_id':runid,'utc_start':now(),'scenario':a.scenario,'environment':'LOCAL_TRAINING_NOT_GITHUB_ACTIONS',
            'python':sys.version,'b1_provenance':'NOT_RUN; requires real GitHub attest action'}
 (out/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
 try:
  for stage,p in zip(('dev','qa','staging'),ports):
   env=dict(os.environ,STAGE_NAME=stage,FAIL_HEALTH='1' if a.scenario=='B01' and stage=='qa' else '0')
   (out/'raw').mkdir(exist_ok=True)
   log=open(out/'raw'/f'{stage}_server.log','wb');logs.append(log)
   proc=subprocess.Popen([sys.executable,'-m','app','--port',str(p)],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
   procs.append(proc)
  ok=collect(list(zip(('dev','qa','staging'),ports)),out)
  raw=jlines(out/'raw/inventory.jsonl');disp=jlines(out/'raw/dispositions.jsonl')
  cutoff=max(datetime.datetime.fromisoformat(r['event_time']) for r in raw)+datetime.timedelta(seconds=10)
  audit=cutoff+datetime.timedelta(minutes=10)
  case={'source_cutoff':iso(cutoff),'audit_time':iso(audit),'release_id':'release-demo-001',
        'collector_coverage_confirmed':True,'finding_observation_scope_confirmed':True,
        'inventory':raw,'dispositions':disp,'findings':[],'scenario_id':a.scenario,
        'provenance_class':'CONTROLLED_LOCAL_TRAINING'}
  if a.scenario=='A101':case['dispositions']=[d for d in disp if d['signal_id']!='health:qa']
  if a.scenario=='A102':case['dispositions']=disp+[dict(disp[1])]
  if a.scenario in ('A201','A202','A203','A204','A205'):
   f={'finding_id':'F-DEMO-1','observed_time':iso(cutoff+datetime.timedelta(minutes=1)),
      'source_release':'release-demo-001','requirement_id':'REQ-FIX-1',
      'target_due_time':iso(cutoff+datetime.timedelta(minutes=2)),'target_verified':False}
   if a.scenario=='A201':f['requirement_id']=None
   if a.scenario=='A203':f['target_due_time']=iso(cutoff+datetime.timedelta(days=1))
   if a.scenario=='A204':f['target_verified']=True
   if a.scenario=='A205':f['source_release']=None
   case['findings']=[f]
  (out/'case').mkdir(exist_ok=True);(out/'results').mkdir(exist_ok=True)
  (out/'case/case.json').write_text(json.dumps(case,indent=2)+'\n')
  b0={'variant':'B0_LOCAL_TRAINING','gate':'PASS' if ok else 'FAIL',
      'b1':'NOT_RUN','protocol_note':'Real HTTP requests; no GitHub attestation or enterprise deployments'}
  (out/'results/b0.json').write_text(json.dumps(b0,indent=2)+'\n')
  b2=verify(case)
  (out/'results/b2_prototype.json').write_text(json.dumps(b2,indent=2)+'\n')
  (out/'metrics').mkdir(exist_ok=True)
  (out/'metrics/timing.json').write_text(json.dumps({'wall_clock_ms':round((time.perf_counter()-start)*1000,3)},indent=2)+'\n')
  print(json.dumps({'run_dir':str(out),'scenario':a.scenario,'B0':b0['gate'],
    'B1':'NOT_RUN','B2_PROTOTYPE':b2['machine_decision'],'evidence_status':b2['evidence_status']},indent=2))
  return 0 # didactic runner always returns 0; statuses are in machine-readable outputs
 finally:
  for proc in procs:
   if proc.poll() is None:
    proc.terminate()
    try:proc.wait(timeout=3)
    except subprocess.TimeoutExpired:proc.kill();proc.wait()
  for log in logs:log.close()
  files=[p for p in out.rglob('*') if p.is_file() and p.name!='manifest.json']
  manifest={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
  (out/'manifest.json').write_text(json.dumps({'files':manifest,'created_at':now()},indent=2)+'\n')
if __name__=='__main__':raise SystemExit(main())
