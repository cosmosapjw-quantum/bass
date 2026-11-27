"""Held-out actual Commander 120..179; use exact C3Z sample, template, and training response."""
from pathlib import Path
import json,numpy as np
D=Path(__file__).resolve().parent;P=D.parent/'r118c3z_spin_projector_mc'
s=(P/'bass.py').read_text()
def rep(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
rep("A=[];N=[];ids=[];records=[]\n for i in range(30):","train=np.load(D.parent/'r118c3z_spin_projector_mc/mc_extension/COMMANDER_SCORES_120.npz')\n assert np.array_equal(idx,train['sample_pixel']) and np.array_equal(R,train['response'])\n A=[];N=[];ids=[];records=[];met=root/'reductions'\n for i in range(120,180):")
rep("assert len(A)>=16,(len(A),records)","assert len(A)>=40,(len(A),records)")
rep("out=dict(n_pairs=len(A),ids=ids,","from scipy.linalg import solve_triangular\n from scipy.stats import chi2\n T=train['signal']+train['noise'];mu=T.mean(axis=0);L0=np.linalg.cholesky(np.cov(T,rowvar=False));Z0=solve_triangular(L0,(A+N-mu).T,lower=True).T;d2=np.sum(Z0**2,axis=1);Ce=np.linalg.eigvalsh(np.cov(Z0,rowvar=False));\n out=dict(train_pairs=len(T),holdout_whitened_cov_eigenvalues=Ce.tolist(),holdout_whitened_mean=Z0.mean(axis=0).tolist(),mahalanobis_mean=float(np.mean(d2)),mahalanobis_95_exceed=int(np.sum(d2>chi2.ppf(.95,6))),chi2_reference_95=float(chi2.ppf(.95,6)),n_pairs=len(A),ids=ids,")
rep("write('COMMANDER_MC.json',out);write('COMMANDER_INPUTS.json',records);np.savez_compressed(D/'COMMANDER_SCORES.npz'","write('HOLDOUT.json',out);write('HOLDOUT_INPUTS.json',records);np.savez_compressed(D/'HOLDOUT_SCORES.npz'")
ns={'__file__':str(D/'heldout.py'),'__name__':'c4a_heldout'}
exec(compile(s,str(P/'bass.py'),'exec'),ns);ns['mc']()

