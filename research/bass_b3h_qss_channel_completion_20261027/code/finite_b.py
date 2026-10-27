"""Constant activity matrix finite endpoint and exact integrated moments."""
from mp_b import *
from decimal import Decimal

def decimal_half_unit(s):return mp.power(10,Decimal(s).as_tuple().exponent)/2
class Clock:
    def __init__(self,packet,tube,op,right,maps):
        self.packet=packet;self.tube=tube;self.g0=op['x1s'];self.g1=right['x1s'];self.NH=m(tube['nH_reference_m3']);self.LYA=m(packet['native_cosmology']['LYA_FACT_cm3_inv'])
        sel=packet['selection'];inc=packet['incoming'];self.h=m(float.fromhex(sel['dlna_hex']));self.gp=(self.g1-self.g0)/self.h
        self.c=self.NH/m(10**6)/self.LYA;self.pref=1/self.c
        self.E=m(float.fromhex(inc['target_energy_eV_hex']));Es=m(float.fromhex(inc['source_energy_eV_hex']));self.lag=mp.log(Es/self.E)
        k=sel['cell_indices'][0];eta=m(float.fromhex(sel['eta0_hex']))+k*self.h;co=packet['native_cosmology']
        self.A=self.E*mp.exp(eta)*m(co['fsR'])**2*m(co['meR'])/(m(co['kBoltz_eV_K'])*m(co['T0_K']))
        self.knots=[(j-k)*self.h+self.lag for j in inc['source_indices']];self.values=[m(float.fromhex(x)) for x in inc['departure_hex']]
        edges=[ZERO]+[u for u in self.knots if 0<u<self.h]+[self.h];self.segments=list(zip(edges[:-1],edges[1:]))
        self.segment_indices=[next(j for j in range(len(self.knots)-1) if self.knots[j]<=(a+b)/2<=self.knots[j+1]) for a,b in self.segments]
        self.slopes=[(self.values[j+1]-self.values[j])/(self.knots[j+1]-self.knots[j]) for j in self.segment_indices]
        self.bn=maps['b_nonLya'];self.M=maps['M'];self.K=maps['K'];self.K2=self.K*self.K;self.K3=self.K2*self.K;self.gamma=maps['gamma']
        ref=tube['independent_reference'];self.Nin=m(ref['N_in_m3']);self.Uin=m(ref['U0_J_m3']);self.duration=m(ref['proper_duration_s'])
        self.inherited_errors=dict(Nin=decimal_half_unit(ref['N_in_m3']),Uin=decimal_half_unit(ref['U0_J_m3']),duration=decimal_half_unit(ref['proper_duration_s']),role='saved65-significant-digit reference-string representation rounding only; not old quadrature or source accuracy',
          prior_acceptance_tolerance=m('2e-11'),prior_acceptance_is_rigorous_error_bound=False,inherited_reference_quadrature_remainder=None,total_input_error=None,physical_error=None,
          new_bounds_conditional_on='admitted saved moment numbers and declared MP arithmetic allowance; no old quadrature replay')
        check('strict-past actual incoming split',self.lag>self.h and len(self.segments)==2,[self.lag-self.h,edges])
    def g(self,u):return self.g0+self.gp*u
    def D(self,u):return self.c*self.g(u)*mp.exp(-3*u)
    def Du(self,u):return self.c*(self.gp-3*self.g(u))*mp.exp(-3*u)
    def dep(self,u,j):
        i=self.segment_indices[j];return self.values[i]+self.slopes[j]*(u-self.knots[i])
    def F(self,u,j):return self.dep(u,j)+mp.exp(-self.A*mp.exp(u))
    def b(self,u,j):return self.bn+mp.matrix([0,3*self.g(u)*self.F(u,j)])
    def derivatives(self,u,j):
        g=self.g(u);z=self.A*mp.exp(u);W=mp.exp(-z);F=self.F(u,j);F1=self.slopes[j]-z*W;F2=(z*z-z)*W;F3=(-z**3+3*z*z-z)*W
        u1=3*(self.gp*F+g*F1);u2=3*(2*self.gp*F1+g*F2);u3=3*(3*self.gp*F2+g*F3)
        D=self.D(u);Du=self.Du(u);Duu=self.c*(-6*self.gp+9*g)*mp.exp(-3*u)
        return self.b(u,j),mp.matrix([0,D*u1]),mp.matrix([0,D*D*u2+D*Du*u1]),mp.matrix([0,D**3*u3+3*D*D*Du*u2+(D*Du**2+D**2*Duu)*u1])
    def part(self,u,j):
        b,bs,bss,_=self.derivatives(u,j);return self.K*b-self.K2*bs+self.K3*bss
    def sup(self,kind,k,component=None):
        def bound(mid,r,j):
            gm=self.g(mid)+abs(self.gp)*r;gl=self.g(mid)-abs(self.gp)*r
            if gl<=0:raise ValueError('Cauchy circle crosses g pole')
            exp=mp.exp(k*(mid+r));F=abs(self.dep(mid,j))+abs(self.slopes[j])*r+mp.exp(-self.A*mp.exp(mid-r)*mp.cos(r))
            if kind=='clock':return self.pref*exp/gl
            if kind=='forcing':return exp*F
            if kind=='b':return exp*(abs(self.bn[component])+(3*gm*F if component==1 else 0))
            raise ValueError('unknown analytic bound')
        return bound
    def integral(self,k):
        return quadrature(f'clock S{k}',lambda u:mp.exp(k*u)/self.D(u),self.segments,self.sup('clock',k+3))
    def derivative_bounds(self,j):
        a,b=self.segments[j];gmax=max(self.g(a),self.g(b));gp=abs(self.gp);z=self.A*mp.exp(self.h);W=mp.exp(-self.A)
        Fmax=max(abs(self.dep(a,j)),abs(self.dep(b,j)))+W;F1=abs(self.slopes[j])+z*W;F2=(z*z+z)*W;F3=(z**3+3*z*z+z)*W
        bu1=3*(gp*Fmax+gmax*F1);bu2=3*(2*gp*F1+gmax*F2);bu3=3*(3*gp*F2+gmax*F3)
        Dmax=self.c*gmax;D1=self.c*(gp+3*gmax);D2=self.c*(6*gp+9*gmax)
        bound=Dmax**3*bu3+3*Dmax**2*D1*bu2+(Dmax*D1**2+Dmax**2*D2)*bu1
        return dict(Fmax=Fmax,F1=F1,F2=F2,F3=F3,Bu1=bu1,Bu2=bu2,Bu3=bu3,Dmax=Dmax,D1max=D1,D2max=D2,bsss_bound=bound)

