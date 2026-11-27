import numpy as np,json,re
from pathlib import Path
D=Path(__file__).resolve().parent
def load(tag,eps,nt):
 stem=f'{tag}_{eps:g}_{nt}_192_8'
 p=np.genfromtxt(D/(stem+'.csv'),names=True,delimiter=',')
 assert len(p)==162 and np.all(np.isfinite(p.view(float)))
 q=p[(p['epoch']==1)&(p['ell']==3)]
 assert len(q)==7
 g=(D/(stem+'.geom')).read_text().splitlines()
 m={k:float(v) for k,v in re.findall(r'(max_gauss|min_screen|const_err)=([0-9eE+.-]+)',g[-1])}
 assert len(m)==3 and m['min_screen']>=0 and m['const_err']<1e-13
 S=np.array([float(x) for x in g[-2].split(',')][3:8])
 return q['Bre']+1j*q['Bim'],S,m
def norm(x):return float(np.linalg.norm(x))
def run():
 rows=[]
 for tag,ep,nt in [(tag,ep,nt) for tag in ['pred','best'] for ep,nt in [(.04,2048),(.04,4096),(.02,4096)]]:
  if not (D/f'{tag}_{ep:g}_{nt}_192_8.csv').exists():continue
  z=np.load(D.parent/'r118c3t_radial_null'/'best_4096.npz' if tag=='pred' else D.parent/'r118c3u_exact_wedge'/f'{tag}_selected_4096.npz')
  bp,sp,gp=load(tag,ep,nt);bm,sm,gm=load(tag,-ep,nt);bz,sz,gz=load('base',0.,nt)
  j=z['B'][:,9:16];ev=(bp+bm)/2-bz;od=(bp-bm)/2;je=ep**2*j[1]+ep**4*j[3];jo=ep**3*j[2]+ep**5*j[4]
  spre=np.array([sum((sg*ep)**(k+1)*z['S'][-1,k] for k in range(4)) for sg in [1,-1]])
  r=dict(tag=tag,eps=ep,steps=nt,even=norm(ev),odd=norm(od),jet_even=norm(je),jet_odd=norm(jo),even_rel=norm(ev-je)/norm(je),odd_rel=norm(od-jo)/norm(jo),zero_floor=norm(bz),signed_obj=max(norm(bp-bz),norm(bm-bz)),jet_signed_obj=max(norm(je+jo),norm(je-jo)),S_rel=max(norm(sp-sz-spre[0])/norm(spre[0]),norm(sm-sz-spre[1])/norm(spre[1])),max_gauss=max(gp['max_gauss'],gm['max_gauss'],gz['max_gauss']),min_screen=min(gp['min_screen'],gm['min_screen'],gz['min_screen']),max_const_err=max(gp['const_err'],gm['const_err'],gz['const_err']))
  rows.append(r)
 out=dict(rows=rows,scope='native harmonic analytic rest collision and parity projection, same C3T-to-C3U W/G stratum, C3U jet prediction, zero-control independently verified below 1e-22. Time refinement only; no coefficient precision claim until checked.')
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
