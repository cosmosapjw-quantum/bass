"""Independent parity and wedge coefficient check for C3H native controls."""
import json,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent
def vec(l):
 x=np.genfromtxt(D/(l+'.csv'),names=True,delimiter=',');m=x['ell']==3;return x['re'][m]+1j*x['im'][m]
def main():
 rows={}
 for amp,plus,minus in [(0.0125,'orthogonal125_fine','orthogonal125_minus'),(0.00625,'orthogonal062_plus','orthogonal062_minus')]:
  a,b=vec(plus),vec(minus);even=(a+b)/2;odd=(a-b)/2
  rows[str(amp)]=dict(even=float(np.linalg.norm(even)),odd=float(np.linalg.norm(odd)),even_over_amp2=float(np.linalg.norm(even)/amp**2),odd_over_amp3=float(np.linalg.norm(odd)/amp**3))
 a,b=rows.values();er=abs(a['even_over_amp2']/b['even_over_amp2']-1);orr=abs(a['odd_over_amp3']/b['odd_over_amp3']-1)
 ref=json.loads((D/'orthogonal125_fine.json').read_text());pred=16/np.sqrt(378)*ref['normalized_wedge']*ref['fraction']
 check=abs(a['even_over_amp2']/pred-1)
 assert er<1e-3 and orr<1e-3 and check<2e-3
 out=dict(rows=rows,even_refinement_relative=er,odd_refinement_relative=orr,quadratic_wedge_prediction=float(pred),relative_to_quadratic=check,scope='sampled two amplitudes on native geometry; empirical leading even quadratic and odd cubic, not uniform expansion proof')
 (D/'PARITY_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
