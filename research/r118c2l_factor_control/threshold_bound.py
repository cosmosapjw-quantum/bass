"""Re-merge actual terminal packet groups; one-step collisionless FLRW bound, not a trajectory estimate."""
import json, math, sys
from pathlib import Path
import numpy as np
root=Path(sys.argv[1]);edges=np.array([13.60,24.59,54.42]);rows=[]
for name in ('spec2','spec4','guard10'):
    p=np.genfromtxt(root/name/'packets.tsv',names=True,delimiter='\t');E=p['energy_eV'];w=p['N_per_H'];reg=np.searchsorted(edges,E,side='right')-1;bins=np.floor(np.log(E/edges[reg])/.04).astype(int);groups={}
    for i,key in enumerate(zip(p['ray'].astype(int),reg,bins)):
        if w[i]>0:groups.setdefault(key,[]).append(i)
    tested=0;max_delta=0.;max_ratio=0.;sumgap=0.;sumN=0.;max_conservation=0.
    for indices in groups.values():
        if len(indices)<=2:continue
        x=E[indices].astype(np.longdouble);q=w[indices].astype(np.longdouble);a=x.min();b=x.max();N=q.sum()
        if a==b:continue
        A=(q*(b-x)/(b-a)).sum();B=(q*(x-a)/(b-a)).sum();ng=abs(A+B-N)/N;ug=abs(A*a+B*b-q@x)/(q@x)
        gap=(q@np.log(x)-A*np.log(a)-B*np.log(b))/N;bound=(b-a)**2/(8*a*a)
        assert -1e-15<=gap<=bound+1e-15 and max(ng,ug)<3e-14
        tested+=1;max_delta=max(max_delta,float(gap));max_ratio=max(max_ratio,float(gap/bound));max_conservation=max(max_conservation,float(max(ng,ug)));sumgap+=float(N*gap);sumN+=float(N)
    rows.append(dict(case=name,groups=len(groups),nontrivial_groups=tested,max_mean_advance_dln_a=max_delta,max_ratio_to_bound=max_ratio,mean_advance_over_remerged_stock=sumgap/max(sumN,1e-300),max_N_U_relative=max_conservation))
assert sum(x['nontrivial_groups'] for x in rows)>0
out=dict(scope='hypothetical unguarded endpoint recompression of actual terminal stocks; FLRW collisionless threshold crossing; no actual global trajectory bound',width=.04,rows=rows)
Path(__file__).with_name('THRESHOLD_BOUND.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
