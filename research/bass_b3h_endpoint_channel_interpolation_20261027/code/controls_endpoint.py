"""One finite analytic control for the new slow and adjoint jet routines."""
from mp_b import *
from jets import Jet,slow_state,adjoint_terms
from certified_quad import integrate


def analytic_control():
    A=mp.matrix([[4,-1],[-2,5]]);K=A**-1;b0=mp.matrix([1,2]);v=mp.matrix([m('.2'),m('.1')]);p0=mp.matrix([m('.3'),m('.4')]);T=m('.3');H=Jet.constant(m(1),3)
    z=p0-K*b0+K*K*v;E=mp.expm(-A*T)
    exact_end=K*(b0+T*v)-K*K*v+E*z
    def objects(t):
        U=Jet.variable(t,3);M=Jet.constant(A,3);b=Jet.constant(b0,3)+U*v
        return U,M,b
    U,M,b=objects(T);slow=slow_state(M,b,H,2);implemented_end=slow['value']+E*(p0-slow_state(*objects(m(0))[1:],H,2)['value'])
    end_error=norm(exact_end-implemented_end)
    check('new constant-M affine-source control nonzero initial layer',norm(z)>m('.01'),z)
    check('new q2 jet endpoint vs exact affine convolution',end_error<=ARITH*norm(exact_end),end_error)
    # q(t)=(1+t+t^2)I gives nonzero Psi1 and Psi2, with zero m3 remainder.
    J=[K*(mp.eye(2)-E)]
    for n in (1,2):J.append(-T**n*K*E+n*K*J[-1])
    exact_I=sum(((K*b0-K*K*v)*(T**(n+1)/(n+1))+(K*v)*(T**(n+2)/(n+2))+J[n]*z for n in (0,1,2)),mp.zeros(2,1))
    def evaluation(t):
        U,M,b=objects(t);q=(1+U+U*U)*mp.eye(2);terms,rem=adjoint_terms(q,M,H,3)
        value=sum((term*b for term in terms),Jet.constant(mp.zeros(2,1),0))
        return value.c[0],value.e[0]
    integral,error=integrate('new analytic control polynomial adjoint',evaluation,m(0),T,m(1),m(100),diagnostic16=True)
    boundary=mp.zeros(2,1);boundary_error=m(0);term_values=[]
    for t,p,sign in [(m(0),p0,1),(T,implemented_end,-1)]:
        U,M,b=objects(t);terms,rem=adjoint_terms((1+U+U*U)*mp.eye(2),M,H,3)
        check('constant control m3 remainder exactly zero at '+str(t),norm(rem)==0,rem)
        term_values.append([term.c[0] for term in terms])
        for term in terms:boundary+=sign*term.c[0]*p;boundary_error+=term.e[0]*norm(p)+ARITH*norm(term.c[0]*p)
    actual_I=integral+boundary;bound=error+boundary_error+ARITH*(norm(integral)+norm(boundary)+norm(exact_I));residual=norm(actual_I-exact_I)
    check('new m3 adjoint vs independent exact nonzero-layer moment',residual<=bound,dict(residual=residual,bound=bound))
    return dict(M=A,b0=b0,b_proper_derivative=v,p0=p0,T=T,initial_layer=z,exact_endpoint=exact_end,new_q2_endpoint=implemented_end,endpoint_difference=end_error,
      weight='1+t+t^2',exact_moment=exact_I,new_adjoint_moment=actual_I,moment_difference=residual,derived_bound=bound,adjoint_terms=term_values,old_controls_replayed=0)
