import hashlib,json
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;H=Path('/home/cosmosapjw');I=H/'worktrees/rei-htt-thomson-20261124';B=D.parents[1]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
j=json.loads((I/'research/r118c2q_coupled_split/RESULTS.json').read_text());rows=[];sources={}
for s in j['cases']['q256']['segments']:
 p=Path(s['raw_path'])/'history.csv';assert sha(p)==s['hashes']['history.csv'];sources[str(p)]=sha(p)
 x=np.genfromtxt(p,names=True,delimiter=',',usecols=['a','ne_proper_cm3'])
 rows.append(np.stack([np.log(x['a']*21),1e6*x['ne_proper_cm3']],axis=1))
r=np.concatenate([rows[0],rows[1][1:]]);r[0,0]=0.;r[-1,0]=np.log(21/5)
np.savetxt(D/'rei_q256.csv',r,delimiter=',',header='u,ne_m3',comments='',fmt='%.17e')
j=json.loads((B/'research/r118c2m_energy_budget/RESULTS.json').read_text());p=Path(j['raw'])/'cross'/'history.tsv';q=next(v for v in j['results'] if v['name']=='cross');assert sha(p)==q['hashes']['history.tsv'];sources[str(p)]=sha(p)
x=np.genfromtxt(p,names=True,delimiter='\t',usecols=['eta','nH_m3','xe']);r=np.stack([x['eta'],x['nH_m3']*x['xe']],axis=1);r[0,0]=0.;r[-1,0]=np.log(21/5)
np.savetxt(D/'bass_cross.csv',r,delimiter=',',header='u,ne_m3',comments='',fmt='%.17e')
(D/'SOURCES.json').write_text(json.dumps(sources,indent=2)+'\n')
