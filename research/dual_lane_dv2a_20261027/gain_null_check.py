"""Additional scope-local B20 source-null test; does not repeat basis campaign."""
from pathlib import Path
import sys,json
import numpy as np
r=Path(__file__).resolve().parent;sys.path[:0]=[str(r/'code'),str(r/'vendor')]
from curvature_streaming import rank_one,curvature_rhs
from curvature_oracle import direct_curved_rhs
from polarized_dictionary import Grid,synthesize,source_matrix,stf_basis,hermitian
rows=[];amp=.1;kap=.7;target=amp*kap*np.sqrt(4*np.pi/5)*stf_basis()[2]
for nt in (8,12,20):
 g=Grid(nt,nt*2);c={('B',2,0):amp};base={('I',0,0):2*np.sqrt(4*np.pi)};full=base|c
 J=synthesize(g,c);dJ=direct_curved_rhs(g,c,0.,np.zeros((3,3)),rank_one(kap,[0,0,1]))
 M=np.einsum('n,nij->ij',g.w,J);dM=np.einsum('n,nij->ij',g.w,dJ)
 Y=synthesize(g,full);E=np.stack([g.bt,g.bp],axis=2)
 row={'ntheta':nt,'initial_source_norm':float(np.linalg.norm(M)),'source_derivative':dM.tolist(),'source_derivative_norm':float(np.linalg.norm(dM)),
 'analytic_difference':float(np.max(abs(dM-target))),'spectral_difference':float(np.max(abs(dM-source_matrix(curvature_rhs(c,rank_one(kap,[0,0,1]),3))))),
 'paired_positive_state_screen_min_eigenvalue':float(np.linalg.eigvalsh(np.einsum('nia,nij,njb->nab',E,hermitian(Y),E)).min())}
 assert row['initial_source_norm']<2e-11 and row['analytic_difference']<2e-11 and row['spectral_difference']<2e-11 and row['paired_positive_state_screen_min_eigenvalue']>0
 rows.append(row)
(r/'evidence/GAIN_NULL_B20.json').write_text(json.dumps({'status':'PASS_SCOPED','amplitude':amp,'kappa':kap,'rows':rows,'analytical_reference':'Mdot=amp*kappa*sqrt(4*pi/5)*U20','ivps':0},indent=2))
print(json.dumps(rows,indent=2))
