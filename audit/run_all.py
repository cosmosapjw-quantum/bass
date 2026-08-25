"""
Run the whole BASS audit and write manifest.json.

    cd audit && python run_all.py

Every check is deterministic (explicit seeds).  A rerun that exceeds the
thresholds below is a regression, not noise.
"""
import json, subprocess, sys, os

GENERATOR = {
    'name': 'BASS aggregate audit runner',
    'version': 'rf02a-1.0',
    'source': 'audit/run_all.py',
}

SCRIPTS = [
    ('einstein_frame.py', 'einstein_frame.json'),
    ('r1_jacobi_rotation.py', 'r1_jacobi_rotation.json'),
    ('r2_curvature.py', 'r2_curvature.json'),
    ('fit_einstein.py', 'fit_einstein.json'),
    ('r4_bianchi_constraints.py', 'r4_bianchi_constraints.json'),
    ('r5c_tilt_fit.py', 'r5c_tilt_fit.json'),
    ('r5d_tilt_closed.py', 'r5d_tilt_closed.json'),
    ('r5e_typeIX_D.py', 'r5e_typeIX_D.json'),
    ('d_transport.py', 'd_transport.json'),
    ('d_kinetic.py', 'd_kinetic.json'),
    ('d_matter.py', 'd_matter.json'),
    ('d_optical.py', 'd_optical.json'),
    ('d_vorticity.py', 'd_vorticity.json'),
    ('d_tilted_II.py', 'd_tilted_II.json'),
]

