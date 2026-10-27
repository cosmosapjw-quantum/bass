"""One bounded new Phase A invocation: controls + four inverse/source operands.

No native history run, old full result execution, finite transaction, or plot.
Reconstructed endpoint results are saved before the right holdout is opened.
"""
import csv
import hashlib
import io
import json
import math
import sys
import traceback
from pathlib import Path
import numpy as np
from native import ROOT,SOURCE,constants,Rates,read_twog,steady_tm,populate,solve_virtual,validate_diffusion
from diffusion_inverse import reconstruct,solve_ratio
from energy import moments,synthetic_control

PACKET_SHA='c335e0273677a55a910b4ff67a1aa47a64834a19bf460b286bfe78404e9cf710'
CONTRACT_SHA='8393803be80a7ad7e4d9b0e728362da8ab32d63783c0ca3a1c3190de30ad4647'
OUT=ROOT/'results'
CHECKS=[]
RESULT=dict(schema='BASS_NATIVE_QSS_SOURCE_OPERANDS_PHASE_A_V1',status='STARTED',
    original_DAG=dict(completed=27,total=88,delta=0),new_B3i_calls=0,native_history_solves=0,
    old_inverse_replays=0,old_finite_photon_replays=0,plot=0,requested_model='gpt-6.1-sol',observed_runtime_model=None,
    physical_radii=dict(eS=None,en=None,eE=None,geometry=None,total=None),diffusion_inversions=[],endpoints=[],
    reconstruction_holdout_boundary='All constructed endpoints saved before opening validation snapshot',
    closure='Source coefficients and effective Maxwellian successful-channel energy moment only; Phase B not performed')

