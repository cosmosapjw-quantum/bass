"""One frozen B3e sweep; inherited reference tensors are read, never recomputed."""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
from numpy.polynomial.legendre import leggauss
import positive_angular as p
ROOT=p.ROOT;OUT=ROOT/'results';OUT.mkdir(exist_ok=True)

def reference(S,R,N):
    """Direct GL reference construction independent of selector and rule builder."""
    mu,weights=leggauss(N);F=0.;P=np.zeros((3,3));flux=np.zeros(3)
    phi=np.arange(2*N)*(2*math.pi/(2*N))
    for z,w in zip(mu,weights):
        ring=np.column_stack((math.sqrt(1-z*z)*np.cos(phi),math.sqrt(1-z*z)*np.sin(phi),np.full(2*N,z)))
        q=np.einsum('ni,ij,nj->n',ring,np.eye(3)+S,ring);v=ring@R.T;r=np.linalg.norm(v,axis=1);aq=w/(4*N)*q
        F+=float(np.sum(aq*r));P+=np.einsum('n,ni,nj->ij',aq/r,v,v);flux+=np.einsum('n,ni->i',aq,v)
    T=np.zeros((4,4));T[0,0]=F;T[1:,1:]=P;T[0,1:]=flux;T[1:,0]=flux
    return dict(F=F,P=P,pi=P-np.eye(3)*F/3,flux=flux,T=T)

def error_metrics(actual,ref,BT,beta,M):
    delta=actual['T']-ref['T'];dP=actual['P']-ref['P'];F=ref['F']
    low=float(np.linalg.eigvalsh((beta*M+dP+(beta*M+dP).T)/2)[0]);high=float(np.linalg.eigvalsh((beta*M-dP+(beta*M-dP).T)/2)[0])
    return dict(max_component_relative=float(np.max(np.abs(delta)))/F,
        frobenius_relative=float(np.linalg.norm(delta,'fro'))/F,
        stf_frobenius_relative=float(np.linalg.norm(actual['pi']-ref['pi'],'fro'))/F,
        ideal_bound_over_reference=BT/F,loewner_lower_min_over_F=low/F,loewner_upper_min_over_F=high/F)

def invariants(d,S,R,k,w,mass,nb):
    F=d['F'];Tkin=p.kinetic.tensor(k,w,mass);factor=p.SCALE.density_factor*p.EB*nb*np.linalg.det(R)
    rho,flux,pbar,pi=p.kinetic.moments(k,w,mass);g=p.geometry(S,R)
    return dict(normalization=abs(d['normalization']-1),sphere=d['sphere_residual'],
        exact_M=float(np.max(np.abs(d['M_quadrature']-g['M'])))/g['m2'],
        flux=float(np.max(np.abs(d['flux'])))/F,raw_trace=abs(float(np.trace(d['P']))-F)/F,
        psd_negative=max(0.,-float(np.linalg.eigvalsh((d['P']+d['P'].T)/2)[0]))/F,
        number=abs(float(np.sum(w))/(p.SCALE.density_factor*p.EB)/(nb*np.linalg.det(R))-1),
        packet_tensor=float(np.max(np.abs(Tkin/factor-d['T'])))/F,
        packet_rho=abs(rho/factor-F)/F,packet_flux=float(np.max(np.abs(flux/factor-d['flux'])))/F,
        packet_pressure=abs(pbar/factor-F/3)/F,packet_pi=float(np.max(np.abs(pi/factor-d['pi'])))/F,
        energy_bracket_lower=max(0.,g['F_lower']-F)/F,energy_bracket_upper=max(0.,F-g['F_upper'])/F,
        minimum_packet_weight=float(np.min(w)),minimum_q=d['minimum_q'],minimum_rule_weight=d['minimum_A'])

def row(label,scope,S,R,ref,extra=None):
    plan=p.select(S,R);baseline=p.select(S,R,baseline=True)
    n,A=p.sphere_rule(plan['selected']['Nmu']);k,w,m,d=p.packets(S,R,n,A)
    b=plan['selected'];g=p.geometry(S,R);err=error_metrics(d,ref,b['B_T'],b['beta'],g['M']);inv=invariants(d,S,R,k,w,m,1.)
    gates=dict(selector=b['bound_relative']<=p.ANGULAR and (len(plan['history'])==1 or plan['history'][-2]['bound_relative']>p.ANGULAR),
        baseline=baseline['selected']['baseline_relative']<=p.ANGULAR and (len(baseline['history'])==1 or baseline['history'][-2]['baseline_relative']>p.ANGULAR),
        tensor_target=max(err['max_component_relative'],err['frobenius_relative'])<=p.TARGET,
        actual_bound=err['frobenius_relative']<=err['ideal_bound_over_reference']+p.FLOAT_ALLOWANCE,
        loewner=min(err['loewner_lower_min_over_F'],err['loewner_upper_min_over_F'])>=-p.FLOAT_ALLOWANCE,
        invariants=all(v<=p.ROUND for key,v in inv.items() if not key.startswith('minimum_')),
        nonnegative=min(inv['minimum_packet_weight'],inv['minimum_q'],inv['minimum_rule_weight'])>=0)
    r=dict(label=label,scope=scope,S=S,R=R,detR=float(np.linalg.det(R)),source_aware=plan,baseline=baseline,
        selected_moments=d,reference=ref,errors=err,invariants=inv,gates=gates)
    if extra:r.update(extra)
    return r,(n,A,k,w,m)

