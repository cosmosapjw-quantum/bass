from pathlib import Path
import numpy as np,hashlib,json
D=Path(__file__).resolve().parent
E=Path.home()/'worktrees/rei-htt-thomson-20261124/research/r118c4n_dg_jvp'
tags=['base','H-0.01','H+0.01','H-0.003','H+0.003']
p={tag:E/(tag+'_work.csv') for tag in tags}
d={tag:np.loadtxt(f,delimiter=',',dtype=np.longdouble) for tag,f in p.items()}
b=d['base'];eps=np.longdouble('.01')
assert all(np.array_equal(x[:,0],b[:,0]) for x in d.values())
t1=(d['H+0.01'][:,1:]-d['H-0.01'][:,1:])/(2*eps)
t2=((d['H+0.01'][:,1:]-b[:,1:])+(d['H-0.01'][:,1:]-b[:,1:]))/(2*eps**2)
rows=[]
for tag,pv in [('H-0.003','-.003'),('H+0.003','.003')]:
 pv=np.longdouble(pv)
 y=d[tag][:,1:]-b[:,1:];pred=t1*pv+t2*pv*pv
 scale=np.max(abs(y),axis=0)
 rows.append(dict(tag=tag,response_max=list(map(float,scale)),absolute_gap=list(map(float,np.max(abs(pred-y),axis=0))),relative_gap=list(map(float,np.max(abs(pred-y),axis=0)/np.maximum(scale,np.longdouble('1e-300')))),original_vs_work_response_gap=float(np.max(abs(y[:,0]-y[:,1]))),original_vs_work_baseline_gap=float(np.max(abs(d[tag][:,1]-d[tag][:,2])))))
out=dict(columns=['direct_external_density','energy_work_reconstruction'],source_sha={k:hashlib.sha256(f.read_bytes()).hexdigest() for k,f in p.items()},rows=rows,first=t1.astype(float).tolist(),second_coefficient=t2.astype(float).tolist(),scope='Native stage density difference in longdouble postprocessing; original stored binary64 owner cancellation cannot be undone; work-based evaluation measured separately; not analytic owner derivatives.')
(D/'WORK_TABLE_AUDIT.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps(out['rows'],indent=2))
