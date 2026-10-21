#!/usr/bin/env python3
"""Independent S12 stored-output review; no BASS modules or solver imported.

Uses Q=A+(B-A)mu^2 and direct parameter differential, distinct implementation
from Rust's memory-kernel decomposition. No new physics integration or weights.
"""
import argparse,cmath,hashlib,json,math,statistics,struct,time
from fractions import Fraction as F
from pathlib import Path

SOURCE='f4cd0d53760783e6a58c3b0a98c64311ca489d28'
VALIDATION='4e3615dd75ff1a1efc2792edb3ba5b702a8a9b06'
OWNER='0e25846433170d0f420c4cda44a0bedbf02cd177'
VIGIL='a21d573980f66fe02891bd216153443b5352f921'
EPS=F(3,10**15)
checks=[];inputs={};metrics={}

def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
    raw=p.read_bytes();inputs[str(p)]={'bytes':len(raw),'sha256':sha(raw)}
    return json.loads(raw)
def check(name,ok,**detail):checks.append({'name':name,'pass':bool(ok),**detail})
def flat(x):
    if isinstance(x,(tuple,list)):
        return [z for a in x for z in flat(a)]
    return [x]
def scaled(a,b):
    x,y=flat(a),flat(b)
    if len(x)!=len(y) or not x:raise ValueError('ARRAY_SHAPE')
    if not all(math.isfinite(float(z)) for z in x+y):raise ValueError('NONFINITE')
    return max(abs(v-w)/(1+max(abs(v),abs(w))) for v,w in zip(x,y))
def difference(a,b):return max(abs(x-y) for x,y in zip(flat(a),flat(b)))
def gate(name,v,g,**detail):check(name,math.isfinite(v) and 0<=v<=g,value=v,gate=g,**detail)
def moment_exact(p):
    A=[F(a) for a in p['alpha']];Z=[F(m)**2 for m in p['mu']]
    return [sum(A)-1,sum(a*(3*z-1)/2 for a,z in zip(A,Z)),sum(a*(35*z*z-30*z+3)/8 for a,z in zip(A,Z))]
def physical_sha(p):
    v=[p['u'],p['b_birth'],p['energy_birth'],*p['mu'],*p['alpha']]
    return sha(b''.join(struct.pack('<d',float(x)) for x in v)+p['role'].encode())
def memory_sha(c):
    v=[c['birth_b_theta'],c['memory_theta'],*c['mu_b'],*c['alpha_b'],*c['mu_theta'],*c['alpha_theta']]
    return sha(c['physical_sha256'].encode()+b''.join(struct.pack('<d',float(x)) for x in v))
def csum(a):return complex(math.fsum(z.real for z in a),math.fsum(z.imag for z in a))

def moments(x,b,B,cohorts):
    # Q is squared photon redshift. T=3*B_axis*mu^2-Q is twice pressure numerator.
    total=[[] for _ in range(4)]
    for c in cohorts:
        p=c.get('physical',c);d=b-p['b_birth'];delta=B-c['memory_theta']
        A=cmath.exp(2*d);Baxis=cmath.exp(-4*d);s=[[] for _ in range(4)]
        for m,a,mt,at in zip(p['mu'],p['alpha'],c['mu_theta'],c['alpha_theta']):
            z=m*m;Q=A+(Baxis-A)*z;r=cmath.sqrt(Q);T=3*Baxis*z-Q
            qt=2*(A*(1-z)-2*Baxis*z)*delta+2*(Baxis-A)*m*mt
            tt=3*(-4*Baxis*z*delta+2*Baxis*m*mt)-qt
            vals=[a*r,a*T/(2*r),at*r+a*qt/(2*r),at*T/(2*r)+a*(tt/(2*r)-T*qt/(4*r**3))]
            for group,val in zip(s,vals):group.append(complex(val))
        fac=p['energy_birth']*cmath.exp(-4*(x-p['u']))
        for group,part in zip(total,s):group.append(fac*csum(part))
    return [csum(v) for v in total]

