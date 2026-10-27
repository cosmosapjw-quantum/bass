import csv,json,hashlib,functools
import numpy as np
from reconstruct import *

def main():
    finite,core=reused_modules();p=finite.p
    p.sphere_rule=functools.lru_cache(maxsize=65)(p.sphere_rule)
    read=lambda f:json.loads((OLD/'inputs/b3c/raw'/f).read_text())
    fixtures={x['name']:x for x in read('VALIDATION.json')['fixtures']};rows=[];summaries=[]
    for label,fixture in fixtures.items():
        path=read(label+'_N256_PATH.json');births=read(label+'_N256_SOURCE_HISTORY.json')
        if len(path)!=257 or len(births)!=256:raise ValueError('frozen row count')
        final=path[-1];t14=[];tc=[];balls=[];ubs=[];upper=[]
        for i,(ep,birth) in enumerate(zip(path,births)):
            m=midpoint(ep,birth,fixture);R,eR,D,dD=mapped(m,final);Ra,era,Da,dda=mapped(m,final,False)
            S=np.asarray(birth['midpoint_S']);n=birth['ledger']['down_m3'];E=fixture['card']['energy_J']
            if n<=0 or E!=p.EB:raise ValueError('positive source/fixed energy')
            select=p.select(S,R,maxK=64);sel=select['selected'];rays,A=p.sphere_rule(sel['Nmu'])
            cont=p.moments(S,R,rays,A);q=p.moments(S,R,*q14());w=E*n*D
            t14.append(w*q['T']);tc.append(w*cont['T'])
            ball=finite.ball(S,R,n,sel['B_T'],eR=eR,eS=0,en=0);balls.append(ball)
            physical=finite.ball(S,R,n,sel['B_T'],eR=None,eS=None,en=None)
            if physical['status']!='INPUT_ERROR_UNSPECIFIED':raise ArithmeticError('physical uncertainty')
            u=E*n*(D*eR+dD*(max(np.diag(R))+eR));ua=E*n*(Da*era+dda*(max(np.diag(Ra))+era))
            ubs.append(np.sqrt(2)*u);upper.append(E*n*(D+dD)*(max(np.diag(R))+eR))
            rows.append(dict(fixture=label,transfer_id=birth['transfer_id'],**m,R=np.diag(R),D=D,eR=eR,dD=dD,analytic_eR=era,analytic_dD=dda,U14=u,U14_analytic=ua,finite14_T=t14[-1],continuum_T=tc[-1],odd_residual=q['flux'],continuum_odd_residual=cont['flux'],selected=sel,numerical_ball=dict(semantics='NUMERICAL_RECONSTRUCTION',historical_result=ball),physical_ball=physical,physical_radii=dict(eS=None,en=None,eE=None,geometry=None)))
        f14=compensated(t14);continuum=compensated(tc);scale=core.FixedScale(fixture['L_m']).density_factor
        saved=np.zeros((4,4));saved[0,0]=final['rho_gamma']/scale;saved[1:,1:]=(final['rho_gamma']*np.eye(3)/3+np.asarray(final['pi_gamma']))/scale
        # Odd components are a separately recorded roundoff diagnostic.
        diff=f14-saved;diff[0,1:]=0;diff[1:,0]=0
        norm=float(np.linalg.norm(diff));bound=math.fsum(ubs)+2e-12*math.fsum(upper)
        covered=all(b.get('composition') is not None for b in balls)
        mix=finite.mixture(balls,np.ones(256)) if covered else dict(status='NOT_COVERED_BY_NUMERICAL_BALL')
        summaries.append(dict(fixture=label,finite14=f14,continuum=continuum,saved=saved,signed_difference=f14-saved,angular_model_difference=continuum-f14,joint_difference_norm=norm,numerical_consistency_bound=bound,consistency_pass=norm<=bound,relative_difference=norm/saved[0,0],relative_bound=bound/saved[0,0],mixture=mix,individual_target_pass_count=sum(b.get('composition',{}).get('status')=='CERTIFIED_SCOPED_NUMERICAL_BUDGET' for b in balls if b.get('composition')),geometry=geometry_check(final,fixture,f14,core)))
    write_json(ROOT/'results/MIDPOINT_ROWS.json',dict(rows=rows))
    with (ROOT/'results/MIDPOINT_ROWS.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['fixture','transfer_id','alpha','beta1','beta2','beta3','alpha_analytic','beta1_analytic','beta2_analytic','beta3_analytic','eR','D','dD'])
        for r in rows:w.writerow([r['fixture'],r['transfer_id'],*r['coordinates'],*r['analytic'],r['eR'],r['D'],r['dD']])
    write_json(ROOT/'results/SUMMARY.json',dict(fixtures=summaries,births=len(rows),core_rhs_evaluations=2,physical_error=None,L4=False,B4='NOT_RUN',B5='NOT_RUN',interpretation='ANALYTIC_RECONSTRUCTION_PLUS_EMPIRICAL_BINARY64_RESERVE_NOT_HISTORICAL_INTERVAL_ENCLOSURE'))
    if not all(s['consistency_pass'] for s in summaries):raise ArithmeticError('saved final photon consistency failed; preserved outputs')
    print('512 reconstructed births; two final fixture RHS evaluations; physical radii unspecified')
if __name__=='__main__':main()