raw_path=ROOT/'provenance/reused_data/B3D_COHORT_SWEEP.json'
assert hashlib.sha256(raw_path.read_bytes()).hexdigest()=='3b8cc8007266ff2419c04baf48a3eea6c45eb49c85a67627dc250285ad5beb71'
source_copies=json.loads((ROOT/'provenance/SOURCE_COPIES.json').read_text())
for c in source_copies:
    assert hashlib.sha256((ROOT/c['destination']).read_bytes()).hexdigest()==c['sha256']
old=json.loads(raw_path.read_text());rows=[];cache={};old_failures=[]
for case in old['fixtures']:
    S=np.asarray(case['S']);R=math.exp(-.4)*np.asarray(case['C'])
    ref={key:np.asarray(value)*math.exp(-.4) for key,value in case['reference']['64'].items()};ref['F']=float(ref['F'])
    inherited={key:case['rules'][key]['errors'] for key in ['Q14','Q26']}
    for rule,e in inherited.items():old_failures.append(dict(source=case['source'],eta=case['eta'],rule=rule,original_errors=e,failed_original_2e8=e['tensor']>p.TARGET))
    label=f"B3d_{case['source']}_eta{case['eta']:g}"
    r,_=row(label,'INHERITED_REFERENCE',S,R,ref,dict(eta=case['eta'],old_errors_unchanged=inherited,reference_evidence='REUSED_B3D_N64_SCALED_EXP_MINUS_0P4'))
    rows.append(r)
for label,S,R in p.fixtures():
    # Both selectors execute before any new angular moments are evaluated.
    p.select(S,R);p.select(S,R,baseline=True)
    ref64=reference(S,R,64);ref96=reference(S,R,96)
    r,data=row(label,'MANUFACTURED_ENDPOINT',S,R,ref96)
    proof64=p.bound(S,R,61);proof96=p.bound(S,R,93)
    diff=float(np.linalg.norm(ref64['T']-ref96['T'],'fro'))/ref96['F']
    r.update(reference64=ref64,reference64_96_relative_frobenius=diff,reference64_ideal_bound=proof64,reference96_ideal_bound=proof96)
    r['gates']['references']=max(diff,proof64['bound_relative'],proof96['bound_relative'])<=p.FLOAT_ALLOWANCE
    if label=='G5':
        oracle=np.zeros((4,4));oracle[0,0]=.7;oracle[1:,1:]=.7*(np.eye(3)/3+2*S/15)
        residual=float(np.max(np.abs(r['selected_moments']['T']-oracle)))/.7
        r['isotropic_analytic_oracle']=dict(T=oracle,residual=residual)
        r['gates']['isotropic_oracle']=residual<=p.ROUND
    rows.append(r);cache[label]=(r,data)
for label in ['G1','G3']:
    original,data=cache[label];S=original['S'];R=original['R'];Sr=p.OY@S@p.OY.T;Rr=p.OX@R@p.OY.T
    transformed=np.eye(4);transformed[1:,1:]=p.OX
    ref=original['reference'];refrot=dict(F=ref['F'],P=p.OX@ref['P']@p.OX.T,pi=p.OX@ref['pi']@p.OX.T,flux=p.OX@ref['flux'],T=transformed@ref['T']@transformed.T)
    r,_=row(label+'_ROT','CANONICAL_ORIENTATION_CHECK',Sr,Rr,refrot)
    n,A,*_=data;corot=p.moments(Sr,Rr,n@p.OY.T,A)
    expected=transformed@original['selected_moments']['T']@transformed.T
    cov=float(np.max(np.abs(corot['T']-expected)))/original['selected_moments']['F']
    b0=original['source_aware']['selected'];br=r['source_aware']['selected']
    boundres=max([abs(br[key]-b0[key])/ref['F'] for key in ['B_T','B_F','B_P_F','F_lower']]+[abs(br['bound_relative']-b0['bound_relative']),float(np.max(np.abs(p.geometry(Sr,Rr)['M']-p.OX@p.geometry(S,R)['M']@p.OX.T)))/ref['F']])
    r['covariance']=dict(corotated=corot,co_rotated_tensor_residual=cov,bound_relative_invariance_residual=boundres,K_exact_equal=br['K']==b0['K'])
    r['gates']['covariance']=cov<=p.ROUND and boundres<=p.ROUND and br['K']==b0['K']
    rows.append(r)