def rhs(x,state,bank):
    h,b,y,H,B,Y=state
    E,P,Et,Pt=moments(x,b,B,bank['cohorts'])
    Ed=bank['donor0']*cmath.exp(-3*x-bank['decay_lambda']*bank['exposure'])
    L=bank['cosmological_constant']
    A=-h*h-2*y*y-Ed/2-E+L
    return [A/h,y/h,-3*y+P/h,
        (-2*h*H-4*y*Y-Et)/h-A*H/h**2,
        Y/h-y*H/h**2,-3*Y+Pt/h-P*H/h**2], [E,P,Et,Pt,Ed]

def core_parse(p,mode,count):
    raw=p.read_bytes();inputs[str(p)]={'bytes':len(raw),'sha256':sha(raw)}
    lines=raw.decode().splitlines();assert lines[:3]==['BASS_S12_CORE_OUTPUT_V1','MODE '+mode,'ROWS '+str(count)]
    out=[];j=3
    for i in range(count):
        assert lines[j]=='ROW '+str(i);j+=1;row={}
        for key,n in [('RHS',6),('JVP',6),('PT',6),('JAC',36),('MOMENTS',10)]:
            a=lines[j].split();j+=1;assert a[0]==key and len(a)==n+1
            row[key]=[float(v) for v in a[1:]];assert all(map(math.isfinite,row[key]))
        out.append(row)
    assert j==len(lines);return out

def stored_core(c):
    report=read(c/'RETURN.json');data=read(c/'FIXED_INPUT.json');perf=read(c/'PERFORMANCE.json')
    check('core_registered_summary',report['source_commit']==SOURCE and report['status']=='PASS_SCOPED'
          and report['passed']==report['check_count']==269 and len(report['checks'])==269
          and all(v['pass'] for v in report['checks']))
    bank=data['bank'];queries=data['queries'];assert len(queries)==24
    a=core_parse(c/'diagnostic_baseline.stdout','baseline',24);b=core_parse(c/'diagnostic_fused.stdout','fused',24)
    errors={k:0. for k in ('RHS','JAC','JVP','PT','moments','baseline_fused')};e=1e-27
    for i,q in enumerate(queries):
        s=q['state'];x=q['x'];vec,mm=rhs(x,s,bank);J=[[0.]*6 for _ in range(6)]
        for j in range(6):
            sc=[complex(z,0.) for z in s];sc[j]+=complex(0,e)
            v,_=rhs(x,sc,bank)
            for k in range(6):J[k][j]=v[k].imag/e
        jt=rhs(complex(x,e),s,bank)[0]
        expected={'RHS':[z.real for z in vec],'JAC':flat(J),
            'JVP':[sum(J[k][j]*q['direction'][j] for j in range(6)) for k in range(6)],
            'PT':[z.imag/e for z in jt]}
        for key,value in expected.items():
            err=scaled(b[i][key],value);errors[key]=max(errors[key],err);gate(f'core_{i}_{key}',err,2e-11)
        err=scaled([b[i]['MOMENTS'][j] for j in (0,1,8,9,7)],[v.real for v in mm])
        errors['moments']=max(errors['moments'],err);gate(f'core_{i}_moment_direct',err,2e-11)
        err=max(scaled(a[i][k],b[i][k]) for k in a[i]);errors['baseline_fused']=max(errors['baseline_fused'],err)
        gate(f'core_{i}_baseline_fused',err,2e-13)
    # Each benchmark output is independently parsed and compared with its own diagnostic.
    paired=[]
    for row in perf['all_pairs']:
        for mode,expected in [('baseline',a),('fused',b)]:
            obs=core_parse(c/f"bench_{row['pair']:02d}_{mode}.stdout",mode,24)
            check(f"benchmark_{row['pair']}_{mode}_exact",obs==expected)
            timing=read(c/f"bench_{row['pair']:02d}_{mode}.stderr")
            check(f"benchmark_{row['pair']}_{mode}_workload",timing==row[mode]
                and timing['timed_evaluations']==48000 and timing['repeat']==2000 and timing['elapsed_ns']>0)
        ratio=row['baseline']['elapsed_ns']/row['fused']['elapsed_ns']
        check(f"benchmark_{row['pair']}_ratio",ratio==row['speedup'])
        if not row['warmup']:paired.append(ratio)
    check('benchmark_median',len(paired)==7 and statistics.median(paired)==perf['paired_speedup_median'])
    metrics['core_direct_max_scaled']=errors;metrics['fixed_workload_paired_median']=statistics.median(paired)
    metrics['performance_scope']='New24point48ray fixed augmented callback workload only; no whole-history or NCP64 speedup.'


