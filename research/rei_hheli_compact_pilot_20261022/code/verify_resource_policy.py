#!/usr/bin/env python3
"""Focused deterministic admission tests; no numerical model execution."""
import json
from run_pilot import ROOT,cpu_admission,worker_admission

def main():
    rows=[]
    def check(name,quota,peers,used,idle,busy,expected,load=100.):
        measured={'cgroup_used_cpu':used,'affinity_idle_cpu':idle,'affinity_busy_cpu':busy,'load_1m':load}
        result=cpu_admission(quota,peers,measured)
        assert result['cpu_slots']==expected,(name,result)
        rows.append({'name':name,'quota':quota,'peers':peers,'measurement':measured,'result':result})
    check('high_host_load_low_actual_use',8,0,.1,8.5,.5,6)
    check('full_actual_quota_use',8,0,8,3,6,0)
    check('full_actual_affinity_use',8,0,.1,0,9,0)
    check('fractional_quota_enforced',2.5,0,.2,8.5,.5,1)
    check('observed_peer_busy_not_double_counted',8,4,4,5,4,3)
    check('unrealized_peer_reservation_retained',8,4,.1,8.5,.5,3)
    check('known_busy_prevents_missing_measurement_fallback',8,0,8,None,None,0)
    check('missing_measurement_fallback_one_only',8,0,None,None,None,1)
    cases=[('memory_zero',63,None,4,6,0,0),('memory_cap',63,None,4,6,2,2),
           ('sandbox_cap',63,None,4,7,10,4),('ncp_request_cap',63,63,63,63,200,63)]
    for name,desired,cap,default,cpu,memory,expected in cases:
        actual=worker_admission(desired,cap,default,cpu,memory)
        assert actual==expected,(name,actual)
        rows.append({'name':name,'actual_workers':actual,'expected_workers':expected})
    result={'status':'PASS','tests':rows,'load_average':'diagnostic only; no admission dependence'}
    (ROOT/'evidence/RESOURCE_POLICY_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