#: acceptance thresholds.  key -> (json file, dotted path, comparison, bound)
THRESHOLDS = [
    ('S3 explicit, class A', 'r2_curvature.json', 'S3_explicit_err_classA', '<', 1e-12),
    ('S3 explicit, class B', 'r2_curvature.json', 'S3_explicit_err_classB_jacobi', '<', 1e-12),
    ('S3 explicit, no Jacobi', 'r2_curvature.json', 'S3_explicit_err_general_noJacobi', '<', 1e-12),
    ('3R closed form', 'r2_curvature.json', 'R3_explicit_err_classB_jacobi', '<', 1e-12),
    ('WE S_pm cross-check', 'r2_curvature.json', 'WE_classA_Splus_Sminus_err', '<', 1e-12),
    ('A-term coeff +2 wins', 'r2_curvature.json', 'A_term_coefficient_scan.coef_+2', '<', 1e-12),
    ('A-term coeff 0 fails', 'r2_curvature.json', 'A_term_coefficient_scan.coef_+0', '>', 1e-3),
    ('A-term coeff +1 fails', 'r2_curvature.json', 'A_term_coefficient_scan.coef_+1', '>', 1e-3),
    ('A-term coeff -2 fails', 'r2_curvature.json', 'A_term_coefficient_scan.coef_-2', '>', 1e-3),
    ('G_00 block', 'fit_einstein.json', 'G00.maxres', '<', 1e-12),
    ('G_0i block', 'fit_einstein.json', 'G0i.maxres', '<', 1e-12),
    ('tr G_ij block', 'fit_einstein.json', 'tr_Gij.maxres', '<', 1e-12),
    ('G_<ij> block', 'fit_einstein.json', 'Gij_tracefree.maxres', '<', 1e-12),
    ('Jacobi propagates', 'r1_jacobi_rotation.json',
     'jacobi_constraint_numeric_Jdot_on_surface', '<', 1e-12),
    ('Omega prime (published)', 'r5c_tilt_fit.json', 'Omega_prime_published_relerr', '<', 1e-12),
    ('P_a identification', 'r5d_tilt_closed.json', 'P_i_maxres', '<', 1e-12),
    ('Euler closed form', 'r5d_tilt_closed.json', 'euler_closed_form_maxres', '<', 1e-12),
    ('explicit v_a prime', 'r5d_tilt_closed.json', 'explicit_v_prime_maxres', '<', 1e-12),
    ('Fbar closed form', 'r5e_typeIX_D.json', 'residuals.Fclosed', '<', 1e-12),
    ('Hbar prime', 'r5e_typeIX_D.json', 'residuals.H', '<', 1e-12),
    ('Sigmabar prime', 'r5e_typeIX_D.json', 'residuals.S', '<', 1e-12),
    ('Nbar prime', 'r5e_typeIX_D.json', 'residuals.N', '<', 1e-12),
    ('Omegabar prime', 'r5e_typeIX_D.json', 'residuals.O', '<', 1e-12),
    ('D-chart Gauss', 'r5e_typeIX_D.json', 'residuals.gauss', '<', 1e-12),
    ('D-chart 3D^2 identity', 'r5e_typeIX_D.json', 'residuals.D2', '<', 1e-12),
    # ---- v1.2 derivation round
    ('Gamma^a_b0 = -Omega', 'd_transport.json', 'D2_Gammaa_b0_equals_minus_Omega', '<', 1e-13),
    ('Gamma^0_ab = K', 'd_transport.json', 'D2_Gamma0_ab_equals_K', '<', 1e-13),
    ('triad rotation +Omega', 'd_transport.json',
     'D2_triad_rotation_sign_scan.W = +1 * Omega', '<', 1e-7),
    ('triad rotation -Omega fails', 'd_transport.json',
     'D2_triad_rotation_sign_scan.W = -1 * Omega', '>', 1.0),
    ('photon dE/dt', 'd_transport.json', 'D13_photon_dE_dt', '<', 1e-12),
    ('photon dP/dt', 'd_transport.json', 'D13_photon_dP_dt', '<', 1e-12),
    ('massive dP/dt', 'd_transport.json', 'D9_massive_dP_dt', '<', 1e-12),
    ('|n| preserved', 'd_transport.json', 'D13_norm_preserved', '<', 1e-12),
    ('tidal trace = Ricci focusing', 'd_optical.json',
     'D16_trace_tidal_equals_Ricci_focusing', '<', 1e-12),
    ('EdS d_A', 'd_optical.json', 'D17_FLRW_EdS_dA_relerr', '<', 1e-10),
    ('FLRW redshift', 'd_optical.json', 'D14_FLRW_redshift_relerr', '<', 1e-11),
    ('reciprocity', 'd_optical.json', 'D17_reciprocity.relerr', '<', 1e-2),
    ('free-stream isotropic pi=0', 'd_kinetic.json', 'D12_isotropic_pi_is_zero', '<', 1e-11),
    ('free-stream EMT conservation', 'd_kinetic.json',
     'D12_energy_conservation_relresid_massless', '<', 1e-8),
    ('sudden response -8/15', 'd_kinetic.json',
     'D12_sudden_response_limit_vs_-8/15', '<', 5e-3),
    ('vorticity zero at v=0', 'd_matter.json', 'D22_vorticity_vanishes_for_v0', '<', 1e-12),
    # ---- v1.3 adversarial-audit gates -------------------------------------
    # (A-F2) coefficient gates: span-only maxres gates were blind to the physics
    ('G00 coeff H^2 = 3', 'fit_einstein.json', 'G00.coeffs.H^2', '=', 3.0),
    ('G00 coeff sigma^2 = -1', 'fit_einstein.json', 'G00.coeffs.sigma^2', '=', -1.0),
    ('G00 coeff 3R = 1/2', 'fit_einstein.json', 'G00.coeffs.^3R', '=', 0.5),
    ('G0i coeff sigma.a = -3', 'fit_einstein.json', 'G0i.coeffs.sigma.a', '=', -3.0),
    ('G0i coeff eps sigma n = 1', 'fit_einstein.json',
     'G0i.coeffs.eps_ibc sigma^b_d n^cd', '=', 1.0),
    ('trGij coeff Hdot = -6', 'fit_einstein.json', 'tr_Gij.coeffs.Hdot', '=', -6.0),
    ('trGij coeff H^2 = -9', 'fit_einstein.json', 'tr_Gij.coeffs.H^2', '=', -9.0),
    ('Gij coeff sigmadot = 1', 'fit_einstein.json',
     'Gij_tracefree.coeffs.sigmadot', '=', 1.0),
    ('Gij coeff H sigma = 3', 'fit_einstein.json',
     'Gij_tracefree.coeffs.H sigma', '=', 3.0),
    ('Gij coeff 3S = 1', 'fit_einstein.json', 'Gij_tracefree.coeffs.^3S', '=', 1.0),
    ('Gij coeff eps R sigma = 2', 'fit_einstein.json',
     'Gij_tracefree.coeffs.eps_{cd<a}R^c sigma_b>^d', '=', 2.0),
    # (A-F4) the engine's own self-check, previously shipped failing and ungated
    ('engine self-check G00', 'einstein_frame.json', 'G00', '<', 1e-12),
    ('engine self-check G0i', 'einstein_frame.json', 'G0i', '<', 1e-12),
    ('engine self-check trGij', 'einstein_frame.json', 'trGij', '<', 1e-12),
    ('engine self-check Gij_tf', 'einstein_frame.json', 'Gij_tf', '<', 1e-12),
    # (A-F1) reciprocity: was gated at 1e-2, masking a converged 1.5e-3 defect
    ('reciprocity (fixed screens)', 'd_optical.json', 'D17_reciprocity.relerr',
     '<', 1e-9),
    ('screen null-orthogonality', 'd_optical.json',
     'D15_screen_null_orthogonality_final', '<', 1e-9),
    # (A-F3/F8) previously failing-or-discriminating results left ungated
    ('D19 E=0 limit (R-converted)', 'd_matter.json',
     'D19_E0_limit_max_residual', '<', 0.5),
    ('Bianchi I covariant momentum', 'd_transport.json',
     'D10_bianchiI_covariant_momentum_const', '<', 1e-3),
    ('geodesic FLRW limit', 'd_transport.json', 'D13_FLRW_limit', '<', 1e-12),
    ('S^3 sphere anchor', 'r2_curvature.json', 'S3_anchor_Ric_err', '<', 1e-13),
    ('spatial block order pinned', 'd_transport.json',
     'D2_spatial_block_vs_core_order_acb', '<', 1e-13),
    # ---- v1.4 debts resolved -----------------------------------------------
    # debt A: vorticity vbardot-dependence is real off-shell; on-shell it is a
    #         clean EOS-independent observable (u-orthogonal, antisymmetric, ->0 at v=0)
    ('vorticity offshell dep is real', 'd_vorticity.json',
     'D22_offshell_vdot_dependence_is_real', '>', 1e-2),
    ('vorticity onshell accel || v', 'd_vorticity.json',
     'D22_onshell_accel_perp_to_v', '<', 1e-8),
    ('vorticity onshell _|_ u', 'd_vorticity.json',
     'D22_onshell_vorticity_orthogonal_to_u', '<', 1e-12),
    ('vorticity onshell EOS-independent', 'd_vorticity.json',
     'D22_onshell_spatial_vorticity_EOS_independent', '<', 1e-8),
    ('vorticity vanishes at v=0', 'd_vorticity.json',
     'D22_vorticity_vanishes_at_v0', '<', 1e-12),
    # debt B: CS(II) tilt reduction to {v2,v3} is complete
    ('CS(II) tilt eig matches analytic', 'd_tilted_II.json',
     'tilt_eigenvalues_match_analytic', '<', 1e-12),
    ('CS(II) type II geom momentum = 0', 'd_tilted_II.json',
     'type_II_geometric_momentum_at_CS.0', '<', 1e-12),
    ('CS(II) v1 forbidden by constraint', 'd_tilted_II.json',
     'v1_constraint_gradient', '>', 1e-2),
    ('CS(II) constrained crosses 10/7', 'd_tilted_II.json',
     'constrained_threshold_scan.g=1.4286', '<', 1e-8),
    # RF-02A: exact Jacobi-surface reduction, not the old raw component flag.
    ('Bianchi identity reduced', 'r4_bianchi_constraints.json',
     'bianchi_identity_reduced_vanishes', 'bool', True),
    ('Bianchi mutation witness', 'r4_bianchi_constraints.json',
     'mutation_witness.ndot_H_sign_flip.reduced_vanishes', 'bool', False),
]


