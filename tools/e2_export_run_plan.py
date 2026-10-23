import csv,json
from pathlib import Path
from scenarios.build_case import MANIFEST
root=Path(__file__).resolve().parents[1]
out=root/'protocols/E2_48_Controlled_Run_Plan.csv'
with out.open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f)
    w.writerow(['scenario_id','variant','replicate_index','planned_source','github_run_id','observed_baseline','observed_B2','oracle_ref','archive_sha256','status'])
    for item in MANIFEST['scenarios']:
        if item['source']!='CONTROLLED_PILOT':continue
        for variant in ('B0','B1','B2'):
            w.writerow([item['id'],variant,1,'CONTROLLED_PILOT','','','','','','NOT_RUN'])
print(out,'48 run rows')
