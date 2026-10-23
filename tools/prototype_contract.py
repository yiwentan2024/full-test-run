"""Illustrative, limited A1/A2 pilot adapter, NOT the paper's frozen verifier.

The code implements six illustrative behavior checks for developer onboarding.
Do not report this prototype as Algorithm 1 conformance or independent oracle.
"""
import datetime, hashlib, json
from pathlib import Path

def jlines(p):
 p=Path(p)
 if not p.exists():raise FileNotFoundError(p)
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def digest(b):return hashlib.sha256(b).hexdigest()

def verify(case):
    cutoff=dt(case['source_cutoff']);audit_at=dt(case['audit_time'])
    raw=case['inventory'];disp=case['dispositions'];fails=[];annotations=[]
    if not case.get('collector_coverage_confirmed',False):
        annotations.append({'state':'NFI','code':'UNVERIFIED_SIGNAL_SCOPE'});
        fails.append('UNVERIFIED_SIGNAL_SCOPE')
    ids=[r['signal_id'] for r in raw]
    if len(set(ids))!=len(ids):fails.append('DUPLICATE_RAW_IDENTITY')
    for sid in ids:
        ds=[d for d in disp if d['signal_id']==sid and dt(d['decision_time'])<=cutoff]
        if len(ds)!=1:
            fails.append('MISSING_OR_DUPLICATE_DISPOSITION:'+sid)
        elif ds[0]['decision'] not in ('PASS','AUTHORIZED_EXCLUDED'):
            fails.append('NONADMISSIBLE_DISPOSITION:'+sid)
    for d in disp:
        if d['signal_id'] not in ids:fails.append('UNKNOWN_DISPOSITION_ID:'+d['signal_id'])
    for r in raw:
        if dt(r['event_time'])>cutoff:fails.append('POST_CUTOFF_RAW_EVENT:'+r['signal_id'])
    historical_closed=(len(fails)==0)
    obligations=[]
    for f in case.get('findings',[]):
        if dt(f['observed_time'])>audit_at:continue
        if f.get('source_release')!=case.get('release_id'):
            obligations.append({'state':'NFI','code':'UNRESOLVED_SOURCE_ATTRIBUTION'});continue
        if not f.get('requirement_id'):
            obligations.append({'state':'NFI','code':'MISSING_FINDING_REQUIREMENT_LINK'});continue
        if dt(f['target_due_time'])>audit_at:
            obligations.append({'state':'PENDING','code':'TARGET_NOT_DUE'});continue
        if f.get('target_verified') is not True:
            obligations.append({'state':'OPEN','code':'TARGET_VALIDATION_INCOMPLETE'});continue
        obligations.append({'state':'CLOSED','code':'TARGET_VALIDATED'})
    if not case.get('finding_observation_scope_confirmed',False):
        obligations.append({'state':'NFI','code':'FINDING_SCOPE_NOT_ATTESTED'})
    if not obligations: evidence_status='NOT_APPLICABLE'
    else:
        for s in ('NFI','OPEN','PENDING'):
            if any(o['state']==s for o in obligations): evidence_status=s;break
        else:evidence_status='CLOSED'
    audit_closed=historical_closed and evidence_status in ('NOT_APPLICABLE','CLOSED')
    reasons=fails+[o['code'] for o in obligations if o['state']!='CLOSED']
    return {'prototype_only':True,'historical_closed_as_of':historical_closed,
            'audit_closed_as_of':audit_closed,'machine_decision':'CLOSED' if audit_closed else 'OPEN',
            'evidence_status':evidence_status,'failure_codes':reasons,
            'obligations':obligations,'source_cutoff':case['source_cutoff'],'audit_time':case['audit_time']}
