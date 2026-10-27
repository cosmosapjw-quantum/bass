"""Prescribed nested-disk bounds, true-clock jets, and finite norm recurrences."""
from math import comb
from mp_b import *

def proper_bounds(B,H,gap):
    # Cauchy on outer domain, evaluated throughout the inner disk.
    G1=B/gap;G2=2*B/gap**2;G3=6*B/gap**3;Hu=H/gap;Huu=2*H/gap**2
    return [B,H*G1,H*H*G2+H*Hu*G1,H**3*G3+3*H*H*Hu*G2+(H*Hu**2+H*H*Huu)*G1]
def convolution_derivatives(F,G,n):return [sum(comb(j,k)*F[k]*G[j-k] for k in range(j+1)) for j in range(n+1)]
def differentiated_product(previous,K):
    n=len(previous)-2;return [sum(comb(j,k)*previous[k+1]*K[j-k] for k in range(j+1)) for j in range(n+1)]

def certificate(model,a,b,segment,outer=m('.001'),inner=m('.0005')):
    C=model.clock;E=model.endpoint;centre=(a+b)/2
    if not (b-a)/2<inner<outer:raise ValueError('positive nested Cauchy radius gap absent')
    H=C.H_disk(centre,outer);gmin=C.g(centre)-abs(C.gprime)*outer;gmax=C.g(centre)+abs(C.gprime)*outer
    if gmin<=0:raise ValueError('g disk includes a pole')
    J=model.jets(centre,segment);Kc=J['M'].inverse();theta=J['theta'].c[0];theta_error=J['theta'].e[0]
    theta_delta=outer/H['H_min']/C.T_lower
    Rmax=C.LYA/C.nH0*H['H_max']*mp.exp(3*(centre+outer))/gmin
    BRu=Rmax*(H['H_u_over_H_bound']+3+abs(C.gprime)/gmin)
    rep=E['coefficient_representation_errors'];DM=matnorm(E['delta_M'])+rep[0]['M']+rep[1]['M'];Db=norm(E['delta_b'])+rep[0]['b']+rep[1]['b']
    disk_variation=DM*theta_delta+outer*BRu;centre_error=J['M'].e[0]
    beta=matnorm(Kc.c[0])*(centre_error+disk_variation)
    if beta>=1:raise ValueError('M inverse outer disk Neumann certificate failed')
    BK=matnorm(Kc.c[0])/(1-beta)
    Fbound=abs(C.departure(centre,segment))+abs(C.slopes[segment])*outer+mp.exp(-C.A*mp.exp(centre-outer)*mp.cos(outer))
    bn=E['b0']+theta*E['delta_b'];Bb=norm(bn)+Db*(theta_delta+theta_error)+rep[0]['b']+3*(C.LYA/C.nH0)*H['H_max']*mp.exp(3*(centre+outer))*Fbound
    gap=outer-inner;Kd=proper_bounds(BK,H['H_max'],gap);bd=proper_bounds(Bb,H['H_max'],gap)
    y0=convolution_derivatives(Kd,bd,3);y1=differentiated_product(y0,Kd);y2=differentiated_product(y1,Kd)
    Mprime=DM/C.T_lower+H['H_max']*BRu
    return dict(a=a,b=b,segment=segment,centre=centre,outer_radius=outer,inner_radius=inner,positive_derivative_gap=gap,H=H,g_modulus_lower=gmin,g_modulus_upper=gmax,
      theta_centre=theta,theta_centre_error=theta_error,theta_complex_variation=theta_delta,Ralpha_complex_upper=Rmax,Ralpha_u_bound=BRu,
      M_centre_error=centre_error,M_disk_variation=disk_variation,inverse_Neumann_beta=beta,K_complex_upper=BK,b_complex_upper=Bb,
      K_proper_derivative_bounds=Kd,b_proper_derivative_bounds=bd,slow_y0_bounds=y0,slow_y1_bounds=y1,slow_y2_bounds=y2,
      exact_slow_residual_bound=y2[1],M_proper_derivative_bound=Mprime,
      clock_error_method='RouteA: C1-C3 value/jet enclosures directly propagated by C7-C11; no additional profile Eclock added',
      inherited_input_accuracy='conditional on admitted saved values; physical and old quadrature remainder remain null')

def observable_bound(cert,k,j=0,direct_alpha=False):
    C=cert;outer=C['outer_radius'];centre=C['centre'];theta_abs=abs(C['theta_centre'])+C['theta_centre_error']+C['theta_complex_variation']
    Q=mp.exp(k*(centre+outer))*(C['Ralpha_complex_upper'] if direct_alpha else theta_abs if j else 1)
    Qd=proper_bounds(Q,C['H']['H_max'],C['positive_derivative_gap']);Kd=C['K_proper_derivative_bounds'];P0=convolution_derivatives(Qd,Kd,3);P1=differentiated_product(P0,Kd);P2=differentiated_product(P1,Kd)
    return dict(q_complex_upper=Q,q_proper_derivative_bounds=Qd,Psi0_bounds=P0,Psi1_bounds=P1,Psi2_bounds=P2,
      adjoint_m3_remainder_derivative_bound=P2[1],adjoint_m2_remainder_derivative_bound=P1[1],
      integrand_m3_complex_upper=(P0[0]+P1[0]+P2[0])*C['b_complex_upper']/C['H']['H_min'],
      integrand_m2_complex_upper=(P0[0]+P1[0])*C['b_complex_upper']/C['H']['H_min'])
