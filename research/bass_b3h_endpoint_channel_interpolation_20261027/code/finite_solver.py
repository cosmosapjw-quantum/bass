"""Prescribed q2 endpoints and m3 shared moments with true-clock jet errors."""
from mp_b import *
from jets import mag,product_error,Jet
from analytic_bounds import certificate,observable_bound
from certified_quad import integrate

def panels(model):
    out=[];changes=0
    def make(a,b,seg,outer=m('.001'),inner=m('.0005')):
        nonlocal changes
        try:cert=certificate(model,a,b,seg,outer,inner)
        except ValueError as exc:
            if changes>=4:raise ValueError('analytic domain refinements exhausted: '+str(exc))
            changes+=1
            if inner/2>(b-a)/2:return make(a,b,seg,outer/2,inner/2)
            mid=(a+b)/2;make(a,mid,seg,outer,inner);make(mid,b,seg,outer,inner);return
        out.append(cert)
    for j,(a,b) in enumerate(model.clock.segments):make(a,b,j)
    return out,changes

def finite_endpoints(model,save_progress=None):
    C=model.clock;real=model.real_bounds();certs,refinements=panels(model);p=model.p0.copy();E=m(0);saved=[]
    for j,cert in enumerate(certs):
        a,b,seg=cert['a'],cert['b'],cert['segment'];ta,ea=C.partial_time(a);tb,eb=C.partial_time(b);dt=tb-ta;dterr=ea+eb;lo=dt-dterr;hi=dt+dterr
        if lo<=0:raise ValueError('new proper segment duration lower bound not positive')
        pa=model.slow(a,seg,2);pb=model.slow(b,seg,2);Ja=model.jets(a,seg);Mj=Ja['M'].c[0];Merror=Ja['M'].e[0]
        gammas=[sum(Mj[i,k] for i in range(2)) for k in range(2)];gamma=min(real['gamma'],min(gammas))-Merror
        if gamma<=0:raise ValueError('frozen-layer contraction lower bound not positive')
        z=p-pa['value'];Z=norm(z)+ARITH*(norm(p)+norm(pa['value']));factor=mp.exp(-gamma*lo);tail=Z*factor
        omit_allow=ARITH*(norm(p)+norm(pb['value']));omit_layer=tail<=omit_allow;omitted=tail if omit_layer else m(0)
        if omit_layer:layer=mp.matrix([0,0])
        else:
            eig=mp.eig(Mj,left=False,right=False);l1,l2=eig;I=mp.eye(2)
            layer=((mp.exp(-l1*dt)*(Mj-l2*I)-mp.exp(-l2*dt)*(Mj-l1*I))/(l1-l2))*z
        epsilon=cert['exact_slow_residual_bound'];L=cert['M_proper_derivative_bound']
        slow_bound=epsilon*(-mp.expm1(-gamma*hi))/gamma
        layer_variation=L*Z*hi**2*factor/2;anchor_evaluation=Merror*Z*hi*factor
        arithmetic=ARITH*(norm(p)+norm(pb['value'])+norm(z)+norm(layer))
        retained_layer_time_error=m(0) if omit_layer else matnorm(Mj)*Z*dterr*factor
        endpoint_error=factor*(E+pa['value_error'])+slow_bound+layer_variation+anchor_evaluation+pb['value_error']+omitted+retained_layer_time_error+arithmetic
        pnew=pb['value']+layer
        row=dict(u_start=a,u_end=b,source_segment=seg,t_start=ta,t_end=tb,duration=dt,duration_error=dterr,p_start=p,p_end=pnew,
          error_start=E,error_end=endpoint_error,part_start=pa['value'],part_end=pb['value'],part_start_evaluation_error=pa['value_error'],part_end_evaluation_error=pb['value_error'],
          actual_endpoint_residual=pb['residual'],actual_residual_evaluation_error=pb['residual_evaluation_error'],analytic_residual_bound=epsilon,
          frozen_layer_M=Mj,layer_amplitude=z,layer_log_contraction=-gamma*lo,layer_omitted=bool(omit_layer),omitted_layer_norm_bound=omitted,retained_layer_duration_evaluation_error=retained_layer_time_error,
          slow_error_bound=slow_bound,variable_layer_error_bound=layer_variation,frozen_anchor_evaluation_error_bound=anchor_evaluation,declared_arithmetic_allowance=arithmetic,
          clock_error_route='A: finite value/jet enclosures propagated through K,Pq; no duplicate Eclock sensitivity term')
        saved.append(row)
        if save_progress:save_progress(dict(endpoints=saved,analytic_domain_certificates=certs,real_bounds=real))
        check(f'endpoint panel{j} positive fraction with error margin',min(pnew)>endpoint_error,dict(p=pnew,error=endpoint_error))
        check(f'endpoint panel{j} one-norm error target',endpoint_error<=m('1e-34'),endpoint_error,m('1e-34'))
        p=pnew;E=endpoint_error
    return dict(p0=model.p0,p1=p,p1_error=E,endpoints=saved,analytic_domain_certificates=certs,real_bounds=real,domain_refinements=refinements)

