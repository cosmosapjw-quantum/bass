# Finite LINE01 exchange into a BASS packet state

## Result

An existing source-qualified REC atomic population map admits stable integrated
gross emission and absorption counts. For zero prescribed incoming occupation,
its finite emission can be represented by 14 positive BASS photon packets and
charged to the same finite atomic excitation stock. This is a local frozen
source substep. The actual source, frame, clock, energy partner and remaining
external boundary dependence are fixed in CONTRACT.md.

The independent derivation and source inspection are in reviews/THEORY_REVIEW.md.
Actual symbolic code and response are in evidence/. All 19 residual groups were
zero, measured kernel wall0.128027s and CPU0.1274340000000005s. Code acceptance is
a separate stage.

## Population and integrated counts

Write b=g+1, F=1+bf, x_e=gf/F, d_e=g/F, k=8*pi*H/(N*lambda^3),
eta=k*F/d_e. The existing owner solves
dx/dt=-k*F*(x-x_e)/(g-b*x) on 0<=x<g/b, with N,H>0, f>=0.
The physical domain and the whole-path thick-opacity gate are mandatory.

For y0=x0-x_e and z0=-b*y0/d_e, define v>=0 by
omega=eta*dt=v+z0*(1-exp(-v)). Its derivative is
1+z0*exp(-v)>0, establishing a unique monotone map.
The stable population increment is dx=-y0*a(v), a(v)=-expm1(-v).

Integrating the original rates N*k*(1+f)*x/(g-b*x) and
N*k*g*f*(1-x)/(g-b*x), use
dt/dv=[d_e-b*y0*exp(-v)]/(k*F).
The common population-dependent denominator cancels. The resulting positive
forms are
D_down=N*(1+f)/F*[x0*a+x_e*(v-a)],
D_up=N*g*f/F*[(1-x0)*a+(1-x_e)*(v-a)].

Both are nonnegative for physical data. Use the stable owner dx for
D_net=-N*dx, since subtracting near-equal gross counts is poorly conditioned.
The equivalent forms N*(1+f)*(k*f*dt-dx) and
N*f*(k*(1+f)*dt-dx) are algebraic checks, not the primary floating algorithm.

At exact LTE, the owner's u=0 is a shortcut for a zero net packet. Gross
integration must instead use v=omega, so both gross counts equal
N*k*f*(1+f)*dt. At x0=0, the emission is quadratic in a small duration:
v-a=v^2/2-v^3/6+..., which is evaluated without subtracting leading terms.
These two cases distinguish a correct gross-event ledger from a net-only one.

For frozen parameters the autonomous map is a semigroup. Its gross counts
compose additively because they are time integrals of the same local rates.
No time-history approximation is certified by that local semigroup property.

## Angular representation and finite units

Six signed axes of weight1/15 and eight cube corners of weight3/40 reproduce
the sphere's second and fourth moments: <n_i*n_j>=delta_ij/3 and
<n_i*n_j*n_k*n_l>=(delta_ij*delta_kl+delta_ik*delta_jl+
delta_il*delta_jk)/15. Sign symmetry cancels odd moments.

For any symmetric STF S admitted by the continuum source gate,
q(n)=1+n.S.n is positive. Multiplying each base weight by q gives number1,
zero flux and spatial moment I/3+2*S/15. This is a standard degree5 cubature
construction applied to the quadratic thick source; no new cubature/no-go
novelty is claimed.

For f=0, D_up=0 and 0<=D_net<=N*x0. The actual upper population therefore
provides all photon energy. With alpha_L=kappa_grav*L^2,
Delta rho_gamma=alpha_L*E*D_net and Delta rho_atom=-Delta rho_gamma.
Choose photon momentum k_j=E*n_j/(c*Pstar) and state weight
Delta w_j=alpha_L*c*Pstar*D_net*A_j*q_j. Actual kinetic moments give
Delta p_gamma=Delta rho_gamma/3 and
Delta pi_gamma=Delta rho_gamma*(2*S/15).

The dimensionless state increment uses L^2; integrating the interval-average
source U=kappa_grav*L^3*(E*D_net/dt)/c over Delta tau=c*dt/L gives the same
increment. Source.pi is the resulting state stress, not an event-rate moment.
After the interval is applied, its U/J must not be charged again.

At fixed geometry, the actual BASS Hamiltonian/Codazzi constraints depend on
total rho/flux. Equal and opposite sector changes preserve the existing
constraint residual. The changed photon pressure/pi affect the subsequent RHS.
This observation does not construct a constraint-satisfying initial geometry.

## Domain of the result

General f gross counts remain a prescribed-boundary calculation. The existing
f_plus input does not identify a finite photon bath; closed absorption needs
a real bath spectrum/occupation and a receiver with matched history and clock.
This is an unresolved input and coupling obligation, not an impossibility
theorem. Current commit is canonical rest frame only.

The source's finite-opacity population/net-energy/STF envelopes remain
available with their original FLOAT_NOT_INTERVAL qualification. They are not
automatically gross-channel relative bounds. The 14 packets exactly match
specified rest N/T moments; they do not reproduce arbitrary higher multipoles
or the observer-dependent event K(u) denominator.

A tiny stable analytic increment may be smaller than the representable stock
change. The finite transaction must reject that unresolved update or report a
properly bounded representation error; this contract chooses explicit rejection.
No population clipping or manufactured donor bath is used.

## External context and evidence reuse

SciSpace was used for discovery; adopted literature is primary.
Chluba and Sunyaev, arXiv:0810.1045, DOI10.1051/0004-6361/200811100,
studies time-dependent Ly-alpha escape corrections. It motivates retaining
the distinction between a frozen local source step and full radiative history;
it is not the source of the positive formulas derived here.
The current arXiv abstract was actually read; a separate 0903.4925 HTML request
failed and was not substituted with invented text.

The B3a event-measure result and original failed/repair records are reused.
The collisionless G1B radial reduction is unaffected. Recovered S1/S2 bytes,
110 payload validation and the curved process exit0 are historical evidence.
Exact contemporaneous pytest argv/cwd remain unknown. No old execution was
reconstructed by running a new command.

