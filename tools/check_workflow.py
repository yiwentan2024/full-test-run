"""Static assertions for tutorial topology. Does NOT substitute GitHub execution."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]
for f in ('b0.yml','b1.yml','b2.yml'):
 path=r/'.github/workflows'/f
 assert path.exists(),path
 data=path.read_text()
 assert 'workflow_dispatch:' in data,(f,'missing manual trigger')
 assert 'actions/checkout@' in data,(f,'missing checkout')
 print('workflow skeleton OK:',f)