def plain(v):
    if isinstance(v,np.ndarray):return [plain(x) for x in v.tolist()]
    if isinstance(v,np.generic):return v.item()
    if isinstance(v,dict):return {k:plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [plain(x) for x in v]
    return v
def write(path,obj):
    path.write_text(json.dumps(plain(obj),indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def save():
    OUT.mkdir(exist_ok=True);write(OUT/'SOURCE_OPERANDS.json',RESULT)
    write(OUT/'PHASE_A_CHECKS.json',dict(schema='BASS_QSS_PHASE_A_CHECKS_V1',checks=CHECKS,total=len(CHECKS),
      passed=sum(x['passed'] for x in CHECKS),failed=sum(not x['passed'] for x in CHECKS),status=RESULT['status'],new_B3i_calls=0))
def check(name,ok,observed=None,limit=None,scale=None):
    CHECKS.append(dict(name=name,passed=bool(ok),observed=plain(observed),limit=limit,scale=scale))
    print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def require(name,ok,observed=None,limit=None,scale=None):
    check(name,ok,observed,limit,scale)
    if not ok:raise ValueError('frozen prerequisite failed: '+name)
def identity(raw,sha):
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('immutable input byte identity mismatch')
def expect_value_error(name,fn):
    try:fn()
    except ValueError:check(name,True);return
    check(name,False,'expected ValueError absent')
def rel(a,b):return abs(a-b)/abs(b) if b else (0. if a==0 else None)
def tv_product(Tvv,x):return Tvv[0]*x+Tvv[1]*np.r_[0.,x[:-1]]+Tvv[2]*np.r_[x[1:],0.]

def endpoint(knot,TM,twog,c,rates,nH_reference):
    op=populate(knot,TM,twog,c,rates);Trr,Trv,Tvr,Tvv=[op[n] for n in ['Trr','Trv','Tvr','Tvv']]
    xr,xv,sr,sv=[op[n] for n in ['xr','xv','sr','sv']]
    W,den=solve_virtual(Tvv,Tvr.T);v,den2=solve_virtual(Tvv,sv)
    M=Trr-Trv@W;seff=sr-Trv@v;eig=np.linalg.eigvals(M)
    rr=Trr@xr+Trv@xv-sr;vr=Tvr.T@xr+tv_product(Tvv,xv)-sv
    rg=np.abs(Trr)@np.abs(xr)+np.abs(Trv)@np.abs(xv)+np.abs(sr)
    vg=np.abs(Tvr.T)@np.abs(xr)+Tvv[0]*np.abs(xv)+np.abs(Tvv[1])*np.r_[0.,np.abs(xv[:-1])]+np.abs(Tvv[2])*np.r_[np.abs(xv[1:]),0.]+np.abs(sv)
    sr_req=Trr@xr+Trv@xv;A=np.array(op['rates']['Alpha']);DA=np.array(op['rates']['DAlpha'])
    xe=((sr_req-op['line_source'])/op['nH_cm3']-op['saha_s']*op['x1s']*DA+A*op['saha_s']*op['x1s'])/(A*op['xHII'])
    q=op['Wien_shift_q'];qv=op['x1s']*np.exp(-twog[:,0]/op['TR'])
    shift_r=Trr@q+Trv@qv;shift_v=Tvr.T@q+tv_product(Tvv,qv)
    chan=np.array(list(op['channels'].values()));rowsum=chan.sum(axis=0)
    op.update(dict(W=W,v=v,M=M,s_eff=seff,Thomas_denominators=den,reduced_eigenvalues=eig.real,
      reduced_eigenvalue_imaginary=eig.imag,reduced_offdiagonal_arithmetic_tolerance=64*np.finfo(float).eps*float(np.max(np.abs(M))),
      real_row_residual=rr,real_row_gross=rg,real_row_gross_relative=np.abs(rr)/rg,
      virtual_row_residual=vr,virtual_row_gross=vg,virtual_row_gross_relative=np.abs(vr)/vg,
      source_required_sr=sr_req,xe_independent_rows=xe,xe_row_relative=np.abs(xe-op['xe'])/op['xe'],
      channel_additive_sum=rowsum,channel_sum_vs_source_row_residual=rowsum+rr,channel_gross_terms=np.abs(chan),
      virtual_Wien_shift=qv,absolute_source_shift_real=shift_r,absolute_source_shift_virtual=shift_v,
      absolute_source_real=sr+shift_r,absolute_source_virtual=sv+shift_v,
      energy=moments(op,rates,c,nH_reference)))
    ix=knot['index'];check(f'{ix}: real row residual',np.all(np.abs(rr)/rg<=5e-8),np.abs(rr)/rg,5e-8,'sum absolute row operands')
    check(f'{ix}: virtual row residual',np.all(np.abs(vr)/vg<=5e-8),float(np.max(np.abs(vr)/vg)),5e-8,'sum absolute row operands')
    check(f'{ix}: independent xe rows',np.all(op['xe_row_relative']<=5e-8),op['xe_row_relative'],5e-8,'own source H-only xe')
    check(f'{ix}: positive Thomas denominators',np.all(den>0) and np.all(den2>0),float(np.min(den)),0)
    check(f'{ix}: reduced eigenvalues positive real',np.all(eig.real>0) and np.all(eig.imag==0),[eig.real,eig.imag],0)
    off=[float(M[0,1]),float(M[1,0])];tol=op['reduced_offdiagonal_arithmetic_tolerance']
    check(f'{ix}: reduced offdiagonal nonpositive',max(off)<=tol,off,tol,'64eps maxabs M arithmetic only')
    check(f'{ix}: channel decomposition arithmetic',np.all(np.abs(rowsum+rr)<=64*np.finfo(float).eps*rg),rowsum+rr,64*np.finfo(float).eps,'real row gross')
    e=op['energy'];check(f'{ix}: positive finite energy moments',np.all(np.isfinite(e['Krec_eV'])) and np.all(np.isfinite(e['Kion_eV'])) and np.all(e['Krec_eV']>0) and np.all(e['Kion_eV']>0),[e['Krec_eV'],e['Kion_eV']],0)
    for level in range(2):
        for side,key,derkey in [('recombination','Krec_eV','derivative_at_Tm'),('ionization','Kion_eV','derivative_at_TR')]:
            ref=e['reference70'][level][side];errs=dict(derivative=rel(e[derkey][level],float(ref['dlogAlpha_dTm'])),moment=rel(e[key][level],float(ref['K_eV'])))
            check(f'{ix}: level{level} {side} independent70 partial/moment',all(v is not None and v<=2e-10 for v in errs.values()),errs,2e-10,'own nonzero quantity')
    check(f'{ix}: energy sum zero',np.all(e['sum_zero_gross_relative']<=5e-14),e['sum_zero_gross_relative'],5e-14,'sum of six absolute gross energy terms')
    return op

def read_holdout(expected_sha):
    raw=(ROOT/'inputs/validation_only/RIGHT_NATIVE_SNAPSHOT_5127.csv').read_bytes();identity(raw,expected_sha)
    snap=dict(META={},REAL=np.zeros((2,5)),TRR=np.zeros((2,2)),TRV=np.zeros((2,311)),TVR=np.zeros((2,311)),TVV=np.zeros((3,311)),VIRTUAL=np.zeros((311,13)))
    for row in csv.reader(io.StringIO(raw.decode())):
        tag=row[0]
        if tag=='META':snap[tag][row[1]]=float(row[2])
        elif tag=='REAL':snap[tag][int(row[1])]=list(map(float,row[2:]))
        elif tag=='VIRTUAL':snap[tag][int(row[1])]=list(map(float,row[2:]))
        elif tag in ['TRR','TRV','TVR','TVV']:snap[tag][int(row[1]),int(row[2])]=float(row[3])
        else:raise ValueError('unknown holdout record '+tag)
    return snap

def parity(name,actual,expected):
    a=np.asarray(actual);e=np.asarray(expected);mask=e!=0
    structural=np.all(a[~mask]==0);relative=np.zeros(a.shape);relative[mask]=np.abs(a[mask]-e[mask])/np.abs(e[mask])
    maximum=float(np.max(relative)) if relative.size else 0.
    check('right holdout '+name,structural and maximum<=5e-8,dict(max_entry_relative=maximum,structural_zeros_exact=bool(structural)),5e-8,'each own nonzero entry; expected structural zeros exact')
    return dict(max_entry_relative=maximum,structural_zeros_exact=bool(structural),entry_relative=relative)

def main():
    raw=(ROOT/'inputs/NATIVE_QSS_STORED_INPUT_5126_5127.json').read_bytes();identity(raw,PACKET_SHA)
    identity((ROOT/'CODING_CONTRACT_PHASE_A.md').read_bytes(),CONTRACT_SHA)
    packet=json.loads(raw)
    for name,meta in packet['native_source_members'].items():identity((SOURCE/name).read_bytes(),meta['sha256'])
    RESULT['input_identity']=dict(packet_sha256=PACKET_SHA,contract_sha256=CONTRACT_SHA,native_source_members=packet['native_source_members'],source_commit=packet['source_commit'])
    check('exact frozen packet/contract/native source identities',True)
    for r in [.5,1.,-.1]:expect_value_error('invalid ratio rejected '+str(r),lambda r=r:solve_ratio(r))
    expect_value_error('input identity bad bytes rejected',lambda:identity(raw+b' ',PACKET_SHA))
    expect_value_error('negative diffusion coefficient rejected',lambda:validate_diffusion([0.,-.1],[0.,0.]))
    synthetic=synthetic_control();RESULT['synthetic_Maxwellian']=synthetic
    check('synthetic fixed TR Maxwellian known moment',synthetic['relative_error']<=2e-10,synthetic['relative_error'],2e-10)
    check('wrong diagonal derivative direction detected',synthetic['wrong_direction_detected'],synthetic['wrong_diagonal_moment_eV'])
    check('physical radii null input and output',all(v is None for v in packet['physical_radii'].values()) and all(v is None for v in RESULT['physical_radii'].values()))
    c=constants();rates=Rates(c);twog,norm=read_twog(c);RESULT['source_constants']=c;RESULT['two_photon_normalization']=norm
    tube=json.loads((ROOT/'inputs/reused_incoming_tube/TUBE_RESULT.json').read_text());nhref=tube['nH_reference_m3']
    for knot in packet['knots']:
        RESULT['diffusion_inversions'].extend([reconstruct(knot,b,twog,c) for b in [100,179]]);save()
    for knot in packet['knots']:
        inv=[x for x in RESULT['diffusion_inversions'] if x['index']==knot['index']]
        for x in inv:
            check(f"{x['index']} b{x['bin']}: binary64 vs independent70",all(v<=2e-10 for v in x['relative_to_reference70'].values()),x['relative_to_reference70'],2e-10,'own nonzero tau and Tm')
        steady=steady_tm(knot,c,packet);RESULT.setdefault('source_steady_temperature',[]).append(dict(index=knot['index'],**steady))
        err=rel(inv[1]['Tm_eV'],inv[0]['Tm_eV']);require(f"{knot['index']}: two diffusion Tm agreement",err<=2e-8,err,2e-8,'primary b100 Tm')
        for x in inv:
            err=rel(x['Tm_eV'],steady['Tm_eV']);require(f"{knot['index']} b{x['bin']}: trace Tm agrees source Tmss",err<=2e-8,err,2e-8,'source Tmss')
        require(f"{knot['index']}: local steady guard",0<=steady['local_guard_deficit']<steady['guard_limit'],steady['local_guard_deficit'],steady['guard_limit'])
        op=endpoint(knot,steady['Tm_eV'],twog,c,rates,nhref);op['coefficient_Tm_owner']='source history.c::rec_Tmss after two new trace qualifications'
        RESULT['endpoints'].append(op);save()
    RESULT['status']='CONSTRUCTED_BEFORE_HOLDOUT';save()
    # Deliberate validation boundary: no snapshot data have been read above.
    snap=read_holdout(packet['validation_only_snapshot']['identity']['sha256']);op=RESULT['endpoints'][1];iv=[x for x in RESULT['diffusion_inversions'] if x['index']==5127]
    ht=snap['META']['TM_eV_rescaled'];err=rel(iv[0]['Tm_eV'],ht)
    check('right primary diffusion Tm holdout',err<=2e-8,err,2e-8,'own heldout Tm')
    RESULT['right_temperature_holdout']=dict(Tm_eV=ht,primary_relative=err,
      source_Tmss_relative=rel(op['Tm'],ht),assumed_interval_covers=[x['assumed_roundoff']['Tm_interval'][0]<=ht<=x['assumed_roundoff']['Tm_interval'][1] for x in iv],
      interval_coverage_is_separate_diagnostic=True)
    h={};h['Alpha']=parity('Alpha',op['rates']['Alpha'],snap['REAL'][:,2]);h['Beta']=parity('Beta',op['rates']['Beta'],snap['REAL'][:,4])
    h['DAlpha']=parity('DAlpha',op['rates']['DAlpha'],snap['REAL'][:,3]);h['R2p2s']=parity('R2p2s',[op['rates']['R2p2s']],[-snap['TRR'][0,1]])
    for n,tag in [('Trr','TRR'),('Trv','TRV'),('Tvr','TVR'),('Tvv','TVV')]:h[n]=parity(n,op[n],snap[tag])
    h['sr']=parity('sr',op['sr'],snap['REAL'][:,1])
    for n,col in [('sv',7),('Gamma',11),('Dtau',5),('xv',6),('Aup',9),('Adn',10),('one_minus_P',12)]:h[n]=parity(n,op[n],snap['VIRTUAL'][:,col])
    for n,field in [('A2p_up','A2p_up_sInv'),('A2p_dn','A2p_dn_sInv')]:h[n]=parity(n,[op[n]],[snap['META'][field]])
    h['xr']=parity('xr',op['xr'],snap['REAL'][:,0]);RESULT['right_holdout_parity']=h
    RESULT['status']='NUMERICAL_CHECKS_PASS_AWAITING_ROOT_REVIEW' if all(x['passed'] for x in CHECKS) else 'FAILED_CHECKS_PRESERVED_RETURN_TO_ROOT'
    save();return 0 if all(x['passed'] for x in CHECKS) else 2

if __name__=='__main__':
    try:code=main()
    except Exception as exc:
        RESULT['status']='EXCEPTION_PARTIAL_RESULTS_PRESERVED_RETURN_TO_ROOT';RESULT['exception']=dict(type=type(exc).__name__,message=str(exc));traceback.print_exc();save();code=2
    sys.exit(code)
