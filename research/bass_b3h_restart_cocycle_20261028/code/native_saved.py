"""Read two already-computed native panels; never import the old solver."""
from __future__ import annotations
import gzip, hashlib, json
from pathlib import Path
import mpmath as mp

EXPECTED='acf56f5aefe556d1d86e4f93f3063c5d38078cb8c7f9a627b141c4ef9582f3bd'

def read_locked(path: Path, expected: str) -> dict:
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError('secondary source SHA mismatch: '+path.name)
    return json.loads(raw)

def _v(value):
    return [mp.mpf(x[0] if isinstance(x,list) else x) for x in value]

def _fmt(value):
    if isinstance(value,dict): return {str(k):_fmt(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [_fmt(v) for v in value]
    if isinstance(value,mp.mpf): return mp.nstr(value,90)
    return value

def prefix_incoming(clock, packet, e21, ev):
    """One new finite prefix, closed primitive, on the represented incoming PL."""
    h=mp.mpf(clock['h']); lag=mp.mpf(clock['lag'])
    edge=mp.mpf(clock['actual_split_edges'][1]); a=mp.mpf(clock['A'])
    dep=[mp.mpf(float.fromhex(x)) for x in packet['incoming']['departure_hex']]
    knots=[(j-5126)*h+lag for j in packet['incoming']['source_indices']]
    mid=edge/2
    j=next(j for j in range(len(knots)-1) if knots[j]<=mid<=knots[j+1])
    slope=(dep[j+1]-dep[j])/h; d0=dep[j]-slope*knots[j]
    if not (knots[j]<=0 and edge<=knots[j+1]+mp.mpf('1e-70')):
        raise ValueError('prefix crosses an unrepresented incoming segment')
    gross={}
    def integral(k):
        def dep_primitive(u):
            return mp.exp(k*u)*((d0+slope*u)/k-slope/k**2)
        def upper_gamma(x):
            return mp.factorial(k-1)*mp.exp(-x)*sum(x**m/mp.factorial(m) for m in range(k))
        x0=a; x1=a*mp.exp(edge)
        terms=[dep_primitive(edge),-dep_primitive(0),upper_gamma(x0)/a**k,-upper_gamma(x1)/a**k]
        gross[k]=sum(abs(x) for x in terms)
        return sum(terms)
    G=3*10**6*mp.mpf(packet['native_cosmology']['LYA_FACT_cm3_inv'])
    n=G*integral(3); energy=G*e21*ev*integral(4)
    return n,energy,dict(segment=j,occupation_at_zero=d0+mp.exp(-a),
        cancellation_gross_to_result_count=G*gross[3]/abs(n),
        declared_arithmetic_count_allowance=G*gross[3]*mp.mpf('1e-80'),
        declared_arithmetic_energy_allowance=G*e21*ev*gross[4]*mp.mpf('1e-80'))

def study(source: Path, destination: Path) -> dict:
    mp.mp.dps=100
    rawpath=source/'results/ENDPOINT_RESULT.json'
    raw=rawpath.read_bytes() if rawpath.exists() else gzip.decompress(Path(str(rawpath)+'.gz').read_bytes())
    if hashlib.sha256(raw).hexdigest()!=EXPECTED: raise ValueError('native result SHA mismatch')
    x=json.loads(raw); f=x['finite_solution']; owners=x['finite_owners']; clock=x['clock']; maps=x['endpoint_maps']
    packet=read_locked(source/'inputs/reused/FINITE_TUBE_INPUT_SLICE.json','0eb250e965ad3496d00b53d5a165bafc93de8506baa9dad8e04de2bbd3614cdd')
    constants=read_locked(source/'inputs/reused/SOURCE_OPERANDS.json','179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd')['source_constants']
    NH=mp.mpf(f['NH_reference']); T=mp.mpf(f['T_new']); h=mp.mpf(f['h'])
    tc=mp.mpf(f['endpoints'][0]['t_end']); uc=mp.mpf(f['endpoints'][0]['u_end']); theta=tc/T; beta=1-theta
    ev=mp.mpf(packet['native_cosmology']['EV_J']); e21=mp.mpf(constants['E21']); EJ=e21*ev
    F={}; I={}; checks=[]
    def check(name,ok,details=None): checks.append(dict(name=name,passed=bool(ok),details=details))
    check('exactly_two_existing_native_panels',len(f['endpoints'])==2)
    for k in range(3):
        for j in range(2):
            row=f['moments'][f'k{k}_j{j}']; seg=row['segments']
            I[k,j]=[_v(s['value']) for s in seg]
            if k==0:
                F[k,j]=[(mp.mpf(e['t_end'])-mp.mpf(e['t_start'])) if j==0 else
                    (mp.mpf(e['t_end'])**2-mp.mpf(e['t_start'])**2)/(2*T) for e in f['endpoints']]
            else:
                q=[s for s in x['quadrature_and_analytic_bounds'] if s['name']==f'scalar F{k}{j}']
                if len(q)!=2 or any(s['a']!=e['u_start'] or s['b']!=e['u_end'] for s,e in zip(q,f['endpoints'])):
                    raise ValueError('scalar positive quadrature panel mismatch')
                F[k,j]=[mp.mpf(s['gross_scale']) for s in q]
            check(f'F{k}{j}_sum_saved',abs(sum(F[k,j])-mp.mpf(row['F']))<=mp.mpf(row['F_error']))
    delta=[[mp.mpf(0) for _ in range(4)] for _ in range(2)]
    q=[[[mp.mpf(0) for _ in range(4)] for _ in range(3)] for _ in range(2)]
    count_rows=[]; max_ratio=mp.mpf(0); minimum=None; worst_clock=mp.mpf(0)
    saved={(r['name'],r['endpoint_tag']):r for r in owners['tagged_channel_counts']}
    for tag,label in enumerate(['left','right']):
        for ch in maps[label]:
            aa=mp.mpf(ch['a']); ell=_v(ch['ell']); ee=_v(ch['energy_eV']); nu=ch['stoich']
            out=[]
            for k in range(3):
                counts=[]
                for panel in range(2):
                    ff=F[k,1][panel] if tag else F[k,0][panel]-F[k,1][panel]
                    ii=I[k,1][panel] if tag else [a-b for a,b in zip(I[k,0][panel],I[k,1][panel])]
                    val=NH*(aa*ff+sum(a*b for a,b in zip(ell,ii)))
                    counts.append(val);minimum=val if minimum is None else min(minimum,val)
                    for s in range(4):
                        q[panel][k][s]+=ee[s]*val*ev
                        if k==0:delta[panel][s]+=nu[s]*val
                sr=saved[ch['name'],tag]
                value=mp.mpf(sr['count'] if k==0 else sr[f'weighted_count_k{k}'])
                err=mp.mpf(sr['count_error'] if k==0 else sr['weighted_count_errors'][str(k)])
                allowed=err+mp.mpf('1e-80')*(sum(abs(v) for v in counts)+abs(value))
                residual=abs(sum(counts)-value)
                ratio=residual/allowed if allowed else (mp.mpf(0) if not residual else mp.inf)
                max_ratio=max(max_ratio,ratio)
                out.append(counts)
                if k==0:
                    lf=(F[0,1][1]-theta*F[0,0][1])/beta
                    li=[(b-theta*a)/beta for a,b in zip(I[0,0][1],I[0,1][1])]
                    bf=lf if tag else F[0,0][1]-lf
                    bi=li if tag else [a-b for a,b in zip(I[0,0][1],li)]
                    bad=NH*(aa*bf+sum(a*b for a,b in zip(ell,bi)))
                    worst_clock=max(worst_clock,abs(bad-counts[1]))
            count_rows.append(dict(name=ch['name'],endpoint_tag=tag,panel_counts_by_k=out))
    check('all_16968_panel_weighted_tag_counts_nonnegative',minimum>=0,minimum)
    check('all_8484_summed_tag_counts_within_inherited_bounds',max_ratio<=1,max_ratio)
    incoming_n,incoming_u,prefixmeta=prefix_incoming(clock,packet,e21,ev)
    nin=mp.mpf(f['Nin_saved']);uin=mp.mpf(f['Uin_saved'])
    up=[incoming_n,nin-incoming_n]; uup=[incoming_u,uin-incoming_u]
    down=[NH*_v(s['value'])[0] for s in f['direct_alpha']['k0']['segments']]
    udown=[NH*EJ*_v(s['value'])[0] for s in f['direct_alpha']['k1']['segments']]
    for p in range(2):
        net=down[p]-up[p];delta[p][0]+=net;delta[p][2]-=net
        q[p][0][0]-=EJ*net;q[p][0][3]+=EJ*net
    initial=_v(owners['initial_stocks'])
    cut=[a+b for a,b in zip(initial,delta[0])]
    end=[a+b for a,b in zip(cut,delta[1])]
    stored_end=_v(owners['final_stocks']);stockerrs=_v(owners['conditional_final_stock_errors'])
    stockres=[abs(a-b) for a,b in zip(end,stored_end)]
    check('cut_and_final_atomic_stocks_positive',min(cut+end)>0)
    check('final_stock_reassembly_within_saved_conditional_bounds',all(a<=b for a,b in zip(stockres,stockerrs)),stockres)
    initenergy=_v(owners['initial_sector_energy_J_m3'])
    increments=[[mp.mpf(0),q[p][0][0],q[p][2][1],q[p][1][2],q[p][1][3]+udown[p]-uup[p]] for p in range(2)]
    Zcut=[a+b for a,b in zip(initenergy,increments[0])]
    Zend=[a+b for a,b in zip(Zcut,increments[1])]
    ks=[0,0,2,1,1]
    cutrho=[mp.exp(-(3+k)*uc)*z for k,z in zip(ks,Zcut)]
    endrho=[mp.exp(-(3+k)*h)*z for k,z in zip(ks,Zend)]
    erho=_v(owners['final_sector_energy_J_m3']);ebounds=_v(owners['conditional_propagated_energy_errors'])
    eres=[abs(a-b) for a,b in zip(endrho,erho)]
    check('cut_and_final_sector_energy_positive',min(cutrho+endrho)>0)
    check('five_sector_energy_reassembly_within_saved_conditional_bounds',all(a<=b for a,b in zip(eres,ebounds)),eres)
    pcut=_v(f['endpoints'][0]['p_end'])
    cutdef=[cut[i+1]-NH*pcut[i] for i in range(2)]
    # New source-bound QSS reset size, not a new native ODE trajectory.
    cosm=packet['native_cosmology'];eta=mp.mpf(clock['eta0'])+uc
    H=mp.mpf(cosm['H_prefactor_s_inv'])*mp.sqrt(mp.mpf(cosm['omh2'])*mp.exp(-3*eta)+mp.mpf(cosm['odeh2'])+mp.mpf(cosm['photon_omega_prefactor'])*mp.mpf(cosm['T0_K'])**4*(1+mp.mpf(cosm['neutrino_factor'])*mp.mpf(cosm['Nnueff']))*mp.exp(-4*eta))
    g=mp.mpf(clock['g0'])+(mp.mpf(clock['g1'])-mp.mpf(clock['g0']))*uc/h
    ra=mp.mpf(cosm['LYA_FACT_cm3_inv'])/(NH/mp.mpf(10**6))*H*mp.exp(3*uc)/g
    dep=packet['incoming']['departure_hex']; j=prefixmeta['segment']
    knots=[(i-5126)*h+mp.mpf(clock['lag']) for i in packet['incoming']['source_indices']]
    d=[mp.mpf(float.fromhex(v)) for v in dep]
    fin=d[j]+(d[j+1]-d[j])*(uc-knots[j])/h+mp.exp(-mp.mpf(clock['A'])*mp.exp(uc))
    mm=mp.matrix(maps['M0'])+theta*mp.matrix(maps['delta_M']);mm[1,1]+=ra
    bb=mp.matrix(maps['b0'])+theta*mp.matrix(maps['delta_b']);bb[1]+=3*ra*g*fin
    pq=mp.lu_solve(mm,bb);reset_norm=sum(abs(pq[i]-pcut[i]) for i in range(2))
    gamma=mp.mpf(f['real_bounds']['gamma']); rupper=mp.mpf(f['real_bounds']['Ralpha_upper'])
    reward_bound=NH*rupper*reset_norm/gamma
    data=dict(status='COMPUTED_SCOPED_SAVED_PANEL_COMPANION',source_sha256=EXPECTED,
        cut=dict(t_s=tc,u=uc,theta=theta,p=pcut,atomic_stocks_per_V0=cut,
                 weighted_sector_energy_Z=Zcut,sector_density_J_m3=cutrho,
                 interface_stock_minus_NHp=cutdef,incoming_count_prefix=incoming_n,
                 incoming_weighted_energy_prefix=incoming_u,outgoing_count_prefix=down[0],
                 outgoing_weighted_energy_prefix=udown[0],prefix_primitive=prefixmeta),
        final=dict(atomic_stocks=end,sector_density_J_m3=endrho,stock_residuals=stockres,energy_residuals=eres,
                   Lyalpha_net=sum(down)-nin,Lyalpha_out=sum(down)),
        checks=checks,tag_count_rows=2828,weighted_panel_values=16968,
        max_tag_residual_over_inherited_bound=max_ratio,
        negative_controls=dict(global_theta_reset_reweight_max_tag_count_change=worst_clock,
            dropped_prefix_outgoing_count=down[0],QSS_reset_abundance_one_norm=reset_norm,
            QSS_reset_conditional_future_Lya_count_bound=reward_bound,
            negative_control_scope='reweight stored trajectory and derive same-operator reset bound; no mutated native IVP'),
        source_uncertainty=None,physical_radii={k:None for k in ['eS','en','eE','geometry','temporal','total','global']},
        inherited_incoming_quadrature_remainder=None,L4=False,new_native_ODEs=0,new_B3i_RHS=0,old_quadrature_calls=0,
        prefix_qualification='new represented-profile analytic primitive at MP100; assumed relative arithmetic1e-80; saved input clock/source errors not physical certification')
    destination.mkdir(exist_ok=True,parents=True)
    (destination/'NATIVE_RESTART.json').write_text(json.dumps(_fmt(data),indent=2)+'\n')
    (destination/'NATIVE_PANEL_COUNTS.json').write_text(json.dumps(_fmt(count_rows),separators=(',',':'))+'\n')
    if not all(c['passed'] for c in checks):raise AssertionError('native saved-panel checks failed; saved partial result retained')
    return _fmt(data)
