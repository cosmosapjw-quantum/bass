from __future__ import annotations
import math, numpy as np
from functools import lru_cache
from numpy.polynomial.legendre import leggauss as _numpy_leggauss
from scipy.constants import c,h,k,physical_constants
from scipy.special import wofz,eval_legendre,kve

from .scalar_com_khw import (
    conditional_full_scalar_mean_amplitude_squared,
    conditional_full_minus_provisional_mean_amplitude_squared,
    conditional_provisional_mean_amplitude_squared,
)

M=physical_constants['atomic mass constant'][0]*1.00782503223; T=3000.; beta=1/(k*T)
nu_int=c/(1215.6701e-10);A21=6.265e8;gamma=A21/(4*math.pi);f=.4161967179799824
sigT=physical_constants['Thomson cross section'][0];re=physical_constants['classical electron radius'][0]
vD=math.sqrt(2*k*T/M);dnu=nu_int*vD/c;nu_abs=nu_int+h*nu_int**2/(2*M*c**2);nH=250e6
area_int=A21/(8*math.pi**2*re*f*nu_int**2/(3*c));area_abs=A21/(8*math.pi**2*re*f*nu_abs**2/(3*c))
theta=k*T/(M*c*c);zeta=1/theta;scaledK2=float(kve(2,zeta))
if not np.isfinite(scaledK2) or scaledK2<=0:scaledK2=math.sqrt(math.pi/(2*zeta))*(1+15/(8*zeta)+105/(128*zeta**2)-945/(3072*zeta**3))
const_exact=nH*c*sigT*area_int*h*dnu/(M*c*c); const_base=nH*c*sigT*area_abs*h*dnu/(M*c*c)
xedges=np.arange(-4.25,4.25+1e-12,.5);ncell=len(xedges)-1

@lru_cache(maxsize=None)
def leggauss(order):
    nodes, weights = _numpy_leggauss(int(order))
    nodes.setflags(write=False)
    weights.setflags(write=False)
    return nodes, weights


def H(a,x):return np.real(wofz(np.asarray(x)+1j*np.asarray(a)))
def resolvent(p):
 p=np.asarray(p,dtype=complex);out=np.empty_like(p);up=p.imag>0;lo=p.imag<0
 out[up]=1j*math.sqrt(math.pi/2)*wofz(p[up]/math.sqrt(2));out[lo]=-1j*math.sqrt(math.pi/2)*wofz(-p[lo]/math.sqrt(2));return out

def lor_mean(A,B,g):
 A=np.asarray(A);B=np.asarray(B);out=np.empty_like(A,dtype=float);zero=np.abs(B)<1e-250
 out[zero]=1/(A[zero]**2+g*g);nz=~zero
 xv=A[nz]/(math.sqrt(2)*B[nz]);av=g/(math.sqrt(2)*np.abs(B[nz]));out[nz]=math.sqrt(math.pi)/(math.sqrt(2)*np.abs(B[nz])*g)*H(av,xv)
 return out

def _conditional_denominators(ns,nt,mu):
 ns=np.asarray(ns,dtype=float);nt=np.asarray(nt,dtype=float)
 den=np.sqrt(ns*ns+nt*nt-2*ns*nt*mu);Q=h/c*den
 a_s=(ns-nt*mu)/den;b_s=np.sqrt(np.maximum(0,1-a_s*a_s))
 DE=h*(ns-nt);P=M*DE/Q-Q/2
 A=nu_int-ns+ns*P*a_s/(M*c)+h*ns*ns/(2*M*c*c)
 B=ns*math.sqrt(M*k*T)*b_s/(M*c)
 a_t=(ns*mu-nt)/den
 C=nu_int+nt-nt*P*a_t/(M*c)+h*nt*nt/(2*M*c*c)
 D=-B
 return A,B,C,D

def exact_amp2_provisional(ns,nt,mu):
 """Inherited unresolved 2p pole+crossed conditional average."""
 A,B,C,D=_conditional_denominators(ns,nt,mu)
 return conditional_provisional_mean_amplitude_squared(A,B,C,D)

