# DV2-D: Bianchi-V class-B polarized generator and measure

Status COMPLETE_SCOPED_INSTANTANEOUS_BIANCHI_V_CLASS_B_GENERATOR_AND_MEASURE. Additive research only, parent PR202 / 932bcd8f14c7f04b709007478ec9519a68457172. No production/owner changes, merge, new IVPs or historical campaign reruns.

## Exact local contracts

Signature(-,+,+,+), photon propagation n, geodesic/nonrotating normal tetrad. A=c*a_structure is a rate, not acceleration. N=0. Bolometric full I/E/B/V, cold rest-electron Thomson nu=n_e* sigma_T c. All numerical rates multiply T_star for u=t/T_star. Physical carrier is Hermitian S+iW, stored by P8 as real S+W. Q+iU=sum(E+iB) spin+2 Z in the pinned DL2 convention.

Let s=sigma:nn and alpha=A.n. Direction v=-sigma n+s n-A+alpha n, log-energy rate=-(H+s), screen Wdot=(v nT-n vT)W. Sphere divergence=3s+2alpha. Thus dlog(Jcal*r^3*V/Vi)/dt=2alpha, not zero. The canonical compatible metric is -c2dt2+ax2e^-2bz dx2+ay2e^-2bz dy2+az2 dz2, A_z=cb/az and dot A_z=-(H+sigma_zz)A_z. Coframe consistency is not Einstein consistency.

Analytic harmonic operator L_A=grad(alpha).D_spin. Rank1 Gaunt prefactor [lp(lp+1)+2-l(l+1)]/2, no quadrature fitting or P8 callbacks in construction. Same-channel deltaell=+/-1; E/B deltaell=0. It obeys L+Ldagger=2 multiplication_by_alpha, not anti-Hermiticity.

rho=int I, q=int I n=energyflux/c, pi=int I(nn-delta/3):

    rho_dot=-4Hrho-sigma:pi+2A.q
    q_dot=-(4H+nu)q-sigmaq+3piA

Independent coordinate Christoffels give c div q=-2A.q and c div pressure=-3piA. Homogeneous frame components are not divergence-free; these terms do not violate local energy-momentum conservation. A prescribed electron bath does not close the total four-force.

## Evidence

11 pytest items passed. One new validator run: 828 all-m basis rows on grids8x16,12x24,20x40 and3 A vectors;9 mixed shear/collision rows;9 geometric,9 energy/flux/L2,6 adjoint/selection,9 elementary frozen-map spots,3 gain-null and4 extra signed-strength rows. Fixed algebra2e-11, finite-difference area5e-8.

Max basis2.84217e-14,mixed4.48530e-14,direction/screen/coordinate3.33067e-16,energy4.26326e-14,flux6.74460e-14,L2-rate2.80331e-15,adjoint1.11022e-16. This is roundoff-level agreement, not a convergence order. No finite-time kinetic IVP was run.

Canonical A_z=.7: I10 -> dot I00=.808290376865476, dot I20=-.361478445646026; E22 -> dot B2,-2=-.466666666666666. Initial B22=.1 has M=0 but dot Mxy=.0523132513530473 and normdotM=.0739821095553122. Initial positive pair checked, not time-evolved. No intensity-only polarization production. Two Wolfram calls independently check sphere/source coefficients and coordinate divergences; not independent-model review. Native subagent and fresh model review NOT_RUN.

Frozen A_z=a gives D=cosh(at)-mu0sinh(at), mu=(mu0cosh(at)-sinh(at))/D, nperp=nperp0/D, r=1 and Jcal=D^-2. The changing angular measure is not a Doppler energy factor. Omitting the class-B Jacobian, A moment terms, spin connection or full source-null input is detected by the recorded controls.

## Reproduction and preservation

Git publishes exact tested core/tests and four pinned vendor files, this summary and selected contracts/results/DAG. The complete immutable ZIP identified in DELIVERY.json additionally holds the complete verifier, Korean report/handoff, all raw rows, CAS, logs, plot and hashes. The selected Git tree is not claimed as full archive byte identity.

From this directory:

    OPENBLAS_NUM_THREADS=1 python -m pytest tests/test_class_b.py -q

For the full scientific validator use the archive and run python verify_dv2d.py. For saved-evidence verification only, use verify_saved.py from the archive. Do not repeat previous science merely for delivery. SourceMap records exact vendors, parent and archive identity.

## Next / non-promotion

Upper count6/15 remains source mapping plus scoped complete nodes. DV2 upperPARTIAL; DV2-D subgate complete, DV2-Eready: frozen Bianchi-V exact-characteristic full-polarized finite-time comparison with raw angular weights and unknown-source Volterra. Keep full initial B22 and all tail ownership. Spatial averaging,BF1,Einstein feedback,classB finite-time,generic tilt,spectra/recoil,productionRust,global bounds and observer sky remain open. production_ready=false;overall_physical_completion=null.
