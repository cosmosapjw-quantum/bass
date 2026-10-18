"""Matched-error Python source-only timing; no native/HHe speed claim."""
import argparse,json,statistics,time
from pathlib import Path
from source_oracle import Case
from deposition import midpoint_cases,gauss2_cases,simulate,continuum_reference
from generate_fixtures import original_geometry

def run(out):
    if Path(out).exists():raise FileExistsError(out)
    g,_=original_geometry('COLD');b,H,s=g(.2)
    c=Case('BENCH',.2,b,H,s,1.,nmu=8,nseg=8,nenergy=64,qmin=1.,qmax=512.)
    ref=continuum_reference(c,g,.2,.8)
    rows=[]
    for name,rule,panels in [('midpoint',midpoint_cases,1024),('positive_gl2',gauss2_cases,16)]:
        def evaluate():
            births=rule(c,g,.2,.8,panels)
            return simulate(births,.8,g(.8)[0]),len(births)
        result,count=evaluate();times=[]
        for _ in range(3):
            t=time.perf_counter();result,count=evaluate();times.append(time.perf_counter()-t)
        err=abs(result['inventory_u']/ref['inventory_u']-1)
        if err>1e-6:raise AssertionError('MATCHED_ACCURACY_GATE')
        rows.append({'method':name,'panels':panels,'birth_impulses':count,'median_seconds':statistics.median(times),
                     'wall_seconds':times,'relative_U_error':err,'acceptance_target':1e-6})
    record={'schema':'bass.sourceledger.python.time_benchmark.v1','scope':'Python source-only integration, includes birth generation and deposits, warmed caches; excludes compile/HHe/I/O; no native speed claim',
            'geometry':'original BASS COLD','interval_x':[.2,.8],'cases':rows,
            'median_speedup':rows[0]['median_seconds']/rows[1]['median_seconds']}
    Path(out).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
