import gzip,json,hashlib,subprocess
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;R=Path('/home/cosmosapjw/Downloads/htt_r109_original_rec')
p=R/'research/r118c2g_angular_rei/REI_INITIAL_NORMAL.json.gz';q=gzip.decompress(p.read_bytes());j=json.loads(q)
def sha(b):return hashlib.sha256(b).hexdigest()
assert j['scope']=='HMLA2s2p_neutral_He_FLRW_to_REI_boundary_not_FULL'
assert j['history']['history_owner']=='REC_BIANCHI' and not j['history']['external_history']
s=j['history']['states'];a=np.array([1/(1+r['z']) for r in s]);u=np.log(a/a[0]);ne=np.array([r['n_H_m3']*r['x_HII'] for r in s]);assert np.all(np.diff(u)>0)
ini=j['initial'];assert ini['z']==20. and ini['x_HeII']==ini['x_HeIII']==0.
assert abs(a[-1]-1/21)<1e-14
u[-1]=np.log((1/21)/a[0])
np.savetxt(D/'REC_CLOCK.csv',np.c_[u,ne,a,[r['T_m_K'] for r in s],[r['x_HII'] for r in s]],header='u,ne_m3,a,T,xHII',comments='',delimiter=',',fmt='%.17e')
out=dict(scope=j['scope'],source=str(p),compressed_sha=sha(p.read_bytes()),uncompressed_sha=sha(q),source_commit=subprocess.check_output(['git','-C',str(R),'log','-1','--format=%H','--',str(p.relative_to(R))],text=True).strip(),initial=ini,background=j['background'],rows=len(s),clock_sha=sha((D/'REC_CLOCK.csv').read_bytes()),formal_full_boundary='HOLD_MISSING_VALIDATED_HISTORY',handoff='REC prescribed FLRW electron clock -> BASS native geometry and Thomson sky -> REI live; no REC geometry feedback')
(D/'REC_INPUT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