def finite(clock,op,c):
    C=clock;p0=mp.matrix(op['absolute_population']);p=p0.copy();carry=ZERO;segments=[]
    # The exact clock count identity is algebraic, evaluated separately from
    # incoming integrations, which are preserved rather than replayed.
    u=C.h/2;clock_identity(C.NH*(1/C.D(u))*(m('1e-14')-3*C.g(u)*m('1e-15')),3*m(10**6)*C.LYA*mp.exp(3*u)*(m('1e-14')/(3*C.g(u))-m('1e-15')))
    check('native common-volume Lyalpha clock identity',True)
    for j,(a,b) in enumerate(C.segments):
        L,Lerr=quadrature(f'segment activity {j}',lambda u:1/C.D(u),[(a,b)],lambda mid,r,_:C.sup('clock',3)(mid,r,j))
        pa=C.part(a,j);pb=C.part(b,j);z=p-pa;logdecay=-C.gamma*(L-Lerr);factor=mp.exp(logdecay);tail=norm(z)*factor;allow=ARITH*(norm(p)+norm(pb))
        if tail<=allow:hom=mp.matrix([0,0]);omitted=tail;omission=True
        else:
            eig=mp.eig(C.M,left=False,right=False);l1,l2=eig;I=mp.eye(2);hom=(mp.exp(-l1*L)*(C.M-l2*I)-mp.exp(-l2*L)*(C.M-l1*I))/(l1-l2)*z;omitted=ZERO;omission=False
        db=C.derivative_bounds(j);trunc=matnorm(C.K3)*db['bsss_bound']/C.gamma
        end_error=factor*carry+(1-factor)*trunc+omitted+allow
        pnext=pb+hom
        check(f'finite segment{j} positive endpoint with error margin',min(pnext)>end_error,[pnext,end_error])
        segments.append(dict(u_start=a,u_end=b,activity=L,activity_error=Lerr,p_start=p,p_end=pnext,part_start=pa,part_end=pb,
          layer_amplitude=z,layer_log_contraction=logdecay,layer_omitted=omission,layer_omitted_bound=omitted,
          carry_in_error=carry,analytic_derivative_bounds=db,residual_norm_bound=matnorm(C.K3)*db['bsss_bound'],
          endpoint_truncation_bound=trunc,arithmetic_allowance=allow,endpoint_error=end_error,continuity='same p carried across actual incoming knot; derivatives may jump'))
        p=pnext;carry=end_error
    S,Serr=C.integral(0);Ip=C.K*(C.bn*S+mp.matrix([0,C.Nin/C.NH])-(p-p0));Ierr=matnorm(C.K)*(carry+norm(C.bn)*Serr+C.inherited_errors['Nin']/C.NH)+ARITH*norm(Ip)
    bounds=[C.derivative_bounds(j) for j in range(len(C.segments))];Fmax=max(x['Fmax'] for x in bounds);gmax=max(C.g0,C.g1)
    Pmax=max(norm(p0),(norm(C.bn)+3*gmax*Fmax)/C.gamma);Dmax=C.c*gmax;D1max=C.c*(abs(C.gp)+3*gmax)
    poplower=[min(p0[i],C.bn[i]/C.M[i,i]) for i in range(2)];check('positive system comparison lower bound',min(poplower)>0,poplower)
    weighted={0:dict(S=S,S_error=Serr,Ip=Ip,Ip_error=Ierr)}
    for k in [1,2]:
        Sk,Skerr=C.integral(k)
        if k==1:force=C.Uin/(C.NH*c['E21_J']);forceerr=C.inherited_errors['Uin']/(C.NH*c['E21_J']);forcekind='reused independent incoming pulled-back energy'
        else:
            J,Jerr=quadrature('new k2 incoming forcing',lambda u:mp.exp(5*u)*C.F(u,next(j for j,(a,b) in enumerate(C.segments) if a<=u<=b)),C.segments,C.sup('forcing',5))
            force=3*C.pref*J;forceerr=3*C.pref*Jerr;forcekind='new MP Gauss16/24 moment, not old tube replay'
        B=C.bn*Sk+mp.matrix([0,force]);Berr=norm(C.bn)*Skerr+forceerr
        Bprime=[];Bperr=ZERO
        for i in range(2):
            val,err=quadrature(f'new Bprime{k} component{i}',lambda u:k*mp.exp(k*u)*C.b(u,next(j for j,(a,b) in enumerate(C.segments) if a<=u<=b))[i],C.segments,
              lambda mid,r,j,i=i:k*C.sup('b',k,i)(mid,r,j))
            Bprime.append(val);Bperr+=err
        Bprime=mp.matrix(Bprime);w=mp.exp(k*C.h);ws1=k*w*C.D(C.h);ws0=k*C.D(ZERO)
        Ik=C.K*(B-w*p+p0)+C.K2*(Bprime-ws1*p+ws0*p0)
        remainder=matnorm(C.K2)*Pmax*(S+Serr)*k*mp.exp(k*C.h)*Dmax*(k*Dmax+D1max)
        err=matnorm(C.K)*(Berr+w*carry)+matnorm(C.K2)*(Bperr+abs(ws1)*carry)+remainder+ARITH*norm(Ik)
        weighted[k]=dict(S=Sk,S_error=Skerr,Ip=Ik,Ip_error=err,B=B,B_error=Berr,Bprime=Bprime,Bprime_error=Bperr,
          weighted_identity_remainder_bound=remainder,forcing=force,forcing_error=forceerr,forcing_role=forcekind)
    return dict(p0=p0,p1=p,delta_p=p-p0,p1_error=carry,Ip=Ip,Ip_error=Ierr,weighted=weighted,segments=segments,Pmax=Pmax,
      population_lower_bound=poplower,clock=dict(h=C.h,A=C.A,g0=C.g0,g1=C.g1,gprime=C.gp,nH_reference_m3=C.NH,LYA_FACT=C.LYA,activity=S,activity_error=Serr,
      actual_incoming_knots=C.knots,actual_segment_edges=C.segments,departure_slopes=C.slopes,Nin_saved=C.Nin,Uin_saved=C.Uin,proper_duration_saved=C.duration,
      inherited_saved_reference_uncertainty=C.inherited_errors,physical_clock_radius=None))
