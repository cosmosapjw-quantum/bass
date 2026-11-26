from pathlib import Path
import subprocess, os, json, hashlib, concurrent.futures, sys
H=Path.home()
repos={
'BASS':(H/'worktrees/bass-r109-native-20261124','research/r118c3g_memory_controls','fc94711ff819fe7abb7b9af17b04f108feb98019','research/r109-native-nonlinear-sky-20261124'),
'REC':(H/'Downloads/htt_r109_original_rec','research/r118c3g_causal_shared_gas','f8dd695653885a8c7d83c6916a8fa7762ca67bef','research/r109-finite-tilt-ray-thomson-20261124'),
'REI':(H/'worktrees/rei-htt-thomson-20261124','research/r118c3g_spectral_cutoff','4d79d4744da4fd653cfa4a70e9ae32d45116062b','research/htt-tilted-thomson-20261124')}
env=dict(os.environ,GIT_TERMINAL_PROMPT='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
receipt=H/'r118c3g_push_receipts_20261126.jsonl'
def git(r,*args):
 p=subprocess.run(['git','-C',str(r),*args],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True);return p.stdout.strip()
def folder(k):r,d,_,_=repos[k];return r/d
def write(k,name,content):
 p=folder(k)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content if isinstance(content,str) else json.dumps(content,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def publish(k,stage,extra=()):
 r,d,base,branch=repos[k]
 assert git(r,'branch','--show-current')==branch
 git(r,'add',*(['--sparse'] if k=='REI' else []),'--',d,*extra)
 git(r,'diff','--cached','--check')
 staged=git(r,'diff','--cached','--name-only').splitlines()
 assert staged and all(x.startswith(d+'/') or x in extra for x in staged),staged
 git(r,'commit','-m',f'R118-C3G {stage}: {k} bounded science')
 head=git(r,'rev-parse','HEAD')
 git(r,'push','origin',f'HEAD:refs/heads/{branch}')
 remote=git(r,'ls-remote','--heads','origin',f'refs/heads/{branch}').split()[0]
 assert head==remote
 return dict(stage=stage,repo=k,head=head,remote=remote,tree=git(r,'rev-parse','HEAD^{tree}'),paths=staged)
def batch(stage,keys=None,extras=None):
 keys=list(keys or repos)
 done={(v['stage'],v['repo']) for v in map(json.loads,receipt.read_text().splitlines())} if receipt.exists() else set()
 keys=[k for k in keys if (stage,k) not in done]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  fut={pool.submit(publish,k,stage,(extras or {}).get(k,())):k for k in keys}
  errs=[]
  for f in concurrent.futures.as_completed(fut):
   try:
    row=f.result();print('PUSH',row['stage'],row['repo'],row['head'],flush=True)
    with receipt.open('a') as h:h.write(json.dumps(row)+'\n')
   except Exception as e:print('ERROR',fut[f],stage,repr(e),flush=True);errs.append(e)
  if errs:raise RuntimeError('stage publication incomplete')
def note(stage,content):
 for k,t in zip(repos,content):write(k,stage+'.md','# '+stage+' — R118-C3G '+k+'\n\n'+t+'\n')
 batch(stage)
if __name__=='__main__':
 for k,(r,d,b,br) in repos.items():
  assert git(r,'branch','--show-current')==br
  assert git(r,'ls-remote','--heads','origin',f'refs/heads/{br}').split()[0]==git(r,'rev-parse','HEAD')
 note('R1',[
  'C3F base fc94711; C3G independent BASS: quantify the admissible spin-3 null in a four-dimensional STF history span; use a principal-angle lower bound rather than minimizing a tiny B3 amplitude. Triple branch: retain exact C3F scalar donor; directional REC history must first evolve shared x,T. Scope Bianchi I native geometry, no universal Bianchi or production promotion.',
  'C3F base f8dd695; priority: shared H-only gas (x_HII,T) with accepted canonical ray histories over indices 63..128. Fixed H(a) angular-on/off pair isolates directional correction; original accepted prefix held fixed. Separate independent physical stock lane: conservative canonical momentum overlap and paired transfer, not claiming original virtual bins are physical stocks. H+He and full collision heat remain open.',
  'C3F base 4d79d4744; priority: same-grid signed nonlinear Compton+FF energy moment, refine frequency grid and cutoff with accepted C3B clock. Independent lane: finite-volume cutoff outflow accounting. Fixed-composition gas residual can replace legacy Compton term only in opt-in local oracle, no production V11 activation or live chemistry claim.'])
 note('R2',[
  'Literature: Pontzen & Challinor (2007), Bianchi model CMB polarization and its implications for CMB anomalies, MNRAS, https://scispace.com/papers/bianchi-model-cmb-polarization-and-its-implications-for-cmb-2flcq3mvks ; near-FLRW multipole hierarchy, not a proof of nonlinear memory controllability. C3C project spin-3 Gram and C3F native multi-species are internal authority for this test.',
  'Ali-Haimoud & Hirata, PRD 83 043513 (2011), https://doi.org/10.1103/PhysRevD.83.043513 : simultaneous level populations, free-electron fraction and radiation. Hirata PRD 78 023001 (2008), https://doi.org/10.1103/PhysRevD.78.023001 : delayed redshifting between Ly lines changes recombination. These isotropic results do not validate anisotropic common-atom closure. Use exact archived Oct 2012 rates and existing directional solver.',
  'Kompaneets continuity equation and small-energy-transfer validity: https://arxiv.org/abs/2103.06654 ; Chluba/Sunyaev-related cooling and bremsstrahlung absorption discussion https://www.aanda.org/articles/aa/full_html/2012/04/aa18194-11/aa18194-11.html ; Ballew et al. zero-frequency outflux https://faculty.sites.iastate.edu/hliu/files/inline-files/Kompaneets22.pdf . Reflecting finite x_min is a numerical boundary, not proof of physical photon conservation at x=0.'])
 note('R3',[
  'Source map: research/r118c3c_memory_kernel/WEDGE.json supplies pairs and Gram, P3=2G. C3F physical_wedge.py integrates A,P,W in five STF coordinates; native r118c3f_multi.rs gives actual three-species geometry and B3. First check projector rank and skew representation; use initial S and memory shapes for leading span only.',
  'Source map: C3F canonical_history.py incoming_canonical and step; run_history.py uses prescribed x,T from r118c2w_causal/FULL_128.npz. Replace only prescribed gas with time-discrete shared solve using previous accepted radiation history. thermal_rhs_ln_a is Compton+adiabatic without FULL heat; rates use same H. Delay minimum about 8.46e-5 in ln a; time step at 128 about 1.078e-5. Prefix and source energy table immutable.',
  'Source map: C3F signed.py computes signed face flux and exact Riccati pair sweep, FreeFree.advance returns photon energy/number. C3F run.py uses accepted C3B history and C3C table stages; energy scale BBmid*15/pi^4 eV per H, dimensionless x=h nu/(k_B Tcmb). Previous n=1024 Compton discrepancy -0.005285. V11 Rust remains separate.'])
 note('R4',[
  'Routes: (a) exact geometry of wedge^2 W intersect spin1, (b) actual native controls with mass/weights/orientation, (c) finite-amplitude departure from W. Route (a) gives an immediate obstruction/constructive design: choose hyperplane normal uniaxial and then tune temporal coefficients; necessary does not imply reachable. Generic triaxial normal cannot contain nonzero pure spin1.',
  'Routes: (a) use trapezoidal x solve and analytically implicit temperature with prior accepted rays; (b) backward Euler as independent order control; (c) physical remap in canonical momentum with exact cell overlap. Direction-only pair keeps H, prefix and atom source identical; angular-off replaces coframe by identity and rates by 1. Reject future-history evaluation.',
  'Routes: (a) instantaneous Planck energy moment at varying cutoffs; (b) same clock nonlinear spectral replay at 2048 and 4096; (c) opt-in closed or driven gas step that includes spectral increments once. Do not infer continuum zero-frequency outflow from reflecting results. Boundary sink must ledger both number and energy.'])
 note('R5',[
  'Derived: V=STF(3), Frobenius inner product, wedge^2 V=V_1 ⊕ V_3. A skew endomorphism in V_1 equals J_omega: Q -> [Omega,Q], Omega axial antisymmetric. For omega !=0 rotate axis to z. Matrix in project STF basis has two skew blocks (rates 2,1) and kernel E1=diag(-1,-1,2)/sqrt(6). Wolfram exact evaluation gave eigenvalues ±2i,±i,0 and null e1. For W=n^perp, wedge^2 W consists precisely of skew A with A n=0. Thus W contains nonzero spin1 wedge iff n is proportional to an axial STF tensor (two equal eigenvalues). For generic W, sigma_min(P3 B_W)>0 and ||P3 w||/||w|| >= sigma_min. This is a linear-span result, not a claim about all physical histories or finite-amplitude nulls.',
  'Derived: at endpoint eta_i, all retarded source times below eta_{i-1} allow independent reconstruction of incoming distortion. Solve F(x_i,T_i)=0 with x_i-x_{i-1}=h/2*(f_prev+f_i). Thermal equation T\'=A Tr-(2+A)T with A=Gamma/H; trapezoid solves T_i=[Tprev + h/2*(gprev+A_i Tr_i)]/[1+h/2*(2+A_i)] for trial x. Backward Euler similarly. Accept outgoing only after x root, not during candidate. Canonical stock dN=C dOmega q^2dq f; a conserved ray coordinate q; overlap volumes (min(b,d)^3-max(a,c)^3)_+/3 transfer occupation stock. Uncovered exterior is ledgered; energy difference from redshift not reaction heat.',
  'Derived: FV stock d_i=c_i delta n_i. With J_{i+1/2} positive from i+1 to i, dN=sum d_i, dE=scale sum x_i d_i. Internal face cancels number exactly and changes energy by -(x_{i+1}-x_i) delta stock. Low-frequency outward transfer L contributes -L number and -scale*x_0 L discrete energy, not zero until cutoff limit. For Planck, integral x^3/(exp x-1) dx=pi^4/15, omitted below xmin bounded by xmin^3/3; high tail bounded by exp(-xmax)(xmax^3+3xmax^2+6xmax+6)/(1-exp(-xmax)). Gas residual Cv(Tnew-Tpred)+DeltaE_C+DeltaE_FF=0 when Tpred excludes both exchanges and composition fixed.'])
 note('R6',[
  'Self-adversarial audit: rank4 alone is insufficient; repeated eigenvalues of n are necessary and sufficient for existence in wedge space, not for an attainable history integral. Numerical P3 and wedge orientation must use same ordered pairs. Use independent commutator projection as check; report lower bounds only on leading span. At finite epsilon S can leave W, invalidating a strict full nonlinear bound. Native subagents NOT_RUN (no native dispatch tool).',
  'Self-adversarial audit: angular-off coframe must be constant and shear zero while H(a) retained; changing H concurrently confounds effect. At each endpoint compare min lookback > step; positivity and root residual essential. Trapezoid is not L-stable for very stiff T, so compare BE and refined dt, report differences. Stock remap piecewise constant in canonical momentum; not a physical mapping of virtual excited state reservoirs, nor evidence of exterior atomic reactions. Native subagents NOT_RUN.',
  'Self-adversarial audit: exact FV energy conservation is independent of spectral accuracy. Do not double count the legacy gas Compton template. For signed perturbations full occupation nonnegative, not delta>=0. Small-x cutoff and changing T can alter low-frequency numerical stiffness. A reflecting boundary cannot measure real condensation, and a cutoff sink ledger cannot establish physical absorption. Native subagents NOT_RUN.'])
