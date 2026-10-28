# B3h forced Lyalpha response: finite changes and shared rate ownership

UNIT=BASS_B3H_FORCED_LYA_RESPONSE_20261028
BASE_F=ef4864adc72a95e795a695548102ae3482f1dfbc
BRANCH=research/bass-b3h-forced-lya-20261028
Original canonical DAG28/88,delta0,AUTO_NEXT_NODE=false.
Status: implementation-verified conditional research companion; distinct-author R6/C9 NOT_RUN. Work18/20. Parent220/217/215/212 review holds remain separate. Actual forcing/error budgets remainnull, globalphysicalcompletionnull,L4false.

## Exact finite-change identity
Proper time is seconds; p is dimensionless, n0=N_H/V0 is m^-3, M=A+R*E22 is s^-1. The inherited common frame/volume and signature(-,+,+,+) are preserved. No new natural-units convention is introduced. The baseline is p'=b-Mp, z'=a+n0*R*p2. A comparison obeys phat'=b+delta_b-(M+delta_A+delta_R*E22)phat+r_p and zhat'=a+delta_a+n0*(R+delta_R)phat2+r_z. delta_A excludes the shared delta_R term.

Let e=phat-p, s=delta_R*phat2, f=delta_b-delta_A*phat+r_p and g=delta_a+r_z. Direct subtraction gives e'=-M e+f-e2*s and d'=r^T e+n0*s+g, r=n0 R e2. The backward output adjoint h'=M^T h-r, h(D)=0 satisfies

    (h^T e)'=-r^T e+h^T f-h2*s.

Integrate to obtain

    d(D)-d(0)=h(0)^T e(0)+integral h^T f
                              +integral(n0-h2)*s+integral g.

The comparison state phat makes this an exact finite-change identity, not a first-order derivative. M(t) need not commute at different times. A changed density, clock or frame needs its own source/output transformations.

If the same channel has b=b_other+R*qdrive*e2 and a=a_other-n0*R*qdrive with a common fixed drive, group s_net=delta_R*(phat2-qdrive) instead. The same complement kernel applies; positive delta_R alone does not imply a positive net count. A changed drive requires its extra terms. This companion supplies no physical drive-error history.

## Signed forcing-window consumer
Reuse the saved whole-cell v,w,gamma,N,Rmax certificate: M^T v<=r<=M^T w, 0<=v<=w, gamma>0, w2<=N. For remaining horizon tau,

    l_i(tau)=max(0,v_i-max(v)*(1+gamma*tau/8)^(-8)),
    u_i(tau)=min(w_i,N*Rmax*tau).

For support[A,B] in[0,D], the population-port kernel is[l_i(D-B),u_i(D-A)] and the shared-rate kernel is[N-u2(D-A),N-l2(D-B)]. These envelopes are monotone; the actual nonautonomous adjoint need not be. Shared loss and output must be combined before taking absolute values: N-h2 is not N+h2.

For a nonnegative kernel L<=k<=U and integrated positive/negative masses P in[Pl,Pu],Q in[Ql,Qu], integral k*f lies in[L*Pl-U*Qu,U*Pu-L*Ql]. Known net m and total variation V>=abs(m) yield P=(V+m)/2,Q=(V-m)/2. Missing variation cannot be set tozero. Records must count each additive source once. A zero-width L1 window cannot have positive mass; no impulsive-source extension is claimed.

The core accepts explicit integers/strings/Fractions, rejects unknown/float/bool sources, checks window/range consistency, and does not estimate physical errors. Supplied whole-domain certificate validity and nonduplicated source coverage remain caller premises. combine(base,[]) deliberately selects zero new forcing; its default direct=(0,0) is not permission to omit an unknown physical g.

## Native requirements, not measured uncertainties
With saved initial interval[J0lo,J0hi], a sufficient strict-negative certificate is

    w1*Bf1+w2*Bf2+N*Bs+Bg < -J0hi.