def exact_amp2(ns,nt,mu,*,amplitude_lane='full'):
 """Conditional scalar amplitude mean for the selected atomic lane.

 ``full`` is the PR-03 bound+continuum COM--KHW production lane.
 ``provisional_2p`` retains the inherited PR-01 reference without
 contaminating the production default.
 """
 A,B,C,D=_conditional_denominators(ns,nt,mu)
 if amplitude_lane=='full':
  return conditional_full_scalar_mean_amplitude_squared(A,B,C,D)
 if amplitude_lane in {'full_minus_provisional','amplitude_delta'}:
  return conditional_full_minus_provisional_mean_amplitude_squared(A,B,C,D)
 if amplitude_lane in {'provisional_2p','provisional'}:
  return conditional_provisional_mean_amplitude_squared(A,B,C,D)
 raise ValueError(
  "amplitude_lane must be 'full', 'full_minus_provisional', or "
  "'provisional_2p'"
 )

def logSmj(ns,nt,mu):
 ks=h*ns/(M*c*c);kt=h*nt/(M*c*c);delta=ks-kt;transfer2=2*ks*kt*(1-mu);q=np.sqrt(delta*delta+transfer2);root=np.sqrt(transfer2)/q;chi=np.sqrt(transfer2);sqrtterm=np.sqrt(1+chi*chi/4);sqrtminus=chi*chi/4/(sqrtterm+1);gminus=(1/root)*sqrtminus+(delta/q)**2/(root*(1+root))-delta/2
 return -zeta*gminus-np.log(2*q*scaledK2)

def baseline_amp2(xs,xt,mu):
 ct=math.sqrt((1+mu)/2);A=-(xs+xt)*dnu/2;B=np.full_like(A,dnu/math.sqrt(2)*ct);return (.5*f*nu_abs)**2*lor_mean(A,B,gamma)
def logSmb_hummer(xs,xt,mu):
 s=math.sqrt((1-mu)/2);q=2*h*nu_abs/(M*c*c)*s;delta=h*dnu*(xs-xt)/(M*c*c);return -.5*math.log(2*math.pi*theta)-math.log(q)-delta*delta/(2*theta*q*q)

def cell_nodes(idx,n):
 z,w=leggauss(n);lo=xedges[idx];hi=xedges[idx+1];return .5*(hi-lo)*z+.5*(hi+lo),.5*(hi-lo)*w

def pi_norm(idx,n=64):
 x,w=cell_nodes(idx,n);nu=nu_abs+x*dnu;return float(np.sum(w*nu*nu*np.exp(-beta*h*nu)))

def pair_freq_integral_uv(target,source,mu,kind='exact',nb=32,nl=80,nv=28,local_half=.05,amplitude_lane='full'):
 at,bt=xedges[target],xedges[target+1];as_,bs=xedges[source],xedges[source+1];umin=.5*(at+as_);umax=.5*(bt+bs);delta=gamma/dnu
 breaks=[umin,umax,.5*(at+bs),.5*(bt+as_)]
 if umin<0<umax:breaks += [max(umin,-local_half),0.,min(umax,local_half)]
 breaks=sorted(set(round(float(x),15) for x in breaks if umin-1e-14<=x<=umax+1e-14))
 un=[];uw=[]
 for lo,hi in zip(breaks[:-1],breaks[1:]):
  if hi-lo<1e-14:continue
  if abs(lo)<=local_half+1e-14 and abs(hi)<=local_half+1e-14 and umin<0<umax:
   z,w=leggauss(nl);tl=math.atan(lo/delta);th=math.atan(hi/delta);tt=.5*(th-tl)*z+.5*(th+tl);uu=delta*np.tan(tt);ww=.5*(th-tl)*w*delta/np.cos(tt)**2
  else:
   z,w=leggauss(nb);uu=.5*(hi-lo)*z+.5*(hi+lo);ww=.5*(hi-lo)*w
  un.extend(uu);uw.extend(ww)
 zv,wv=leggauss(nv);result=0.
 for u,wu in zip(un,uw):
  vmin=max(at-u,u-bs);vmax=min(bt-u,u-as_)
  if vmax<=vmin:continue
  vv=.5*(vmax-vmin)*zv+.5*(vmax+vmin);ww=.5*(vmax-vmin)*wv;xt=u+vv;xs=u-vv;ns=nu_abs+xs*dnu;nt=nu_abs+xt*dnu
  if kind=='exact':val=np.exp(-beta*h*ns+logSmj(ns,nt,mu))*ns*nt*exact_amp2(ns,nt,mu,amplitude_lane=amplitude_lane);const=const_exact
  else:val=np.exp(-beta*h*ns+logSmb_hummer(xs,xt,mu))*ns*ns*baseline_amp2(xs,xt,mu);const=const_base
  result += 2*wu*np.dot(ww,val)
 return const*result

