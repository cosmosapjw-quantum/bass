"""Single new pointwise enclosure campaign; imports no historical solver."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal,localcontext,ROUND_CEILING
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from enclosure import I,solve_intervals
U=Path(__file__).resolve().parents[1]
PIN='5f3cb43a7163df646e03309c65b69ff5d6ae2c13fe2459a5ac31df76c085ef5c'

def display(q):
    with localcontext() as c:
        c.prec=45;c.rounding=ROUND_CEILING
        return str(Decimal(q.numerator)/Decimal(q.denominator))
def fracpack(q):return {'numerator':str(q.numerator),'denominator':str(q.denominator),'decimal_upper':display(q)}

def assemble(source,P,mutation=None):
    z=lambda x:I.point(F(x),P)
    C=source['clock'];co=source['cosmology'];maps=source['maps']
    cv=lambda key:z(F(str(co[key])) if mutation=='decimalize_binary64' else F.from_float(float(co[key])))
    h=z(C['h']);u=z(source['cut']['u']);eta0=z(C['eta0']);NH=z(C['NH_reference'])
    g0=z(C['g0']);g1=z(C['g1']);g=g0+(g1-g0)*u/h
    theta=z(source['cut']['t_s'])/z(source['duration'])
    if mutation=='reset_theta':theta=z(0)
    radiation=cv('photon_omega_prefactor')*cv('T0_K')**4*(1+cv('neutrino_factor')*cv('Nnueff'))
    def H(at):
        eta=eta0+at
        return cv('H_prefactor_s_inv')*(cv('omh2')*(-3*eta).exp()+cv('odeh2')+radiation*(-4*eta).exp()).sqrt()
    pref=cv('LYA_FACT_cm3_inv')/(NH/10**6)
    ra=pref*H(u)*(3*u).exp()/g
    inc=source['incoming'];j=source['source_segment']
    knot=(inc['source_indices'][j]-5126)*h+z(C['lag'])
    dep=[z(F.from_float(float.fromhex(v))) for v in inc['departure_hex']]
    wien=z(0) if mutation=='drop_Wien' else (-z(C['A'])*u.exp()).exp()
    fin=dep[j]+(dep[j+1]-dep[j])*(u-knot)/h+wien
    M=[[z(maps['M0'][i][j])+theta*z(maps['delta_M'][i][j]) for j in range(2)] for i in range(2)]
    M[1][1]=M[1][1]+ra
    b=[z(maps['b0'][i][0])+theta*z(maps['delta_b'][i][0]) for i in range(2)]
    b[1]=b[1]+3*ra*g*fin
    q,det=solve_intervals(M,b)
    low_g=min(F(C['g0']),F(C['g1']));high_g=max(F(C['g0']),F(C['g1']))
    rlo=pref*H(h)/high_g
    rhi=pref*H(z(0))*(3*h).exp()/low_g
    cmins=[]
    for col in range(2):
        left=sum(F(maps['M0'][i][col]) for i in range(2))
        right=left+sum(F(maps['delta_M'][i][col]) for i in range(2))
        cmins.append(min(left,right))
    gamma=min(cmins[0],cmins[1]+rlo.pair()[0])
    if gamma<=0:raise AssertionError('whole-cell contraction not established')
    for i,j in [(0,1),(1,0)]:
        if max(F(maps['M0'][i][j]),F(maps['M0'][i][j])+F(maps['delta_M'][i][j]))>0:raise AssertionError('whole-cell Metzler condition failed')
    K=F(C['NH_reference'])*rhi.pair()[1]/gamma
    qhat=[F((v.lo+v.hi)//2,v.S) for v in q]
    E=sum(max(x-v.pair()[0],v.pair()[1]-x) for v,x in zip(q,qhat))
    delta=sum(((v-z(x)).abs() for v,x in zip(q,source['cut']['p'])),z(0))
    residual=[b[i]-sum((M[i][j]*z(qhat[j]) for j in range(2)),z(0)) for i in range(2)]
    gammacut=min(sum(M[i][j] for i in range(2)).pair()[0] for j in range(2))
    Er=sum(max(abs(v.pair()[0]),abs(v.pair()[1])) for v in residual)/gammacut
    return {'precision_bits':P,'mutation':mutation,'M':[[x.pack() for x in row] for row in M],'b':[x.pack() for x in b],
            'q_interval':[v.pack() for v in q],'q_hat':[fracpack(x) for x in qhat],'q_hat_display':[display(x) for x in qhat],
            'E_QSS_new':fracpack(E),'E_residual':fracpack(Er),'residual':[x.pack() for x in residual],
            'delta_interval':delta.pack(),'delta_display':[display(x) for x in delta.pair()],
            'determinant':det.pack(),'Ralpha_cut':ra.pack(),'Ralpha_whole_upper':fracpack(rhi.pair()[1]),
            'gamma_cut_lower':fracpack(gammacut),'gamma_whole_lower':fracpack(gamma),'K_upper':fracpack(K),
            'conditional_reward_ceiling':fracpack(K*delta.pair()[1]),
            'conditional_plus_inherited_cut_error':fracpack(K*(delta.pair()[1]+F(source['cut_error']))),
            'known_cut_error_contribution':fracpack(K*F(source['cut_error'])),
            'future_count_arithmetic_qhat_contribution':fracpack(K*E),
            'historical_scalar_difference':(delta-z(source['historical']['delta_reported'])).pack(),
            'positive':min(x.lo for x in q)>0}

def main():
    p=U/'inputs/SOURCE_SLICE.json';data=p.read_bytes()
    if hashlib.sha256(data).hexdigest()!=PIN:raise ValueError('source projection identity mismatch')
    src=json.loads(data);c=src['clock'];u=F(src['cut']['u']);h=F(c['h']);j=src['source_segment'];inc=src['incoming']
    assert F(0)<=u<=h and F(0)<=F(src['cut']['t_s'])<=F(src['duration'])
    a=(inc['source_indices'][j]-5126)*h+F(c['lag']);b=a+h
    assert a<=u<=b,'source segment mismatch'
    rows=[assemble(src,P) for P in (256,384,512)]
    mutations=[assemble(src,384,m) for m in ('drop_Wien','decimalize_binary64','reset_theta')]
    checks=[{'name':'source_and_segment_exact','pass':True}]
    for row in rows:
        checks.append({'name':f"positive_nonsingular_P{row['precision_bits']}",'pass':row['positive'] and int(row['determinant']['lo'])>0})
    def pair(x):return F(int(x['lo']),1<<x['bits']),F(int(x['hi']),1<<x['bits'])
    for a,b in zip(rows,rows[1:]):
        for i in range(2):
            la,ha=pair(a['q_interval'][i]);lb,hb=pair(b['q_interval'][i])
            checks.append({'name':f"nested_{a['precision_bits']}_{b['precision_bits']}_q{i}",'pass':la<=lb<=hb<=ha})
    er=rows[-1]['E_QSS_new'];checks.append({'name':'P512_radius_below_1e-90','pass':F(int(er['numerator']),int(er['denominator']))<F('1e-90')})
    for row in mutations:
        dr=[I(int(x['lo']),int(x['hi']),384)-I(int(y['lo']),int(y['hi']),384) for x,y in zip(row['q_interval'],rows[1]['q_interval'])]
        dist=sum((x.abs() for x in dr),I.point(0,384))
        row['q_difference_from_nominal']=dist.pack();row['q_difference_display']=[display(x) for x in dist.pair()]
        checks.append({'name':'detected_'+row['mutation'],'pass':dist.lo>0})
    out={'status':'COMPUTED_LITERAL_ARITHMETIC_ENCLOSURE','source_slice_sha256':PIN,'rows':rows,'mutations':mutations,'checks':checks,
         'E_QSS_old':None,'historical_vector_recovered':False,'physical_radii':None,'L4':False,'native_ODEs':0,'old_replays':0,
         'claim':'new exact source-literal target and dyadic representative only; old numerical/physical-source errors not supplied'}
    (U/'evidence/PRIMARY.json').write_text(json.dumps(out,indent=2)+'\n')
    if not all(x['pass'] for x in checks):raise AssertionError('primary failure saved')
    print(json.dumps({'checks_passed':len(checks),'q':rows[-1]['q_hat_display'],'delta':rows[-1]['delta_display'],
      'E_QSS_new':rows[-1]['E_QSS_new']['decimal_upper'],'future_count_bound':rows[-1]['conditional_reward_ceiling']['decimal_upper'],
      'mutations':[(r['mutation'],r['q_difference_display']) for r in mutations]},indent=2))
if __name__=='__main__':main()
