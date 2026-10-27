"""One new finite-source completion, saved operands only; no Phase A replay."""
import hashlib
import sys
import traceback
from mp_b import *
from channel_maps_b import build
from finite_b import Clock,finite
from owners_b import owners
from core_bridge_b import consume

OUT=ROOT/'results';R=dict(schema='BASS_QSS_FINITE_SOURCE_CHANNEL_TRANSACTION_V1',status='STARTED',new_B3i_rhs_invocations=0,
    original_DAG=dict(completed=27,total=88,delta=0),physical_radii=dict(eS=None,en=None,eE=None,geometry=None,temporal=None,total=None),
    requested_model='gpt-6.1-sol',observed_runtime_model=None,old_source_runs_replayed=0,
    inherited_accuracy_qualification='All new truncation/quadrature/MP bounds are conditional on admitted saved moments. 65-digit half-unit is representation rounding only, not a bound on old quadrature/source accuracy. Physical and total inherited input errors remain null.',
    source_emission_scope='Direct Ralpha*p is effective spontaneous escape with inverse3Ralpha*g*fin; separate hard stimulated term omitted in native Wien model. Sub-E21 2s F=(1+ncomp),reverse=n; super-E21 Raman F=n,reverse=(1+ncomp), already source-bound coefficients; no extra counts.')
def save():
    write(OUT/'FINITE_CHANNEL_RESULT.json',R);write(OUT/'PHASE_B_CHECKS.json',dict(checks=CHECKS,total=len(CHECKS),passed=sum(x['passed'] for x in CHECKS),failed=sum(not x['passed'] for x in CHECKS),status=R['status']))
def load(path,sha=None):
    raw=(ROOT/path).read_bytes()
    if sha and hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('immutable byte mismatch '+path)
    return json.loads(raw)
def controls():
    for name,fn in [('negative propensity rejected',lambda:propensity(m(-1))),('mismatched clock rejected',lambda:clock_identity(m(1),m('1.01')))]:
        try:fn()
        except ValueError:check(name,True)
        else:check(name,False)
    M=mp.matrix([[3,-1],[-2,4]]);K=M**-1;b0=mp.matrix([1,2]);b1=mp.matrix(['.1','.2']);p0=mp.matrix(['.3','.4']);L=m('.2');z=p0-K*b0+K*K*b1
    p=lambda s:K*(b0+b1*s)-K*K*b1+mp.expm(-M*s)*z
    exactp=p(L);I=K*(b0*L+b1*L*L/2)-(K*K*b1)*L+K*(mp.eye(2)-mp.expm(-M*L))*z
    residual=M*I-(b0*L+b1*L*L/2-(exactp-p0));check('exact constant-M affine-forcing integrated identity',norm(residual)<=m('1e-60')*norm(I),residual,m('1e-60'))
    differential=mp.matrix([mp.diff(lambda s:p(s)[i],L) for i in range(2)])-(b0+b1*L-M*exactp)
    check('exact affine-forcing differential identity',norm(differential)<=m('1e-60')*norm(exactp),differential,m('1e-60'))
    # Explicit known diagonal solution retains the initial finite layer.
    d=[m(2),m(5)];q=[m('.7'),m('.2')];init=[m('.1'),m('.4')];S=m('.3')
    endpoints=[q[i]+(init[i]-q[i])*mp.exp(-d[i]*S) for i in range(2)]
    ints=[q[i]*S+(init[i]-q[i])*(-mp.expm1(-d[i]*S))/d[i] for i in range(2)]
    err=max(abs(d[i]*ints[i]-(d[i]*q[i]*S-(endpoints[i]-init[i]))) for i in range(2))
    check('known diagonal two-state finite layer/integral',err<=m('1e-60'),dict(p=endpoints,Ip=ints,residual=err),m('1e-60'))

def main():
    controls();a=load('results/SOURCE_OPERANDS.json','179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd');packet=exact(load('inputs/NATIVE_QSS_STORED_INPUT_5126_5127.json','c335e0273677a55a910b4ff67a1aa47a64834a19bf460b286bfe78404e9cf710'))
    tube=load('inputs/reused_incoming_tube/TUBE_RESULT.json');incoming=load('inputs/reused_incoming_tube/FINITE_TUBE_INPUT_SLICE.json');baseline=load('inputs/reused_previous_inverse/INVERSION_NET_RESULT.json')['finite_photon']
    op,right=exact(a['endpoints']);c=exact(a['source_constants']);c.update(energies=packet['energy_eV'],eV_J=m(incoming['native_cosmology']['EV_J']),LYA_FACT=m(incoming['native_cosmology']['LYA_FACT_cm3_inv']),fHe=m(a['source_steady_temperature'][0]['fHe']))
    R['energy_unit_encoding']=dict(applied_eV_J=c['eV_J'],applied_model='exact binary64 lift of preserved native EV_J; matches admitted Phase A SI and saved old incoming/reference',decimal_SI_definition=m('1.602176634e-19'),relative_representation_difference=(c['eV_J']-m('1.602176634e-19'))/m('1.602176634e-19'),old_values_rescaled=False)
    c['G']=3*m(10**6)*c['LYA_FACT'];c['E21_J']=c['E21']*c['eV_J'];R['source_identities']=dict(PhaseA_sha256='179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd',packet_sha256='c335e0273677a55a910b4ff67a1aa47a64834a19bf460b286bfe78404e9cf710')
    model=build(op,packet['knots'][0],c,m(tube['nH_reference_m3']));R['endpoint_maps']=model;save()
    clock=Clock(incoming,tube,op,right,model);f=finite(clock,op,c);R['finite_solution']=f;R['quadrature_and_analytic_bounds']=QUADS;save()
    own=owners(model,f,clock,op,packet['knots'][0],c);R['finite_owners']=own;R['source_right_diagnostic']=dict(native_right_population=right['absolute_population'],new_model_p1=f['p1'],difference=f['p1']-mp.matrix(right['absolute_population']),native_right_M=right['M'],left_constant_activity_M=model['M'],role='source-variation diagnostic; this frozen-left dynamic model is not fitted to native right QSS')
    oldN=m(baseline['reference70']['Nout0']);oldU=m(baseline['reference70']['Uout0']);R['baseline_correction']=dict(old_binary64_Nout=baseline['Nout0'],old_binary64_Uout0=baseline['Uout0'],old_reference_Nout=oldN,old_reference_Uout0=oldU,
      new_Nout=own['Nout_new'],new_Uout0=own['Uout0_new'],DeltaN_correction=own['Nout_new']-oldN,DeltaU_correction=own['Uout0_new']-oldU,
      old_net_count_reference=baseline['reference70']['DeltaN0'],new_net_count=own['Nout_new']-clock.Nin,baseline_replayed=False,correction_only_added_to_saved_baseline=True)
    R['status']='TRANSACTION_CHECKS_PASS_BEFORE_ONCE_RHS';save()
    R['core_consumption']=consume(own,clock,right,R);R['status']='NUMERICAL_FINITE_TRANSACTION_PASS_AWAITING_INDEPENDENT_ROOT_ADMISSION';save();return 0
if __name__=='__main__':
    try:rc=main()
    except Exception as exc:R['status']='FAILED_PARTIAL_RESULTS_PRESERVED_RETURN_TO_ROOT';R['exception']=dict(type=type(exc).__name__,message=str(exc));traceback.print_exc();save();rc=2
    sys.exit(rc)
