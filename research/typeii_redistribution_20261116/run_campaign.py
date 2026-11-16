#!/usr/bin/env python3
"""Bounded actual-source transient experiments, no silent cached run reuse."""
import json
from transient_transport import simulate,HERE
CASES=[
 ('time80',dict(cells=80,nmu=4,nphi=8,steps=80)),
 ('time160',dict(cells=80,nmu=4,nphi=8,steps=160)),
 ('time320',dict(cells=80,nmu=4,nphi=8,steps=320)),
 ('freq40',dict(cells=40,nmu=4,nphi=8,steps=320)),
 ('freq160',dict(cells=160,nmu=4,nphi=8,steps=320)),
 ('angle12',dict(cells=80,nmu=3,nphi=4,steps=320)),
 ('angle72',dict(cells=80,nmu=6,nphi=12,steps=320)),
 ('frozen',dict(cells=80,nmu=4,nphi=8,steps=320,frozen_matter=True)),
 ('no_recoil',dict(cells=80,nmu=4,nphi=8,steps=320,recoil=False)),
 ('no_diffusion',dict(cells=80,nmu=4,nphi=8,steps=320,frequency=False)),
 ('no_ionization',dict(cells=80,nmu=4,nphi=8,steps=320,destruction=False)),
 ('band40',dict(width=40.,cells=160,nmu=4,nphi=8,steps=320)),
 ('band80',dict(width=80.,cells=320,nmu=4,nphi=8,steps=320)),
 ('source1700',dict(z0=1700.,cells=80,nmu=4,nphi=8,steps=320)),
 ('source1700_frozen',dict(z0=1700.,cells=80,nmu=4,nphi=8,steps=320,frozen_matter=True)),
 ('source1392',dict(z0=1392.,cells=80,nmu=4,nphi=8,steps=320)),
 ('source800',dict(z0=800.,cells=80,nmu=4,nphi=8,steps=320)),
]
def main():
 out=[]
 for label,kw in CASES:
  result=simulate(label,**kw);out.append(result)
  (HERE/'TRANSIENT_CAMPAIGN.json').write_text(json.dumps({'cases':out,'case_count':len(out),'scope':'evolving input, dilute tagged packet, finite absorbing boundaries, factorized redistribution'},indent=2)+'\n')
  print('CASE',label,'red',result['red_drift']+result['red_diffusion'],'blue',result['blue_diffusion']+result['blue_drift'],'ion',result['ionized'],'Nres',result['max_number_budget_abs_gap'],flush=True)
 print('ACTUAL_TRANSIENT_CAMPAIGN_COMPLETE',len(out),flush=True)
if __name__=='__main__':main()