# Concatenate actual kinetic packets once, with positive physical cohort factors.
labels=['G1','G2','G3','G4'];nb=np.array([1.,.25,2.,.5]);coeff=np.array([p.EB*n*cache[l][0]['detR'] for l,n in zip(labels,nb)])
selected=sum(c*cache[l][0]['selected_moments']['T'] for c,l in zip(coeff,labels));fine=sum(c*cache[l][0]['reference']['T'] for c,l in zip(coeff,labels))
B=sum(c*cache[l][0]['source_aware']['selected']['B_T'] for c,l in zip(coeff,labels));den=sum(c*cache[l][0]['source_aware']['selected']['F_lower'] for c,l in zip(coeff,labels))
k=np.concatenate([cache[l][1][2] for l in labels]);w=np.concatenate([n*cache[l][1][3] for n,l in zip(nb,labels)]);mass=np.concatenate([cache[l][1][4] for l in labels]);Tpacket=p.kinetic.tensor(k,w,mass)/p.SCALE.density_factor
F=fine[0,0];err=dict(max_component_relative=float(np.max(np.abs(selected-fine)))/F,frobenius_relative=float(np.linalg.norm(selected-fine,'fro'))/F,ideal_bound_over_reference=B/F)
packet=float(np.max(np.abs(Tpacket-selected)))/selected[0,0]
number=float(np.sum(w))/(p.SCALE.density_factor*p.EB);expectednumber=float(sum(n*cache[l][0]['detR'] for n,l in zip(nb,labels)))
# Positive sum of matrix enclosures, in the common final frame.
Mbound=sum(c*cache[l][0]['source_aware']['selected']['beta']*p.geometry(cache[l][0]['S'],cache[l][0]['R'])['M'] for c,l in zip(coeff,labels));dP=selected[1:,1:]-fine[1:,1:]
lo=float(np.linalg.eigvalsh((Mbound+dP+(Mbound+dP).T)/2)[0])/F;hi=float(np.linalg.eigvalsh((Mbound-dP+(Mbound-dP).T)/2)[0])/F
err.update(loewner_lower_min_over_F=lo,loewner_upper_min_over_F=hi)
mixture=dict(label='MIXTURE_G1_G4',scope='POSITIVE_FOUR_COHORT_MIXTURE',cohorts=labels,birth_density_m3=nb,coefficients_SI=coeff,
    selected_tensor_SI=selected,reference_tensor_SI=fine,selected_tensor_over_Eb=selected/p.EB,reference_tensor_over_Eb=fine/p.EB,
    packet_tensor_SI=Tpacket,errors=err,ideal_absolute_bound_SI=B,F_lower_SI=den,bound_relative=B/den,
    number_density_m3=number,expected_number_density_m3=expectednumber,packet_tensor_residual=packet,
    number_residual=abs(number/expectednumber-1),points=len(w),
    gates=dict(selector=B/den<=p.ANGULAR,tensor_target=max(err['max_component_relative'],err['frobenius_relative'])<=p.TARGET,
        actual_bound=err['frobenius_relative']<=B/F+p.FLOAT_ALLOWANCE,loewner=min(lo,hi)>=-p.FLOAT_ALLOWANCE,
        packet=packet<=p.ROUND,number=abs(number/expectednumber-1)<=p.ROUND,nonnegative=bool(np.min(w)>=0)))
rows.append(mixture)
failed=[dict(label=r['label'],gate=key) for r in rows for key,value in r['gates'].items() if not value]
result=dict(status='COMPLETED' if not failed else 'GATE_FAILURE',dtype='float64',new_IVPs=0,old_campaign_replay=0,
    source_copies_verified=True,angular_budget=p.ANGULAR,target=p.TARGET,floating_reference_allowance=p.FLOAT_ALLOWANCE,
    rows=rows,failed_gates=failed,preserved_old_rule_results=old_failures,
    old_failures_count=sum(x['failed_original_2e8'] for x in old_failures),main_endpoint_count=19,orientation_check_count=2,mixture_count=1,
    qualification='Ideal-node truncation bounds; measured floating/reference checks are not interval certificates. Manufactured endpoints, no actual B3c history binding.')
(OUT/'POSITIVE_ANGULAR_SWEEP.json').write_text(json.dumps(p.serial(result),indent=2,allow_nan=False)+'\n')
print(json.dumps(dict(status=result['status'],rows=len(rows),failed_gates=failed,preserved_old_failures=result['old_failures_count'])))
sys.exit(bool(failed))