def pair_conductance(target,source,lane='production',kind='exact',amplitude_lane='full'):
 pars={'coarse':(12,64,16,16,40,16),'production':(20,128,32,28,72,28),'reference':(28,192,48,40,112,40)}[lane]
 ob,om,of,nb,nl,nv=pars;total=np.zeros(7)
 # back c with uv adaptive
 z,w=leggauss(ob);cm=math.sqrt(.005);cc=.5*cm*(z+1);cw=.5*cm*w
 for q,ww in zip(cc,cw):
  mu=-1+2*q*q;freq=pair_freq_integral_uv(target,source,mu,kind,nb,nl,nv,amplitude_lane=amplitude_lane);total += 2*q*ww*.75*(1+mu*mu)*np.array([eval_legendre(l,mu) for l in range(7)])*freq
 # middle and forward use UV too for robust geometry; lower orders okay
 z,w=leggauss(om);lo=-.99;hi=.999;mus=.5*(hi-lo)*z+.5*(hi+lo);mws=.25*(hi-lo)*w
 for mu,ww in zip(mus,mws):
  freq=pair_freq_integral_uv(target,source,float(mu),kind,nb//2,nl//2,nv//2,amplitude_lane=amplitude_lane);total += ww*.75*(1+mu*mu)*np.array([eval_legendre(l,mu) for l in range(7)])*freq
 z,w=leggauss(of);tm=math.sqrt(.001);tt=.5*tm*(z+1);tw=.5*tm*w
 for q,ww in zip(tt,tw):
  mu=1-q*q;freq=pair_freq_integral_uv(target,source,float(mu),kind,nb//2,nl//2,nv//2,amplitude_lane=amplitude_lane);total += q*ww*.75*(1+mu*mu)*np.array([eval_legendre(l,mu) for l in range(7)])*freq
 return total

PRODUCTION_LANE = {
    "ob": 18,
    "om": 112,
    "of": 28,
    "nb": 30,
    "nl": 80,
    "nv": 26,
    "nf": 18,
}
REFERENCE_LANE = {
    "ob": 36,
    "om": 240,
    "of": 64,
    "nb": 52,
    "nl": 144,
    "nv": 48,
    "nf": 40,
}


def _pair_frequency_integral(
    target: int,
    source: int,
    mu: float,
    *,
    kind: str,
    nb: int,
    nl: int,
    nv: int,
    local_half: float = 0.05,
    amplitude_lane: str = "full",
) -> float:
    """Two-cell u-v integral with geometric and resonance breakpoints."""
    at, bt = xedges[target], xedges[target + 1]
    a_s, b_s = xedges[source], xedges[source + 1]
    u_min = 0.5 * (at + a_s)
    u_max = 0.5 * (bt + b_s)
    pole_scale = gamma / dnu

    breakpoints = [
        u_min,
        u_max,
        0.5 * (at + b_s),
        0.5 * (bt + a_s),
    ]
    if u_min < 0.0 < u_max:
        breakpoints += [
            max(u_min, -local_half),
            0.0,
            min(u_max, local_half),
        ]
    breakpoints = sorted(
        set(
            round(float(value), 15)
            for value in breakpoints
            if u_min - 1.0e-14 <= value <= u_max + 1.0e-14
        )
    )

    u_nodes: list[float] = []
    u_weights: list[float] = []
    for left, right in zip(breakpoints[:-1], breakpoints[1:]):
        if right - left < 1.0e-14:
            continue
        use_tangent = (
            u_min < 0.0 < u_max
            and abs(left) <= local_half + 1.0e-14
            and abs(right) <= local_half + 1.0e-14
        )
        if use_tangent:
            nodes, weights = leggauss(nl)
            theta_left = math.atan(left / pole_scale)
            theta_right = math.atan(right / pole_scale)
            theta = (
                0.5 * (theta_right - theta_left) * nodes
                + 0.5 * (theta_right + theta_left)
            )
            values = pole_scale * np.tan(theta)
            transformed_weights = (
                0.5
                * (theta_right - theta_left)
                * weights
                * pole_scale
                / np.cos(theta) ** 2
            )
        else:
            nodes, weights = leggauss(nb)
            values = 0.5 * (right - left) * nodes + 0.5 * (right + left)
            transformed_weights = 0.5 * (right - left) * weights
        u_nodes.extend(values.tolist())
        u_weights.extend(transformed_weights.tolist())

    v_nodes, v_weights = leggauss(nv)
    result = 0.0
    for u_value, u_weight in zip(u_nodes, u_weights):
        v_min = max(at - u_value, u_value - b_s)
        v_max = min(bt - u_value, u_value - a_s)
        if v_max <= v_min:
            continue
        v_values = (
            0.5 * (v_max - v_min) * v_nodes
            + 0.5 * (v_max + v_min)
        )
        weights = 0.5 * (v_max - v_min) * v_weights
        x_target = u_value + v_values
        x_source = u_value - v_values
        nu_source = nu_abs + x_source * dnu
        nu_target = nu_abs + x_target * dnu

        if kind == "exact":
            values = (
                np.exp(
                    -beta * h * nu_source
                    + logSmj(nu_source, nu_target, mu)
                )
                * nu_source
                * nu_target
                * exact_amp2(
                    nu_source, nu_target, mu, amplitude_lane=amplitude_lane
                )
            )
            normalization = const_exact
        elif kind == "hummer":
            values = (
                np.exp(
                    -beta * h * nu_source
                    + logSmb_hummer(x_source, x_target, mu)
                )
                * nu_source**2
                * baseline_amp2(x_source, x_target, mu)
            )
            normalization = const_base
        else:
            raise ValueError("kind must be 'exact' or 'hummer'")

        result += 2.0 * u_weight * float(np.dot(weights, values))

    return normalization * result


def integrate_unordered_pair(
    target: int,
    source: int,
    *,
    lane: str = "production",
    kind: str = "exact",
    ell_max: int = 6,
    amplitude_lane: str = "full",
) -> np.ndarray:
    """Return one canonical pair conductance vector through ell_max.

    ``amplitude_lane='full'`` is the PR-03 production default; the
    explicit ``'provisional_2p'`` lane is retained for transition parity.
    """
    if target == source:
        raise ValueError(
            "same-cell coherent-forward angular block is a separate distributional lane"
        )
    if not (0 <= target < ncell and 0 <= source < ncell):
        raise ValueError("cell index outside the 17-cell core")
    parameters = PRODUCTION_LANE if lane == "production" else REFERENCE_LANE
    total = np.zeros(ell_max + 1)

    # Backscatter endpoint: use the u-v/tangent cell quadrature.
    nodes, weights = leggauss(parameters["ob"])
    c_max = math.sqrt(0.005)
    c_values = 0.5 * c_max * (nodes + 1.0)
    c_weights = 0.5 * c_max * weights
    for c_value, weight in zip(c_values, c_weights):
        mu = -1.0 + 2.0 * c_value**2
        frequency_integral = _pair_frequency_integral(
            target,
            source,
            mu,
            kind=kind,
            nb=parameters["nb"],
            nl=parameters["nl"],
            nv=parameters["nv"],
            amplitude_lane=amplitude_lane,
        )
        phase = 0.75 * (1.0 + mu**2)
        total += (
            2.0
            * c_value
            * weight
            * phase
            * np.asarray([eval_legendre(ell, mu) for ell in range(ell_max + 1)])
            * frequency_integral
        )

    # The regular and coherent-forward pieces are smooth for off-diagonal
    # frequency cells after the endpoint split; a tensor cell rule is much
    # faster than repeating the u-v adaptive construction at every mu node.
    nf = parameters["nf"]
    source_x, source_w = cell_nodes(source, nf)
    target_x, target_w = cell_nodes(target, nf)
    x_source = np.broadcast_to(source_x, (nf, nf))
    x_target = np.broadcast_to(target_x[:, None], (nf, nf))
    cell_weights = target_w[:, None] * source_w[None, :]
    nu_source = nu_abs + x_source * dnu
    nu_target = nu_abs + x_target * dnu

    def add_mu_nodes(mu_values, mu_weights):
        nonlocal total
        for mu, weight in zip(mu_values, mu_weights):
            if kind == "exact":
                values = (
                    np.exp(
                        -beta * h * nu_source
                        + logSmj(nu_source, nu_target, float(mu))
                    )
                    * nu_source
                    * nu_target
                    * exact_amp2(
                        nu_source,
                        nu_target,
                        float(mu),
                        amplitude_lane=amplitude_lane,
                    )
                )
                normalization = const_exact
            elif kind == "hummer":
                values = (
                    np.exp(
                        -beta * h * nu_source
                        + logSmb_hummer(x_source, x_target, float(mu))
                    )
                    * nu_source**2
                    * baseline_amp2(x_source, x_target, float(mu))
                )
                normalization = const_base
            else:
                raise ValueError("kind must be 'exact' or 'hummer'")

            frequency_integral = normalization * float(
                np.sum(cell_weights * values)
            )
            phase = 0.75 * (1.0 + mu**2)
            total += (
                weight
                * phase
                * np.asarray(
                    [eval_legendre(ell, mu) for ell in range(ell_max + 1)]
                )
                * frequency_integral
            )

    nodes, weights = leggauss(parameters["om"])
    lower, upper = -0.99, 0.999
    add_mu_nodes(
        0.5 * (upper - lower) * nodes + 0.5 * (upper + lower),
        0.25 * (upper - lower) * weights,
    )

    nodes, weights = leggauss(parameters["of"])
    t_max = math.sqrt(0.001)
    t_values = 0.5 * t_max * (nodes + 1.0)
    t_weights = 0.5 * t_max * weights
    add_mu_nodes(1.0 - t_values**2, t_values * t_weights)

    return total


def physical_equilibrium_cell_weight(cell: int) -> float:
    """Physical dilute equilibrium mode density in m^-3, common 4pi included."""
    return 8.0 * math.pi * dnu / c**3 * pi_norm(cell)


def pointwise_hummer_limit_ratio(
    x_target: float,
    x_source: float,
    mu: float,
) -> float:
    """No-recoil line-frequency dynamic-structure representation / Hummer RII."""
    if not -1.0 < mu < 1.0:
        raise ValueError("pointwise audit excludes distributional endpoints")
    nu_source = nu_abs + x_source * dnu
    nu_target = nu_abs + x_target * dnu
    pair_value = (
        const_base
        * math.exp(-beta * h * nu_source + float(logSmb_hummer(
            np.asarray([x_source]), np.asarray([x_target]), mu
        )[0]))
        * nu_source**2
        * float(baseline_amp2(
            np.asarray([x_source]), np.asarray([x_target]), mu
        )[0])
    )

    damping = A21 / (4.0 * math.pi * dnu)
    hummer = (
        1.0
        / (math.pi * math.sqrt(1.0 - mu**2))
        * math.exp(
            -(x_target - x_source) ** 2 / (2.0 * (1.0 - mu))
        )
        * float(
            np.real(
                wofz(
                    (x_target + x_source)
                    / math.sqrt(2.0 * (1.0 + mu))
                    + 1j
                    * damping
                    * math.sqrt(2.0 / (1.0 + mu))
                )
            )
        )
    )
    rate_scale = nH * c * math.pi * re * c * f / dnu
    hummer_conductance_density = (
        rate_scale
        * hummer
        * nu_source**2
        * math.exp(-beta * h * nu_source)
    )
    return pair_value / hummer_conductance_density
