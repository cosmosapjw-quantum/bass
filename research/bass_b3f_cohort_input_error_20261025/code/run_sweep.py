"""Prescribed 21 finite pairs + 2 algebraic frame checks + 1 positive mixture."""
import csv
import json
import math
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss
import cohort_input_error as c
p=c.p;OUT=c.ROOT/'results'

def reference(S,R,N):
    """Independent product reference; no calls to selector/rule/moments builders."""
    mu,weights=leggauss(N);F=0.;P=np.zeros((3,3));flux=np.zeros(3);phi=np.arange(2*N)*math.pi/N
    for z,w in zip(mu,weights):
        ring=np.column_stack((math.sqrt(1-z*z)*np.cos(phi),math.sqrt(1-z*z)*np.sin(phi),np.full(2*N,z)))
        q=1+np.einsum('ni,ij,nj->n',ring,S,ring);v=ring@R.T;r=np.linalg.norm(v,axis=1);aq=w*q/(4*N)
        if np.any(q<0):raise ValueError('negative source; no projection')
        F+=float(np.sum(aq*r));P+=np.einsum('n,ni,nj->ij',aq/r,v,v);flux+=np.einsum('n,ni->i',aq,v)
    T=np.zeros((4,4));T[0,0]=F;T[1:,1:]=P;T[0,1:]=flux;T[1:,0]=flux
    return dict(F=F,P=P,flux=flux,T=T)

def moment_invariants(T):
    F=float(T[0,0]);P=T[1:,1:]
    if F<=0:raise ValueError('positive tensor reference energy required')
    return dict(symmetry=float(np.max(np.abs(T-T.T)))/F,trace=abs(float(np.trace(P))-F)/F,
                flux=float(np.linalg.norm(T[0,1:]))/F,psd=max(0.,-float(np.linalg.eigvalsh((P+P.T)/2)[0]))/F)

