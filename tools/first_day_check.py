"""One command for new experiment engineers: tests, build, 3 training scenarios."""
import datetime,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STEPS=[('Unit tests',[sys.executable,'-m','unittest','discover','-s','tests','-v']),
 ('Build artifact',[sys.executable,'tools/build.py']),
 ('N01 normal',[sys.executable,'tools/run_local.py','--scenario','N01']),
 ('A101 A1 missing disposition',[sys.executable,'tools/run_local.py','--scenario','A101']),
 ('A201 A2 missing lineage',[sys.executable,'tools/run_local.py','--scenario','A201'])]
report={'scope':'LOCAL_TRAINING_ONLY; NOT_FORMAL_PAPER_RESULTS',
 'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'steps':[]}
for label,cmd in STEPS:
 print('\n'+'='*50+'\n'+label+'\n'+' '.join(cmd),flush=True)
 proc=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 print(proc.stdout,flush=True)
 report['steps'].append({'label':label,'command':cmd,'exit_code':proc.returncode})
 if proc.returncode!=0:break
report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
report['all_passed']=len(report['steps'])==len(STEPS) and all(s['exit_code']==0 for s in report['steps'])
(ROOT/'runs').mkdir(exist_ok=True)
(ROOT/'runs/first_day_report.json').write_text(json.dumps(report,indent=2)+'\n')
print('D1 CHECK:', 'SUCCESS' if report['all_passed'] else 'FAILED', '| report:',ROOT/'runs/first_day_report.json')
raise SystemExit(0 if report['all_passed'] else 1)
