"""Independent exact polynomial check of stored support; no research imports."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,struct,datetime

ROOT=Path('/workspace/scratch/14e1021f8231')
raw_path=ROOT/'bass_work/research/bass_isotropy_response_20261018/s12_birth_memory/native_support/inputs/B9_N64_PRIOR_ORIGINAL_ROW.json'
result_path=ROOT/'runtime_s12/support_be773dbf_run01/result/RETURN_SUPPORT_PREFLIGHT.json'
failure_path=ROOT/'bass_work/research/bass_isotropy_response_20261018/s12_birth_memory/native_support/inputs/ORIGINAL_S8_FAILURE.json'
raw=json.loads(raw_path.read_bytes()); result=json.loads(result_path.read_bytes()); old=json.loads(failure_path.read_bytes())
checks=[]
def check(name,value,**info):checks.append(dict(name=name,pass_check=bool(value),**info))
def bits(x):return struct.pack('<d',x).hex()
eps=Q(3,10**15)
check('boundaries_and_unchanged_gate',result['gate_exact']==str(eps) and len(result['certificates'])==16)
check('old_birth11_exact_support_bits',list(map(bits,raw['births'][11]['mu']))==list(map(bits,old['support_mu'])))
first=None
for j,birth in enumerate(raw['births']):
    z=sorted(set(Q.from_float(x)**2 for x in birth['mu']))
    fs=[(a*c,-a-c,Q(1)) for a,c in zip(z,z[1:])]+[(-z[0]*z[-1],z[0]+z[-1],Q(-1))]
    cert=result['certificates'][j]
    check(f'birth{j}_complete_polygon_facets',len(fs)==len(cert['facets']) and all(list(map(str,p))==c['polynomial'] for p,c in zip(fs,cert['facets'])))
    bounds=[];slacks=[]
    for i,(a,b,c) in enumerate(fs):
        # Solve coefficients by matching the monomial basis of P0/P2/P4.
        cc=8*c/35; bb=2*(b+30*cc/8)/3; aa=a+bb/2-3*cc/8
        nonnegative=all(a+b*x+c*x*x>=0 for x in z)
        identity=all(a+b*x+c*x*x==aa+bb*(3*x-1)/2+cc*(35*x*x-30*x+3)/8 for x in z)
        upper=aa+eps*(abs(aa)+abs(bb)+abs(cc));bounds.append(upper);slacks.append(aa)
        reported=cert['facets'][i]
        check(f'birth{j}_facet{i}_exact_polynomial_bound',nonnegative and identity and Q(reported['target_slack']['exact'])==aa and Q(reported['maximum_under_existing_gates']['exact'])==upper)
    status='OUTSIDE' if min(slacks)<0 else ('BOUNDARY' if min(slacks)==0 else 'STRICT_INTERIOR')
    check(f'birth{j}_classification',status==cert['exact_target_status'] and (min(bounds)<0)==cert['infeasible_at_existing_gates'])
    Z=z[-1];A=Z/3-Q(1,5);B=2*Z/3-Q(4,7);C=-Q(8,35);upper=A+eps*(abs(A)+abs(B)+abs(C))
    check(f'birth{j}_simple_necessary_bound',Q(cert['simple_zmax_certificate']['maximum_under_existing_gates']['exact'])==upper and Q(cert['z_max']['exact'])==Z)
    if min(bounds)<0 and first is None:first=j
check('first_infeasible_is13',first==13==result['first_infeasible_at_existing_gate'])
check('births0_to12_strict_interior_and13_to15_outside',all(c['exact_target_status']==('STRICT_INTERIOR' if j<13 else 'OUTSIDE') for j,c in enumerate(result['certificates'])))
check('all_three_registered_rational_controls_pass',len(result['rational_proof_controls'])==3 and all(c['pass'] for c in result['rational_proof_controls']))
report={'schema':'BASS_S12_INDEPENDENT_STORED_SUPPORT_REVIEW_V1','status':'PASS_SCOPED' if all(c['pass_check'] for c in checks) else 'FAIL','reviewer':'root; observer authored by p6_theory','checks_passed':sum(c['pass_check'] for c in checks),'checks_total':len(checks),'checks':checks,'inputs':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [raw_path,result_path,failure_path,Path(__file__)]],'first_infeasible_at_existing_gate':first,'proof':'Exact discrete-support nonnegative polynomial and monomial-to-Legendre basis matching; independent of KL solver/observer imports.','solver_calls':0,'projector_calls':0,'geometry_calls':0,'compiler_calls':0,'old_campaign_replays':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
out=Path(__file__).parent/'REVIEW.json'
with out.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:report[k] for k in ['status','checks_passed','checks_total','first_infeasible_at_existing_gate']}))
raise SystemExit(0 if report['status']=='PASS_SCOPED' else 1)
