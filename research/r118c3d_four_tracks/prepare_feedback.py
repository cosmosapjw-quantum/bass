import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent;R=Path('/home/cosmosapjw/Downloads/htt_r109_original_rec/research/r118c3d_two_sided')
p=R/'CLOCK_DONOR_TIGHT.json';j=json.loads(p.read_text());s=j['history']['states'];a=np.array([1/(1+r['z']) for r in s]);u=np.log(a/a[0]);ne=np.array([r['n_H_m3']*r['x_HII'] for r in s])
assert np.all(np.diff(u)>0) and j['scope']=='CONDITIONAL_BASS_SCALAR_CLOCK_HMLA_H_ONLY_NOT_FULL'
u[-1]=np.log((1/21)/a[0])
np.savetxt(D/'FEEDBACK_CLOCK.csv',np.c_[u,ne,a,[r['T_m_K'] for r in s],[r['x_HII'] for r in s]],header='u,ne_m3,a,T,xHII',comments='',delimiter=',',fmt='%.17e')
h=hashlib.sha256(p.read_bytes()).hexdigest()
(D/'FEEDBACK_INPUT.json').write_text(json.dumps(dict(donor=str(p),donor_sha=h,clock_sha=hashlib.sha256((D/'FEEDBACK_CLOCK.csv').read_bytes()).hexdigest(),initial=j['initial'],input_bass_clock_sha=j['bass_clock_sha']),indent=2)+'\n')
cfg=(D/'m3.cfg').read_text().splitlines();values={'initial_state_id':'REC_HMLA_'+h,'initial_x_hii':repr(j['initial']['x_HII']),'initial_temperature_k':repr(j['initial']['T_m_K'])}
(D/'feedback.cfg').write_text('\n'.join(f"{l.split('=',1)[0]}={values[l.split('=',1)[0]]}" if l.split('=',1)[0] in values else l for l in cfg)+'\n')
