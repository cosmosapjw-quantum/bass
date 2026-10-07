use rei_microphysics::{
    homogeneous_opacity, homogeneous_photo_rates, Absorber, AtomicProvider, PhotonNode, C_LIGHT,
    MPC_CM,
};
fn near(a: f64, b: f64) {
    assert!((a - b).abs() <= 5e-14 * b.abs() + 1e-300, "{a:e} != {b:e}");
}
#[test]
fn species_and_energy_owners() {
    let p = AtomicProvider::reference();
    let n = [1e-4, 1e-5, 2e-5];
    let e = 70.;
    let o = homogeneous_opacity(&p, n, e).unwrap();
    let sigma =
        [Absorber::HI, Absorber::HeI, Absorber::HeII].map(|s| p.cross_section(s, e).unwrap());
    let k = (0..3).map(|s| n[s] * sigma[s]).sum::<f64>();
    near(o.kappa_per_cm, k);
    near(o.fractions.iter().sum(), 1.);
    let a = 0.5_f64;
    let density = 2e-6;
    let nc = density * (a * MPC_CM).powi(3);
    let q = homogeneous_photo_rates(
        &p,
        n,
        a,
        &[PhotonNode {
            energy_ev: e,
            n_comoving_per_cmpc3: nc,
        }],
    )
    .unwrap();
    let chi = [13.598434599702, 24.587389011, 54.41776];
    let ev = 1.602176634e-12;
    for s in 0..3 {
        near(o.fractions[s], n[s] * sigma[s] / k);
        near(q.gamma_per_s[s], C_LIGHT * density * sigma[s]);
        near(q.events_proper_per_cm3_s[s], n[s] * q.gamma_per_s[s]);
        near(
            q.heat_erg_per_cm3_s[s],
            q.events_proper_per_cm3_s[s] * (e - chi[s]) * ev,
        );
        near(
            q.binding_erg_per_cm3_s[s],
            q.events_proper_per_cm3_s[s] * chi[s] * ev,
        );
    }
    near(q.photon_loss_comoving_per_cmpc3_s, C_LIGHT * k * nc);
    near(
        q.absorbed_erg_per_cm3_s,
        q.events_proper_per_cm3_s.iter().sum::<f64>() * e * ev,
    );
    near(
        q.absorbed_erg_per_cm3_s,
        q.heat_erg_per_cm3_s.iter().sum::<f64>() + q.binding_erg_per_cm3_s.iter().sum::<f64>(),
    );
}
#[test]
fn zero_opacity_and_quadrature_linearity() {
    let p = AtomicProvider::reference();
    let n = [1e-4, 1e-5, 2e-5];
    let o = homogeneous_opacity(&p, [0.; 3], 70.).unwrap();
    assert_eq!(o.kappa_per_cm, 0.);
    assert_eq!(o.fractions, [0.; 3]);
    let node = PhotonNode {
        energy_ev: 70.,
        n_comoving_per_cmpc3: 1e60,
    };
    let q = homogeneous_photo_rates(&p, [0.; 3], 1., &[node]).unwrap();
    assert_eq!(q.events_proper_per_cm3_s, [0.; 3]);
    assert_eq!(q.photon_loss_comoving_per_cmpc3_s, 0.);
    assert_eq!(q.heat_erg_per_cm3_s, [0.; 3]);
    let sub = homogeneous_photo_rates(
        &p,
        n,
        1.,
        &[PhotonNode {
            energy_ev: 10.,
            n_comoving_per_cmpc3: 1e60,
        }],
    )
    .unwrap();
    assert_eq!(sub.gamma_per_s, [0.; 3]);
    let whole = homogeneous_photo_rates(&p, n, 1., &[node]).unwrap();
    let split = homogeneous_photo_rates(
        &p,
        n,
        1.,
        &[
            PhotonNode {
                energy_ev: 70.,
                n_comoving_per_cmpc3: 4e59,
            },
            PhotonNode {
                energy_ev: 70.,
                n_comoving_per_cmpc3: 6e59,
            },
        ],
    )
    .unwrap();
    for s in 0..3 {
        near(whole.gamma_per_s[s], split.gamma_per_s[s]);
        near(whole.heat_erg_per_cm3_s[s], split.heat_erg_per_cm3_s[s]);
    }
    let early = homogeneous_photo_rates(&p, n, 0.5, &[node]).unwrap();
    for s in 0..3 {
        near(early.gamma_per_s[s], 8. * whole.gamma_per_s[s]);
    }
    near(
        early.photon_loss_comoving_per_cmpc3_s,
        whole.photon_loss_comoving_per_cmpc3_s,
    );
}
#[test]
fn invalid_and_overflow() {
    let p = AtomicProvider::reference();
    for n in [[-1., 0., 0.], [f64::NAN, 0., 0.], [f64::INFINITY, 0., 0.]] {
        assert!(homogeneous_opacity(&p, n, 70.).is_err());
    }
    for a in [0., -1., f64::NAN, f64::INFINITY, 1e-300] {
        assert!(homogeneous_photo_rates(&p, [1e-4; 3], a, &[]).is_err());
    }
    for v in [-1., f64::NAN, f64::INFINITY] {
        assert!(homogeneous_photo_rates(
            &p,
            [1e-4; 3],
            1.,
            &[PhotonNode {
                energy_ev: 70.,
                n_comoving_per_cmpc3: v
            }]
        )
        .is_err());
    }
    assert!(homogeneous_photo_rates(
        &p,
        [1e300; 3],
        1.,
        &[PhotonNode {
            energy_ev: 70.,
            n_comoving_per_cmpc3: 1e300
        }]
    )
    .is_err());
    assert!(homogeneous_photo_rates(
        &p,
        [0.; 3],
        1.,
        &[PhotonNode {
            energy_ev: 50001.,
            n_comoving_per_cmpc3: 0.
        }]
    )
    .is_err());
}
