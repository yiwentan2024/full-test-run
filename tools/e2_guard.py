"""Reject historical ZHFB IDs without source-verified real evidence."""
import sys
from scenarios.build_case import SCENARIOS
sid=sys.argv[1] if len(sys.argv)>1 else ''
if sid not in SCENARIOS:
    raise SystemExit('UNKNOWN_SCENARIO:'+sid)
if SCENARIOS[sid]['source']!='CONTROLLED_PILOT':
    raise SystemExit(f'BLOCKED_REAL_DATA:{sid}: project source export + independent facts not provided')
print('CONTROLLED_PILOT_ENABLED:', sid)
