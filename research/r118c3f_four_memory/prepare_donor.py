import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;R=Path('/home/cosmosapjw/Downloads/htt_r109_original_rec/research/r118c3f_directional_history')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n in ('zerofine','plusfine'):
 p=R/(n+'_tight.json');j=json.loads(p.read_text());s=j['history']['states'];a=np.array([1/(1+r['z']) for r in s]);u=np.log(a/a[0]);ne=np.array([r['n_H_m3']*r['x_HII'] for r in s]);u[-1]=np.log((1/21)/a[0])
 np.savetxt(D/(n+'_CLOCK.csv'),np.c_[u,ne,a,[r['T_m_K'] for r in s],[r['x_HII'] for r in s]],header='u,ne_m3,a,T,xHII',comments='',delimiter=',',fmt='%.17e')
 h=sha(p);ini=j['initial'];cfg=(D.parent/'r118c3d_four_tracks/m3.cfg').read_text().splitlines();values={'initial_state_id':'REC_HMLA_'+h,'initial_x_hii':repr(ini['x_HII']),'initial_temperature_k':repr(ini['T_m_K'])}
 (D/(n+'.cfg')).write_text('\n'.join(f"{l.split('=',1)[0]}={values[l.split('=',1)[0]]}" if l.split('=',1)[0] in values else l for l in cfg)+'\n')
 (D/(n+'_DONOR.json')).write_text(json.dumps(dict(source=str(p),source_sha=h,clock_sha=sha(D/(n+'_CLOCK.csv')),initial=ini),indent=2)+'\n')