def output_states(receipt,times):
    by={v['x']:v['state'] for v in receipt['observations']}
    return [by[x] for x in times]

def stored_history(h):
    summary=read(h/'SUMMARY.json');identity=read(h/'RUN_IDENTITY.json');cross=read(h/'CROSS_IMPLEMENTATION.json')
    check('history_summary',summary['status']=='PASS_SCOPED' and summary['checks_passed']==summary['checks_total']==72
          and summary['source_commit']==SOURCE and summary['validation_source_commit']==VALIDATION
          and summary['process_records']==16 and summary['reused_completed_histories']==5 and summary['new_process_attempts']==11)
    registered=read(h/'CHECKS.json');check('history_actual_72_checks',len(registered)==72 and all(v['pass'] for v in registered))
    names=['p24_y0_full','gl_y0_full','gl_b0_gauge','p24_y0_mf6','p24_y0_baseline',
        'fd_1p0em04_plus','fd_1p0em04_minus','fd_5p0em05_plus','fd_5p0em05_minus','fd_2p5em05_plus','fd_2p5em05_minus',
        'omit_birth_memory','omit_mu_b','omit_alpha_b']
    receipts={};allmax={'C':0.,'Ct':0.,'readback':0.,'energy_law':0.,'tangent_energy_law':0.,'Ct_propagation':0.,'fresh_exact':0.,'event_energy':0.,'event_Et':0.,'event_Pt_full':0.}
    for name in names:
        rec=read(h/(name+'.stdout'));inp=read(h/(name+'.input.json'));assess=read(h/(name+'.assessment.json'))
        receipts[name]=rec;cfg=inp['config'];old_n=len(inp['initial_cohorts']);cohorts=rec['final_cohorts'];full=inp['control']=='full'
        check(name+'_binding',rec['status']=='completed' and rec['failure'] is None and rec['binding']['source_commit']==SOURCE
            and rec['binding']['input_sha256']==inputs[str(h/(name+'.input.json'))]['sha256']
            and rec['binding']['binary_sha256']==identity['binary_sha256'] and rec['input']==inp
            and rec['spectral_owner']==OWNER and rec['vigilode_source']==VIGIL)
        check(name+'_assessment_scope',assess['full_scientific_pass']==full and assess['numerical_gates_pass']==full)
        check(name+'_old_stock_preserved',all(cohorts[i]['physical']==inp['initial_cohorts'][i] for i in range(old_n)))
        check(name+'_all_physical_memory_digests',all(physical_sha(c['physical'])==c['physical_sha256'] and memory_sha(c)==c['memory_sha256'] for c in cohorts))
        check(name+'_all_physical_weights_positive_parity',all(all(a>0 for a in c['physical']['alpha'])
            and c['physical']['alpha']==c['physical']['alpha'][::-1]
            and c['physical']['mu']==[-v for v in c['physical']['mu'][::-1]] for c in cohorts))
        for j,c in enumerate(cohorts[old_n:]):
            r=moment_exact(c['physical']);v=max(abs(z) for z in r);allmax['fresh_exact']=max(allmax['fresh_exact'],float(v))
            check(name+f'_birth{j}_exact_gate',v<=EPS,residuals=list(map(str,r)))
            event=rec['events'][j];p=c['physical'];B=event['state'][4]
            expected_mu=[0. if inp['control']=='omit_mu_b' else z*B for z in c['mu_b']]
            expected_alpha=[0. if inp['control']=='omit_alpha_b' else z*B for z in c['alpha_b']]
            check(name+f'_birth{j}_frozen_memory',p['u']==(j+.5)*cfg['birth_end']/cfg['k']
                and p['b_birth']==event['state'][1] and c['birth_b_theta']==B
                and c['memory_theta']==(0. if inp['control']=='omit_birth_memory' else B)
                and c['mu_theta']==expected_mu and c['alpha_theta']==expected_alpha)
        du=cfg['birth_end']/cfg['k'];times=[v['physical']['u'] for v in cohorts[old_n:]]
        local={k:0. for k in ('C','Ct','readback','energy_law','tangent_energy_law','Ct_propagation')}
        for obs in rec['observations']:
            x=obs['x'];state=obs['state'];n=sum(u<=x for u in times)
            bank={**cfg,'exposure':n*du,'cohorts':cohorts[:old_n+n]}
            rr,mm=rhs(x,state,bank);rr=[z.real for z in rr];E,P,Et,Pt,Ed=[z.real for z in mm]
            H,b,y,St,B,Y=state;C=H*H-y*y-Ed-E-cfg['cosmological_constant'];Ct=2*H*St-2*y*Y-Et
            den=H*H+y*y+Ed+E+cfg['cosmological_constant'];assert den>0 and math.isfinite(den)
            local['C']=max(local['C'],abs(C)/den);local['Ct']=max(local['Ct'],abs(Ct)/den)
            target=[E,P,Et,Pt,Ed,C,Ct];actual=[obs[v] for v in ('e_radiation','pi','e_theta','pi_theta','e_donor','c','c_theta')]
            local['readback']=max(local['readback'],scaled(actual,target))
            eps=1e-27;Et_prime=0.
            for cohort in bank['cohorts']:
                m=moments(complex(x,eps),complex(b,eps*rr[1]),complex(B,eps*rr[4]),[cohort])
                ec,pc,etc,ptc=[z.real for z in m];ep,etp=m[0].imag/eps,m[2].imag/eps
                Et_prime+=etp
                local['energy_law']=max(local['energy_law'],abs(ep+4*ec+2*rr[1]*pc)/max(abs(ec),1e-30))
                local['tangent_energy_law']=max(local['tangent_energy_law'],abs(etp+4*etc+2*(rr[1]*ptc+rr[4]*pc))/max(abs(ec),abs(etc),1e-30))
            Ctp=2*rr[0]*St+2*H*rr[3]-2*rr[2]*Y-2*y*rr[5]-Et_prime
            local['Ct_propagation']=max(local['Ct_propagation'],abs(Ctp+2*Ct)/den)
        for key,val in local.items():
            # Omission histories still satisfy between-event algebra/energy identities;
            # their failed event tangent jump must not become a full-history PASS.
            gate(name+'_independent_'+key,val,1e-11)
            allmax[key]=max(allmax[key],val)
        event_max={'energy':0.,'Et':0.,'Pt':0.}
        for j,event in enumerate(rec['events']):
            before_bank={**cfg,'exposure':j*du,'cohorts':cohorts[:old_n+j]}
            after_bank={**cfg,'exposure':(j+1)*du,'cohorts':cohorts[:old_n+j+1]}
            mb=rhs(event['u'],event['state'],before_bank)[1];ma=rhs(event['u'],event['state'],after_bank)[1]
            mb=[z.real for z in mb];ma=[z.real for z in ma];den=mb[0]+mb[4];assert den>0
            jumps={'energy':(ma[0]+ma[4]-mb[0]-mb[4])/den,'Et':(ma[2]-mb[2])/den,'Pt':(ma[3]-mb[3])/den}
            for key,val in jumps.items():event_max[key]=max(event_max[key],abs(val))
        gate(name+'_event_energy',event_max['energy'],1e-11);gate(name+'_event_Et',event_max['Et'],1e-11)
        if full:gate(name+'_event_Pt',event_max['Pt'],1e-11);allmax['event_Pt_full']=max(allmax['event_Pt_full'],event_max['Pt'])
        else:check(name+'_expected_event_Pt_failure_retained',event_max['Pt']>1e-11 and not assess['full_scientific_pass'],event_Pt=event_max['Pt'])
        allmax['event_energy']=max(allmax['event_energy'],event_max['energy']);allmax['event_Et']=max(allmax['event_Et'],event_max['Et'])
    base=receipts['p24_y0_full'];times=base['input']['output_times'];states=output_states(base,times)
    py=read(h/'PYTHON_REFERENCE.json');py_by_time={v['x']:v['state'] for v in py['state_rows']};py_states=[py_by_time[x] for x in times]
    comparisons={'Python_Rust_scaled':scaled(states,py_states),'MF6_clock7_scaled':scaled(states,output_states(receipts['p24_y0_mf6'],times)),
        'baseline_fused_scaled':scaled(states,output_states(receipts['p24_y0_baseline'],times))}
    for key,val in comparisons.items():gate('ensemble_'+key,val,1e-10);check('ensemble_record_'+key,val==cross[key])
    gauge=output_states(receipts['gl_b0_gauge'],times)
    gv=max(abs(x) for s in gauge for x in (s[3],s[4]-1,s[5]));gate('source_frame_gauge_absolute',gv,1e-11)
    fd=read(h/'FD_RICHARDSON.json');d=[]
    for tag,step in [('1p0em04',1e-4),('5p0em05',5e-5),('2p5em05',2.5e-5)]:
        plus=output_states(receipts['fd_'+tag+'_plus'],times);minus=output_states(receipts['fd_'+tag+'_minus'],times)
        d.append([[(a-b)/(2*step) for a,b in zip(p[:3],m[:3])] for p,m in zip(plus,minus)])
    fine=[[(4*f-c)/3 for f,c in zip(fr,cr)] for fr,cr in zip(d[2],d[1])]
    tangent=[s[3:] for s in states];err=difference(fine,tangent)
    gate('Richardson_absolute',err,1e-8);check('Richardson_stored_readback',d==fd['raw_centered_derivatives'] and fine==fd['fine_Richardson'] and err==fd['fine_Richardson_max_absolute'])
    omission=read(h/'OMISSION_CONTROLS.json');om=[]
    for item in omission:
        actual=[s[3:] for s in output_states(receipts[item['control']],times)];gap=difference(actual,fine)
        check(item['control']+'_Richardson_identified',gap>10*err and gap==item['omitted_vs_Richardson_max_absolute']
            and item['required_strict_lower_bound']==10*err and item['full_scientific_pass'] is False)
        om.append({'control':item['control'],'gap':gap,'required_lower_bound':10*err})
    reused=read(h/'REUSED_PREFIX.json');check('five_reused_no_rerun',len(reused['records'])==5 and all(x['execution_performed'] is False for x in reused['records']) and reused['original_failed_python_reused'] is False and reused['fallback_rerun_allowed'] is False)
    restore=read(h/'final_checkpoint_resume.stdout');check('final_restore_identity',restore['observations']==base['observations'] and restore['events']==base['events'] and restore['final_cohorts']==base['final_cohorts'] and restore['resumed'] is True)
    metrics.update(history_direct_max=allmax,cross_implementation=comparisons,Richardson_max_absolute=err,omission_controls=om,gauge_absolute=gv,
        primary_input_sha256=inputs[str(h/'p24_y0_full.input.json')]['sha256'],primary_raw_sha256=inputs[str(h/'p24_y0_full.stdout')]['sha256'])