def moment(model,fin,k,j=0,direct=False):
    C=model.clock;total=None;total2=None;error=m(0);error2=m(0);rows=[]
    for row,cert in zip(fin['endpoints'],fin['analytic_domain_certificates']):
        a,b,seg=cert['a'],cert['b'],cert['segment'];B=observable_bound(cert,k,j,direct)
        def eval_integrand(u,order=3):
            x=model.adjoint(u,seg,k,j,direct,order);return x['integrand'],x['integrand_error']
        Q,Qerr=integrate(f'adjoint k{k}j{j}alpha{direct} m3',eval_integrand,a,b,cert['inner_radius'],B['integrand_m3_complex_upper'],diagnostic16=True)
        Q2,Qerr2=integrate(f'adjoint k{k}j{j}alpha{direct} m2 diagnostic',lambda u:eval_integrand(u,2),a,b,cert['inner_radius'],B['integrand_m2_complex_upper'])
        boundary=mp.zeros(Q.rows,1);boundary2=mp.zeros(Q.rows,1);boundary_error=m(0);boundary_error2=m(0)
        for u,p,ep,sign in [(a,row['p_start'],row['error_start'],1),(b,row['p_end'],row['error_end'],-1)]:
            adj=model.adjoint(u,seg,k,j,direct,3)
            for r,term in enumerate(adj['terms']):
                boundary+=sign*term.c[0]*p;be=mag(term.c[0])*ep+term.e[0]*norm(p)+term.e[0]*ep+ARITH*mag(term.c[0])*norm(p);boundary_error+=be
                if r<2:boundary2+=sign*term.c[0]*p;boundary_error2+=be
        dt_upper=row['duration']+row['duration_error'];rem=fin['real_bounds']['Pmax']*dt_upper*B['adjoint_m3_remainder_derivative_bound'];rem2=fin['real_bounds']['Pmax']*dt_upper*B['adjoint_m2_remainder_derivative_bound']
        value=Q+boundary;value2=Q2+boundary2;this_error=Qerr+boundary_error+rem+ARITH*(norm(Q)+norm(boundary));this_error2=Qerr2+boundary_error2+rem2+ARITH*(norm(Q2)+norm(boundary2))
        if total is None:total=mp.zeros(value.rows,1);total2=mp.zeros(value.rows,1)
        total+=value;total2+=value2;error+=this_error;error2+=this_error2
        rows.append(dict(a=a,b=b,value=value,value_order2=value2,quadrature_error=Qerr,boundary_error=boundary_error,analytic_adjoint_remainder=rem,error=this_error,
          analytic_bounds=B,inner_radius=cert['inner_radius'],outer_radius=cert['outer_radius'],clock_error_propagation='true-clock finite jet error at all positive Gauss nodes and boundaries'))
    return dict(I=total,I_error=error,I_order2=total2,I_order2_error=error2,order2_order3_difference=norm(total-total2),segments=rows)

def scalar_moment(model,fin,k,j):
    C=model.clock
    if k==0:return (C.T,C.T_error) if j==0 else (C.T/2,C.T_error/2)
    value=m(0);error=m(0)
    for cert in fin['analytic_domain_certificates']:
        a,b,seg=cert['a'],cert['b'],cert['segment'];B=observable_bound(cert,k,j,False)
        def fn(u):
            J=model.jets(u,seg);w=(k*J['U']).exp()
            if j:w=w*J['theta']
            y=w/J['H'];return y.c[0],y.e[0]
        v,e=integrate(f'scalar F{k}{j}',fn,a,b,cert['inner_radius'],B['q_complex_upper']/cert['H']['H_min'],diagnostic16=True);value+=v;error+=e
    return value,error

def all_moments(model,fin,save_progress=None):
    out={};direct={}
    for k in range(3):
        for j in range(2):
            record=moment(model,fin,k,j);record['F'],record['F_error']=scalar_moment(model,fin,k,j);out[f'k{k}_j{j}']=record
            if save_progress:save_progress(dict(moments=out,direct_alpha=direct))
    for k in [0,1]:
        record=moment(model,fin,k,0,True);record['I']=record['I'][0];record['I_order2']=record['I_order2'][0];direct[f'k{k}']=record
        if save_progress:save_progress(dict(moments=out,direct_alpha=direct))
    return out,direct
