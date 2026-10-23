import argparse,json
from pathlib import Path
try:from tools.prototype_contract import verify
except ModuleNotFoundError:from prototype_contract import verify

def main():
 p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);args=p.parse_args()
 case=json.loads((args.run/'case/case.json').read_text())
 result=verify(case);(args.run/'results').mkdir(exist_ok=True)
 (args.run/'results/b2_prototype.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2))
 return 0 if result['machine_decision']=='CLOSED' else 2
if __name__=='__main__':raise SystemExit(main())