def stored_parallel(p):
    binding=read(p/'BINDING.json');process=read(p/'PROCESS.json');base=p/'bench';report=read(base/'RETURN.json');pairs=read(base/'PAIRS.json')
    check('case_parallel_bound_scoped',binding['scientific_source_commit']==SOURCE and binding['input_full_readback'] is True
        and process['exit_code']==0 and report['status']=='PASS_EXECUTION_IDENTITY' and report['profile']=='sandbox'
        and report['requested_workers']==2 and report['cases']==4 and report['repeat']==128
        and report['warmup_pairs']==1 and report['measured_pairs']==3 and report['ray_cohort_reduction_order_changed'] is False)
    allout={};insha={};count=0;ratios=[]
    for row in pairs:
        for arm in ['serial','parallel']:
            for case in range(4):
                d=base/f"pair{row['pair']:02d}_{arm}"/f'case{case:02d}'
                parsed=core_parse(d/'stdout.txt','fused',24);raw=(d/'stdout.txt').read_bytes();proc=read(d/'PROCESS.json');timing=read(d/'stderr.json')
                inp=(d/'input.txt').read_bytes();sig=sha(inp);inputs[str(d/'input.txt')]={'bytes':len(inp),'sha256':sig}
                check(f"parallel_{row['pair']}_{arm}_{case}_raw",proc['status']=='EXITED' and proc['exit_code']==0
                    and proc['stdout_sha256']==sha(raw) and proc['stderr_sha256']==inputs[str(d/'stderr.json')]['sha256']
                    and proc['input_sha256']==sig and proc['binary_sha256']==report['binary_sha256']
                    and timing['repeat']==128 and timing['timed_evaluations']==3072)
                if case not in allout:allout[case]=raw;insha[case]=sig
                check(f"parallel_{row['pair']}_{arm}_{case}_identity",raw==allout[case] and sig==insha[case]);count+=1
        ratio=row['serial']['wall_s']/row['parallel']['wall_s'];check(f"parallel_pair{row['pair']}_ratio",ratio==row['speedup'])
        if not row['warmup']:ratios.append(ratio)
    check('parallel_median',count==32 and len(ratios)==3 and statistics.median(ratios)==report['speedup_median'])
    metrics['case_parallel']={'stdout_identity_count':count,'cases':4,'workers':2,'paired_samples':3,'median':statistics.median(ratios),
        'scope':'Sandbox fixed whole-case batch only; not actual NCP64 speedup.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--core',type=Path,required=True);p.add_argument('--history',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--parallel',type=Path,required=True);a=p.parse_args()
    start=time.time();failure=None
    try:stored_core(a.core);stored_history(a.history);stored_parallel(a.parallel)
    except Exception as exc:failure={'type':type(exc).__name__,'message':str(exc)}
    result={'schema':'BASS_S12_INDEPENDENT_STORED_PHYSICS_REVIEW_V1','reviewer':'p6_theory','status':'PASS_SCOPED' if failure is None and checks and all(v['pass'] for v in checks) else 'FAIL',
        'reviewed_core_and_Rust_source':SOURCE,'reviewed_reference_validation_source':VALIDATION,'review_source_sha256':sha(Path(__file__).read_bytes()),
        'checks_passed':sum(v['pass'] for v in checks),'checks_total':len(checks),'checks':checks,'metrics':metrics,'failure':failure,
        'inputs':inputs,'elapsed_seconds':time.time()-start,'solver_calls':0,'compiler_calls':0,'projector_calls':0,'old_campaign_calls':0,
        'independence':'Reviewer authored S12 theory/native followup wrapper, not Rust core/history/birth, root reference, or assessor. This review excludes own native wrapper and support observer from independent approval.',
        'limits':['Short manufactured scalar histories only.','No native MD14/shared-Q/full spectral/full EoR result.','Fixed-workload callback speedup does not imply whole-history/NCP64 speedup.','Core complex-step differentiates new direct Q-based scalar expressions; it is not a new history solver run.','Final checkpoint restore is the final boundary only, not interrupted mid-event recovery.']}
    a.out.mkdir(parents=True,exist_ok=False);(a.out/'REVIEW.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('status','checks_passed','checks_total','failure','elapsed_seconds')}))
    return int(result['status']!='PASS_SCOPED')
if __name__=='__main__':raise SystemExit(main())
