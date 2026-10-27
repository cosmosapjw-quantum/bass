# DV2-F: coframe-compatible expanding Bianchi-V transport

Status: COMPLETE_SCOPED_COFRAME_COMPATIBLE_EXPANDING_BIANCHI_V_PROVIDER. Parent PR206 commit06579e3f6d580ae775a98eaf6b8fc4562bc5a081. Additive research only, no production or prior campaign changes.

Choose positive diagonal scale factors in ds2=-c2dt2+ax2 exp(-2n0z)dx2+ay2 exp(-2n0z)dy2+az2dz2. A_z=c*n0/az and dotA_z=-(H+sigma_zz)A_z follow, not independent prescribed histories. Coframe consistency is not EFE consistency. Photon propagation directions, normal proper time, all numeric rates times T_star, u=t/T_star. The physical carrier retains the pinned real S+A encoding of Hermitian S+iA and Q+iU=sum(E+iB) spin+2 real-CS convention.

Direction v=-sigma.n+(sigma_nn+A.n)n-A; log-energy derivative=-(H+sigma_nn); screen E_dot=(v n^T-n v^T)E; log-angular-Jacobian derivative=3sigma_nn+2A.n. Jac*r3*volume/volume_i*exp[-2n0(z-zi)]=1. No class-A measure substitution, unit-redshift assumption or weight renormalization.

Independent coordinate Hamiltonian rays and a tangent-map area ODE verify geometry; neither uses the area scalar equation. Exact frozen, A=0 Bianchi-I and conformal-ultrastatic limits retained. Conformal free dipole rho=a^-4 rho_frozen(eta), q=a^-4 q_frozen(eta) checks expansion plus spatial flux: rho_dot+4Hrho=2A.q. No claim about global total energy.

SourceMemory and VolterraHistory reused byte-for-byte. New Cartesian ODE calls pinned P8; analytic harmonic Galerkin and unknown-source Volterra evolve independently without sharing source histories. Source M is not the full carrier or stress-energy. Full initial gain-null radiation stays in the memory term.

## Actual evidence

10 unique pytest items; one scientific invocation:9 geometry,7 direct,5 harmonic,4 Volterra,1 coordinate,1 tangent IVPs and2 exact frozen providers. Test calls separate, historical reruns0. An optional streaming host request failed before any command/science execution; ordinary synchronous execution succeeded. NumPy serialization was checked before science and each phase checkpoints raw rows.

Coordinate direction/redshift differences3.535e-13/1.434e-13; tangent-area5.750e-13; coordinate-volume invariant4.037e-13. Five Wolfram symbolic residuals zero, not an independent-model review. Native subagent/independent-model review NOT_RUN.

Main u0..0.4:16/32/64-panel source differences1.66494e-9/1.04079e-10/6.52989e-12; final carrier1.25033e-12. L4/6/8 source errors1.01824e-4/1.89255e-7/1.82409e-10 while full-carrier errors6.50062e-3/6.86480e-4/7.85629e-5. Source precision does not certify the sky. Direct angular gaps8->12 /12->20 are4.15157e-8/7.42312e-13; ODE and off-grid interpolation are separate. Signed initial B22=.1 returns Mxy(.4)=.008812430724976969, not an extra integrated positive-pair campaign.

## Reproduction and archive scope

From this directory run:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m pytest tests -q

The immutable full archive additionally contains verify_dv2f.py, verify_saved.py, full raw results, detailed Korean derivation/contract/DAG/handoff, CAS, logs and figures. Run the complete scientific validator only from that archive; do not rerun it merely for delivery. Selected Git publication is not the complete archive. DELIVERY.json resolves archive bytes and actual provider receipts. All eight vendor files are unchanged and source-matched to the parent.

## Remaining scope and next

Diagonal fixed-axis prescribed geometry only. No production Rust, EFE feedback, generic tilt, spectra/recoil, general positivity or tail theorem, spatial projection or observer-sky admission. Scoped/source-mapping count6/15 and upper DV2PARTIAL remain, not physical completeness. Next existing BF1: exact physical-carrier spatial projection on a fixed-slicing Bianchi-I periodic domain. Do not turn outstanding generic tilted DV2/KM2 obligations into a new blanket prerequisite. No merge or automatic next-node execution.
