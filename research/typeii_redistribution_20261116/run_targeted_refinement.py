#!/usr/bin/env python3
import json
from transient_transport import simulate,HERE
CASES=[
 ('time640',dict(cells=80,nmu=4,nphi=8,steps=640)),
 ('time1280',dict(cells=80,nmu=4,nphi=8,steps=1280)),
 ('frozen640',dict(cells=80,nmu=4,nphi=8,steps=640,frozen_matter=True)),
 ('fine640',dict(cells=160,nmu=4,nphi=8,steps=640)),
 ('source1700_640',dict(z0=1700.,cells=80,nmu=4,nphi=8,steps=640)),
 ('source1700_frozen640',dict(z0=1700.,cells=80,nmu=4,nphi=8,steps=640,frozen_matter=True)),
]
def main():
 res=[]
 for label,kw in CASES:
  r=simulate(label,**kw);res.append(r)
  (HERE/'TARGETED_REFINEMENT.json').write_text(json.dumps(res,indent=2)+'\n')
  print(label,'red',r['red_drift']+r['red_diffusion'],'blue',r['blue_diffusion'],'ion',r['ionized'],flush=True)
if __name__=='__main__':main()