def dig(d, path):
    """dotted-path lookup; greedy so keys that themselves contain '.' work
    (e.g. fit_einstein.json coeff key 'sigma.a')."""
    parts = path.split('.')
    i = 0
    while i < len(parts):
        for j in range(len(parts), i, -1):
            k = '.'.join(parts[i:j])
            if isinstance(d, dict) and k in d:
                d = d[k]; i = j; break
            if isinstance(d, list) and k.lstrip('-').isdigit():
                d = d[int(k)]; i = j; break
        else:
            raise KeyError(f'{path!r} at segment {parts[i]!r}')
    return d


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ran = {}
    for script, out in SCRIPTS:
        print(f'--- {script}', flush=True)
        r = subprocess.run([sys.executable, script], cwd=here,
                           capture_output=True, text=True)
        ran[script] = dict(returncode=r.returncode, stderr=r.stderr[-2000:])
        if r.returncode != 0:
            print(r.stderr[-2000:])

    rows, failed = [], 0
    for name, f, path, cmp_, bound in THRESHOLDS:
        try:
            val = float(dig(json.load(open(os.path.join(here, f))), path))
        except Exception as exc:                       # noqa: BLE001
            rows.append(dict(check=name, value=None, ok=False, error=str(exc)))
            failed += 1
            continue
        if cmp_ == '<':
            ok = val < bound
        elif cmp_ == '>':
            ok = val > bound
        elif cmp_ == 'bool':
            ok = bool(val) is bound
        else:                                   # '=' : coefficient gate
            ok = abs(val - bound) < 1e-9
        failed += (not ok)
        rows.append(dict(check=name, file=f, path=path, value=val,
                         requirement=f'{cmp_} {bound!s}', ok=bool(ok)))

    manifest = dict(
        version='1.5',
        generator=GENERATOR,
        python=sys.version.split()[0],
        scripts=ran,
        checks=rows,
        n_failed=failed,
        seeds=dict(r2_curvature=20260729, fit_einstein=31337, r1_jacobi_rotation=7,
                   r5c_tilt_fit=4242, r5d_tilt_closed=99, r5e_typeIX_D=20260729,
                   einstein_frame=20260729, d_transport=20260729,
                   d_kinetic=20260729, d_matter=20260729, d_optical=20260729,
                   adjudicate_d19=7),
    )
    json.dump(manifest, open(os.path.join(here, 'manifest.json'), 'w'), indent=2)
    for r in rows:
        flag = 'PASS' if r['ok'] else 'FAIL'
        print(f"  [{flag}] {r['check']:28s} {r.get('value')!r}")
    print(f"\n{len(rows) - failed}/{len(rows)} checks passed")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
