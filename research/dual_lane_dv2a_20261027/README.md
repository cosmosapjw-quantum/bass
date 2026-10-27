# DV2-A: full-polarized Bianchi-II instantaneous curvature

COMPLETE_SCOPED_INSTANTANEOUS_BIANCHI_II_GENERATOR. Stacked on DV1-B recovery PR198/f8d9b9dc4761187f0becc65f5a5338d816d9562e. No production/owner edits, old science reruns, new IVPs or merge. Native subagent and independent-model review NOT_RUN.

## Construction

Physical normal time, (-+++), photon propagation direction, N=c*n_structure=kappa*a*a^T with |a|=1, A_struct=0. All rates multiply T_star for u=t/T_star. N is not scalar curvature or N/H. DL2 spin convention Q+iU=sum(E+iB) spin+2 Z; P8 real S+A represents Hermitian S+iA.

Pure curvature direction and screen rates: v=(Nn) cross n, Omega=Nn-(trN/2)n, dot W=Omega cross W. For axis z, theta is constant and dot phi=kappa cos(theta). Relative screen rotation is -kappa/2, giving L_s f=-kappa cos(theta)partial_phi f-i*s*kappa*f/2. Finite curvature is not expanded. Matrices use the exact cosine recurrence, ordinary SO(3) representation rotations and canonical real transform without angular quadrature/direct RHS calls. Direct comparison uses independently differentiated Cartesian carrier and pinned P8 connection.

The cosine recurrence has offdiagonal C_l=sqrt((l^2-m^2)(l^2-s^2)/(l^2(4l^2-1))) and diagonal -s*m/[l(l+1)]. Thus curvature same-type couplings have delta ell=+/-1, E/B couplings delta ell=0. This differs from shear. The generator is anti-Hermitian for angular L2; no finite-L accuracy/positivity theorem follows.

E20=1 gives dot B20=-kappa. I11=1 gives dot I2,-1=kappa/sqrt5. At kappa=.7, direct results are-.6999999999999996 and.31304951684997046. Removing intrinsic screen rotation gives wrong B20=-.2 (difference.5). Unpolarized radiation is not polarized by curvature alone. Wolfram direct integrals confirm these coefficients and the screen rate. No observational parity-violation or novelty claim.

Initial B20=.1 is gain-source-null, but at kappa=.7 curvature yields dot E20=.07 and dot M_STF=.07 sqrt(4pi/5)U20, norm.110973164332968. Verified on three grids, including the positive physical pair I=2 versus I=2,B20=.1. Retain full initial carrier in future memory equations. M is scattering source, not full stress-energy.

## Evidence

12 unique pytest items.828 basis rows,9 mixed total-RHS rows,9 direction/screen rows,9 energy/flux/L2 rows,6 structure rows,3 signed-amplitude rows plus3 gain-null rows. Fixed gate2e-11. Max basis/mixed differences1.0436e-14/3.4417e-14; geometry2.2204e-16; energy1.8247e-16; flux3.2006e-16; L2-rate7.3466e-16. Pure curvature energy is conserved, while dot q_a=epsilon_abc N_bd pi_dc. Entire generated instantaneous output is retained; this is not a finite-time closure. Roundoff-level agreement is not a convergence-rate measurement.

Run here:

    OPENBLAS_NUM_THREADS=1 python -m pytest tests/test_curvature.py -q
    OPENBLAS_NUM_THREADS=1 python gain_null_check.py

The complete immutable35-file ZIP identified by DELIVERY.json additionally includes verify_dv2a.py, verify_saved.py, full raw evidence, Korean derivation/handoff, source map, exact detailed DAG, CAS, logs, figure and checksums. Those full-campaign commands are run from the archive, not this selected Git subset. The four vendor blobs are preserved exactly; analytic and direct new code plus tests match executed local files.

## Next

Upper DV2 remains PARTIAL;6/15 completed-or-source-mapped upper nodes, plus completed DV2-A subgate. production_ready=false, physical completion=null. DV2-B: frozen ultrastatic Bianchi-II finite-time benchmark using exact collisionless f_s(t,theta,phi)=exp(-i*s*kappa*t/2)f_si(theta,phi-kappa*cos(theta)*t), then rest-Thomson same-physics three-lane comparison. Do not assume p=A(t)q in curvature transport; expose characteristic/screen/angular-Jacobian suppliers. ClassB, generic electron tilt, spectra/recoil, EFE backreaction, observer-sky inference and spatial averaging remain open. No automatic merge.