def main():
    raw=c.nominal_data();rows=[];cache={};newreferences=0
    salt=p.OY@np.diag([-.2,.4,-.2])@p.OY.T;ralt=p.OZ@np.diag([.55,.65,.80])@p.OX.T
    cases=[('P0',0.)]+[(f'P{i}',e) for i in range(1,6) for e in [1e-10,1e-8,1e-4,1e-2]]
    for family,eps in cases:
        parent=raw['G5' if family=='P5' else 'G3'];S0=np.asarray(parent['S']);R0=np.asarray(parent['R']);S1=S0.copy();R1=R0.copy();n1=1.
        if family=='P1':n1=1+eps
        if family=='P2':R1=(1-eps)*R0
        if family in ['P3','P4']:S1=(1-eps)*S0+eps*salt
        if family=='P4':R1=(1-eps)*R0+eps*ralt;n1=1+eps/2
        if family=='P5':S1=(1-eps)*S0;R1=(1-eps/2)*R0;n1=1+eps
        bt=parent['source_aware']['selected']['B_T'];bd=c.pair(S0,R0,1.,S1,R1,n1,bt);ball=c.ball(S0,R0,1.,bt,**bd['radii'])
        T0=np.asarray(parent['reference']['T']);Tangular=np.asarray(parent['selected_moments']['T']);W0=bd['W0'];W1=bd['W1']
        extra={};refgate=True
        if family in ['P0','P1']:T1=T0.copy();evidence='EXACT_REUSE_NOMINAL_T'
        elif family=='P2':T1=(1-eps)*T0;evidence='EXACT_MAP_SCALING_Q_FOURTH_POWER'
        elif family=='P5':
            lam=.7*(1-eps/2);T1=np.zeros((4,4));T1[0,0]=lam;T1[1:,1:]=lam*(np.eye(3)/3+2*S1/15);evidence='EXACT_ISOTROPIC_ORACLE'
        else:
            ref64=reference(S1,R1,64);ref96=reference(S1,R1,96);newreferences+=1;T1=ref96['T'];evidence='NEW_INDEPENDENT_GL64_128_GL96_192'
            agreement=float(np.linalg.norm(ref64['T']-T1,'fro'))/ref96['F'];b64=p.bound(S1,R1,61);b96=p.bound(S1,R1,93)
            extra=dict(reference64=ref64,reference96=ref96,reference64_96_relative=agreement,fixed_K61_bound=b64,fixed_K93_bound=b96)
            refgate=max(agreement,b64['bound_relative'],b96['bound_relative'])<=c.EPS_FP
        Q0=W0*T0;Q1=W1*T1;Qa=W0*Tangular;delta=Q1-Q0;combined=Q1-Qa;energy=float(Q1[0,0]);allow=c.EPS_FP*energy;up=bd['U_pair']
        err=dict(signed_energy_difference=float(delta[0,0]),signed_tensor_difference=delta,energy_absolute=abs(float(delta[0,0])),tensor_absolute=float(np.linalg.norm(delta,'fro')),
                 combined_signed_tensor_difference=combined,combined_relative=float(np.linalg.norm(combined,'fro'))/energy,
                 energy_bound_signed_residual=abs(float(delta[0,0]))-up,tensor_bound_signed_residual=float(np.linalg.norm(delta,'fro'))-c.SQRT2*up,
                 comparison_allowance_absolute=allow)
        inv=moment_invariants(Q1)
        gates=dict(reference=refgate,energy_bound=err['energy_bound_signed_residual']<=allow,tensor_bound=err['tensor_bound_signed_residual']<=allow,
                   admitted_actual=bd['composition']['status']!='CERTIFIED_SCOPED_NUMERICAL_BUDGET' or err['combined_relative']<=c.TAU,invariants=max(inv.values())<=p.ROUND)
        if ball['status']=='PHYSICAL_BALL_CERTIFIED':
            contained=dict(map=float(np.linalg.norm(R1-R0,2))<=ball['radii']['eR'],source=float(np.linalg.norm(S1-S0,'fro'))<=ball['radii']['eS'],density=abs(n1-1.)<=ball['radii']['en'])
            ball['paired_endpoint_containment']=contained;gates['ball_pair_containment']=all(contained.values())
            gates['ball_covers_pair']=up<=ball['U_ball']+allow
            gates['ball_covers_actual']=err['energy_absolute']<=ball['U_ball']+allow and err['tensor_absolute']<=c.SQRT2*ball['U_ball']+allow
            gates['ball_admitted_actual']=ball['composition']['status']!='CERTIFIED_SCOPED_NUMERICAL_BUDGET' or err['combined_relative']<=c.TAU
        label=f'{family}_eps{eps:g}';row=dict(label=label,scope='MANUFACTURED_FINITE_ENDPOINT',family=family,epsilon=eps,parent=parent['label'],S0=S0,R0=R0,n0=1.,S1=S1,R1=R1,n1=n1,
            reference_evidence=evidence,nominal_selected_K=parent['source_aware']['selected']['K'],nominal_B_T=bt,pair=bd,ball=ball,reference_T0=T0,reference_T1=T1,
            nominal_angular_T=Tangular,Q0=Q0,Q1=Q1,Qangular0=Qa,errors=err,invariants=inv,gates=gates,**extra)
        if family in ['P4','P5'] and eps==.01:
            rays,A=p.sphere_rule(32);k,w,m,d=p.packets(S1,R1,rays,A,n1);packet=p.kinetic.tensor(k,w,m)/p.SCALE.density_factor;direct=W1*d['T'];F=float(direct[0,0]);number=float(np.sum(w))/(p.SCALE.density_factor*p.EB);expected=n1*float(np.linalg.det(R1))
            checks=dict(tensor=float(np.max(np.abs(packet-direct)))/F,number=abs(number/expected-1),normalization=abs(d['normalization']-1),**moment_invariants(packet))
            row['kinetic']=dict(rule='GL32x64',points=len(A),tensor_SI=packet,direct_same_rule_tensor_SI=direct,number_density=number,expected_number_density=expected,
                                minimum_weight=float(np.min(w)),minimum_q=d['minimum_q'],checks=checks)
            gates['kinetic']=max(checks.values())<=p.ROUND and np.min(w)>=0 and d['minimum_q']>=0
        rows.append(row);cache[(family,eps)]=row
    # One deliberately wrong omitted-det control and one changed-denominator control.
    control=cache[('P2',1e-4)];wrong=p.EB*np.linalg.det(np.asarray(control['R0']))*np.asarray(control['reference_T1']);right=np.asarray(control['Q1'])
    omitted=float(np.linalg.norm(wrong-right,'fro'))/right[0,0]
    denrow=cache[('P2',.01)];co=denrow['pair']['composition'];frozen=(co['A0']+c.SQRT2*co['U']+c.EPS_FP*co['B0'])/co['L0']
    controls=dict(omitted_det=dict(label=control['label'],wrong_tensor_SI=wrong,correct_tensor_SI=right,signed_residual_SI=wrong-right,relative_residual=omitted,gate=omitted>c.TAU),
                  frozen_denominator=dict(label=denrow['label'],corrected_total=co['operational_total'],frozen_nominal_total=frozen,difference=co['operational_total']-frozen,gate=co['operational_total']>frozen))
    base=cache[('P4',.01)]
    for j,(Ob,Of) in enumerate([(p.OY,p.OX),(p.OZ,p.OY)],1):
        S0=Ob@np.asarray(base['S0'])@Ob.T;S1=Ob@np.asarray(base['S1'])@Ob.T;R0=Of@np.asarray(base['R0'])@Ob.T;R1=Of@np.asarray(base['R1'])@Ob.T
        br=c.pair(S0,R0,1.,S1,R1,base['n1'],base['nominal_B_T']);O=np.eye(4);O[1:,1:]=Of
        q0=O@np.asarray(base['Q0'])@O.T;q1=O@np.asarray(base['Q1'])@O.T
        # Algebra on saved tensors and six diagnostic rays; no angular campaign.
        rays=np.concatenate([np.eye(3),-np.eye(3)]);rays_rot=rays@Ob.T;F=q1[0,0]
        oldv=rays@np.asarray(base['R1']).T;newv=rays_rot@R1.T
        oldq=1+np.einsum('ni,ij,nj->n',rays,np.asarray(base['S1']),rays);newq=1+np.einsum('ni,ij,nj->n',rays_rot,S1,rays_rot)
        recovered=O.T@q1@O
        checks=dict(tensor=float(np.max(np.abs(recovered-np.asarray(base['Q1']))))/F,bound=abs(br['U_pair']-base['pair']['U_pair'])/F,h=abs(br['h']-base['pair']['h'])/float(base['reference_T1'][0][0]),ray_map=float(np.max(np.abs(newv-oldv@Of.T))),ray_source=float(np.max(np.abs(oldq-newq))),normalization=float(np.max(np.abs(np.sum(rays_rot*rays_rot,axis=1)-1))),**moment_invariants(q1))
        rows.append(dict(label=f'FRAME_{j}',scope='SAVED_ENDPOINT_TWO_FRAME_COVARIANCE',epsilon=.01,parent_row=base['label'],Ob=Ob,Of=Of,S0=S0,S1=S1,R0=R0,R1=R1,pair=br,Q0=q0,Q1=q1,birth_rays=rays,transformed_birth_rays=rays_rot,checks=checks,gates=dict(covariance=max(checks.values())<=p.ROUND)))
    components=[cache[(f'P{i}',1e-10)] for i in range(1,5)];coeff=[1.,.25,2.,.5];mc=c.mixture([r['pair'] for r in components],coeff)
    q0=sum(w*np.asarray(r['Q0']) for w,r in zip(coeff,components));q1=sum(w*np.asarray(r['Q1']) for w,r in zip(coeff,components));qa=sum(w*np.asarray(r['Qangular0']) for w,r in zip(coeff,components));delta=q1-q0;actual=float(np.linalg.norm(q1-qa,'fro'))/q1[0,0];allow=c.EPS_FP*q1[0,0]
    rows.append(dict(label='MIXTURE',scope='POSITIVE_FOUR_COHORT_MIXTURE',cohorts=[r['label'] for r in components],multiplicities=coeff,composition=mc,Q0=q0,Q1=q1,Qangular0=qa,signed_tensor_difference=delta,
                     actual_combined_relative=actual,gates=dict(energy_bound=abs(delta[0,0])<=mc['U']+allow,tensor_bound=float(np.linalg.norm(delta,'fro'))<=c.SQRT2*mc['U']+allow,
                     admitted_actual=mc['status']!='CERTIFIED_SCOPED_NUMERICAL_BUDGET' or actual<=c.TAU)))
    failed=[dict(label=r['label'],gate=k) for r in rows for k,v in r['gates'].items() if not v]+[dict(label='CONTROL',gate=k) for k,v in controls.items() if not v['gate']]
    if len(rows)!=24 or newreferences!=8:failed.append(dict(label='COUNTS',gate='frozen_counts'))
    result=dict(status='GATE_FAILURE' if failed else 'COMPLETED',rows=rows,controls=controls,failed_gates=failed,row_count=len(rows),new_reference_pairs=newreferences,new_IVPs=0,old_campaign_replay=0,
                reference_allowance=c.EPS_FP,target=c.TAU,scope='MANUFACTURED_FINITE_INPUT_CERTIFICATES_NO_HISTORY_BINDING',model_identity=dict(requested='gpt-6.1-sol',observed=None),
                qualifications=['Ideal exact-arithmetic bounds; empirical binary64 reserve is not interval certification.','Actual B3c/REC history input binding remains OPEN_INPUT.'])
    OUT.mkdir(exist_ok=True);(OUT/'COHORT_INPUT_ERROR_SWEEP.json').write_text(json.dumps(p.serial(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(status=result['status'],rows=len(rows),new_reference_pairs=newreferences,failed_gates=failed)))
    return bool(failed)
if __name__=='__main__':sys.exit(main())
