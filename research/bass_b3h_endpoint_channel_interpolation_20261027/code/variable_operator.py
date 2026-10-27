"""Actual nonautonomous two-state operator from the same tagged gross maps."""
from mp_b import *
from jets import Jet,slow_state,adjoint_terms

class VariableOperator:
    def __init__(self,clock,endpoint,data):
        self.clock=clock;self.endpoint=endpoint;self.data=data;self.cache={};self.P=mp.matrix([[0,0],[0,1]]);self.ep=mp.matrix([0,1])
        self.p0=mp.matrix([m(x[0]) for x in data['prior']['finite_solution']['p0']])
    def jets(self,u,segment):
        key=(u._mpf_,segment)
        if key not in self.cache:
            C=self.clock;E=self.endpoint;U=Jet.variable(u,3);H=C.Hjet(u,3);theta,theta_error=C.theta_jet(u,H,3)
            g=C.g0+C.gprime*U;R=(C.LYA/C.nH0)*H*(3*U).exp()/g;F=C.incoming_jet(u,segment,3)
            rep=E['coefficient_representation_errors'];M0=Jet.constant(E['M0'],3,rep[0]['M']);dM=Jet.constant(E['delta_M'],3,rep[0]['M']+rep[1]['M'])
            b0=Jet.constant(E['b0'],3,rep[0]['b']);db=Jet.constant(E['delta_b'],3,rep[0]['b']+rep[1]['b'])
            M=M0+theta*dM+R*self.P
            b=b0+theta*db+3*R*g*F*self.ep
            self.cache[key]=dict(U=U,H=H,theta=theta,theta_error=theta_error,g=g,R=R,F=F,M=M,b=b)
        return self.cache[key]
    def slow(self,u,segment,order=2):
        J=self.jets(u,segment);return slow_state(J['M'],J['b'],J['H'],order)
    def qjet(self,u,segment,k,j=0,direct_alpha=False):
        J=self.jets(u,segment);scalar=(k*J['U']).exp()
        if direct_alpha:return scalar*J['R']*mp.matrix([[0,1]])
        if j==1:scalar=scalar*J['theta']
        elif j!=0:raise ValueError('unselected theta power; endpoint-tagged model needs only0/1')
        return scalar*mp.eye(2)
    def adjoint(self,u,segment,k,j=0,direct_alpha=False,order=3):
        J=self.jets(u,segment);q=self.qjet(u,segment,k,j,direct_alpha)
        terms,remainder=adjoint_terms(q,J['M'],J['H'],order)
        bounded=sum((term*J['b'] for term in terms),Jet.constant(mp.zeros(q.c[0].rows,1),0))/J['H']
        return dict(terms=terms,remainder=remainder,integrand=bounded.c[0],integrand_error=bounded.e[0],theta_error=J['theta_error'])
    def real_bounds(self):
        C=self.clock;E=self.endpoint;gmin=min(C.g0,C.g1);gmax=max(C.g0,C.g1)
        if gmin<=0:raise ValueError('nonpositive prepared opacity')
        Rmin=C.LYA/C.nH0*C.H(C.h)/gmax;Rmax=C.LYA/C.nH0*C.H(m(0))*mp.exp(3*C.h)/gmin
        cols=[min(sum(E['M0'][i,j] for i in range(2)),sum(E['M1'][i,j] for i in range(2)))+(Rmin if j==1 else 0) for j in range(2)]
        off=[E['M0'][0,1],E['M0'][1,0],E['M1'][0,1],E['M1'][1,0]];gamma_nominal=min(cols);repr_margin=3*max(x['M'] for x in E['coefficient_representation_errors'])+ARITH*Rmax;gamma=gamma_nominal-repr_margin
        check('uniform variable M cooperative contraction',max(off)<=0 and gamma>0,dict(offdiagonals=off,column_lower_bounds=cols,gamma=gamma))
        Fmax=max(abs(C.departure(u,j)) for j,(a,b) in enumerate(C.segments) for u in [a,b])+mp.exp(-C.A)
        brep=3*max(x['b'] for x in E['coefficient_representation_errors']);Bmax=max(norm(E['b0']),norm(E['b1']))+brep+3*Rmax*gmax*Fmax;Pmax=max(norm(self.p0),Bmax/gamma)
        lower=[]
        for i in range(2):
            bmin=min(E['b0'][i],E['b1'][i])-brep;Mmax=max(E['M0'][i,i],E['M1'][i,i])+(Rmax if i==1 else 0)+repr_margin
            lower.append(min(self.p0[i],bmin/Mmax))
        check('whole-step positive state comparison lower bound',min(lower)>0,lower)
        for j,(a,b) in enumerate(C.segments):
            fmin=min(C.departure(a,j),C.departure(b,j))+mp.exp(-C.A*mp.exp(b))
            check(f'incoming segment{j} positive represented occupation',fmin>0,fmin)
        return dict(gamma=gamma,gamma_nominal=gamma_nominal,coefficient_representation_contraction_margin=repr_margin,Ralpha_lower=Rmin,Ralpha_upper=Rmax,b_norm_upper=Bmax,Pmax=Pmax,p_component_lower=lower)