The Bf/Bs are dimensionless integrated total-variation budgets; Bg is m^-3. Single-port supremum approximations are7.84535836834640e-29,7.30253965882646e-29,3.68542947975197e-31,9.22280514944367e-23m^-3 respectively. They cannot be spent simultaneously: use the joint inequality. Equality certifies only nonpositivity; above means inconclusive, not observed sign reversal. Exact rational PRIMARY is authoritative; REFERENCE has floor/ceil displays, and a rounded-up display must not be used as a safe tolerance.

For the full stored duration, uniform pointwise requirements are about4.59548312813e-38,4.27752260879e-38,2.15877060026e-40s^-1 and5.40233389839e-32m^-3s^-1. These are NOT actual microscopic error measurements. A rate bound alone does not bound Bs without a whole-interval comparison-population bound.

## Actual verification
21unit methods:21failed methods/26assertion events in RED, then identical21/21PASS. Saved-input primary ran once and passed15/15 checks. A separate Decimal80 analytic checker importing no production module passed119/119 checks, including20window fixtures, exact finite-rate output differences and fixed-drive controls. Frozen analytic tolerance1e-60; largest recorded finite-change/drive residual9e-79. Generic noncommuting validity follows from the derivation, not scalar fixtures alone.

Synthetic d=R=1s^-1,delta_R=1s^-1,n0=10m^-3,p0=1,D=2s,drive0 gives direct3.325070826077779 plus induced-state-1.583350979478550 =net1.741719846599229m^-3. Loss-only omission gives the wrong sign. Equal opposite early/late rectangular pulses have net0,TV1 yet output1.501622823373570m^-3. A fixeddrive1,p0=0 example has positive delta_R but net-5.312550198658874m^-3, demonstrating the qualified interpretation.

Explicit Wolfram evaluator returned6scalar zero residuals and a zero-rate-change limit0 without observed warnings. Natural-language context parsing was not evidence. Primary background sources: Baake/Schlaegel arXiv1011.1775 Eq7/Theorem2, and Briat arXiv1204.3554v3 positive-system/copositive context; no literature source supplies native physical error budgets.

Two figures read: a two-port sufficient-budget slice with Bf1=Bg=0, and the synthetic shared-rate decomposition. A first canvas validator falsely included out-of-view automatic tick labels; original images/log/code retained. One explicit-tick/hatch presentation repair passed; scientific values unchanged. No physical print test or distinct-author visual review.

## Reproduction and delivery
From this unit directory, run `python -I -S tests/test_forced.py` for the new unit tests. The immutable full source ZIP additionally contains code/run.py, code/reference.py, code/meter.py, the exact parent PRIMARY, all raw results/logs/figures, complete theory/report and20row stage ledger. Git is the concise core/test projection, not the whole ZIP. Do not run completed commands merely to re-confirm delivery.

Parent PRIMARY135975bytes/SHA2564440b48969a24fa8ba681edc7144ef1a12e1231f856cb485e0d0a6382432c0b9 was copied unchanged from the213389byte parent ZIP/SHA25695f315ad00e981a07471337a3be1ed38baef2755310f48ae0750f9ae58c69e74. No parent ZIP regeneration.

New test/science childCPU0.187093s/wall0.261266480s; wrappersCPU0.005481853s. Known child+two plot attemptsCPU4.731080578s/wall4.946385604s; preparation/import/network/model/preservation costs unknown,not0. Fresh allocation closed. Historical allocations closed,remainingnull,no transfer. No new nativeODE/QSS/B3i,oldcampaign,central/foreign/main write or merge.

S0commitcb4456ea9251f3699a385724d714fa67fd4f8ea9 is actually dual-backed; final actual receipts follow the immutable source ZIP separately.18stage outputs may share two real checkpoints,not18uploads. Next: one distinct-author R6/C9 saved-evidence review of this fixed unit. No automatic next node.
