use bianchi_rustcore::{
    homogeneous_sky::{
        material::Material,
        rei_live::{evolve_with_compression, LiveInput},
        replay::StepRecord,
        solve::{solve_general, Settings, SolveOptions},
        CollisionScheme,
    },
    kinetic::{
        lie_history::{LieInitial, RayNode},
        radiation_feedback::{ExpansionEquation, LieUpdate},
    },
};
use rei_microphysics::igm_state::{w_erg_per_h_to_ev, IgmGasState};
use std::{
    fs,
    io::{BufWriter, Write},
    path::Path,
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let a = std::env::args().skip(1).collect::<Vec<_>>();
    if a.len() != 8 && a.len() != 9 {
        return Err(
            "usage OUT END_Z STEPS Q_REF ENERGY_SUBDIV N_MU XP TM_K [LOG_COMPRESSION_WIDTH]".into(),
        );
    }
    let out = Path::new(&a[0]);
    let z: f64 = a[1].parse()?;
    let steps: usize = a[2].parse()?;
    let q: f64 = a[3].parse()?;
    let sub: usize = a[4].parse()?;
    let nmu: usize = a[5].parse()?;
    let xp: f64 = a[6].parse()?;
    let tm: f64 = a[7].parse()?;
    let width: Option<f64> = a.get(8).map(|v| v.parse()).transpose()?;
    let short = (19.8..20.).contains(&z) && steps <= 4096;
    let long = width.is_some() && q == 0. && (4.0..19.8).contains(&z) && steps <= 65536;
    if !(short || long) || steps == 0 || !q.is_finite() || q.abs() > 0.02 {
        return Err("bounded short LRS I or compressed analytic FLRW z20 to z>=4".into());
    }
    let a0 = 1. / 21.;
    let om = 0.315 * 21f64.powi(3);
    let or = 9.2e-5 * 21f64.powi(4);
    let ol = 1. - 0.315 - 9.2e-5;
    let h0 = 67.4 * 1e5 / 3.0856775814913673e24;
    let h = h0 * (om + or + ol).sqrt() * 1f64.hypot(q);
    let sig = q / 1f64.hypot(q);
    let lie = LieInitial {
        shear: [[-sig, 0., 0.], [0., -sig, 0.], [0., 0., 2. * sig]],
        ..Default::default()
    };
    let duration = (21. / (1. + z)).ln();
    let cfg = Settings {
        family: "I",
        shear: 0.,
        duration,
        steps,
        nmu: 6,
        nphi: 12,
        active: true,
        recoil: false,
        dust_fraction: om / (om + or),
        dust_beta: [0.; 3],
        collision: CollisionScheme::Sdirk2,
        omega_lambda: ol / ((om + or + ol) * (1. + q * q)),
        lie_update: LieUpdate::Congruence,
    };
    // For the long FLRW control, exact H(a) avoids integrating a redundant
    // geometry solve. The existing short route still uses BASS accepted records.
    let (records, nodes) = if long {
        let nodes = (0..=steps)
            .map(|i| {
                let eta = duration * i as f64 / steps as f64;
                let e = (om * (-3. * eta).exp() + or * (-4. * eta).exp() + ol).sqrt();
                RayNode {
                    eta,
                    hubble_ratio: e / (om + or + ol).sqrt(),
                    omega_radiation: or * (-4. * eta).exp() / e.powi(2),
                    omega_lambda: ol / e.powi(2),
                    ..Default::default()
                }
            })
            .collect::<Vec<_>>();
        let records = nodes
            .windows(2)
            .map(|p| StepRecord {
                left: p[0].clone(),
                right: p[1].clone(),
                first: vec![],
                second: vec![],
            })
            .collect::<Vec<_>>();
        (records, nodes)
    } else {
        let geom = solve_general(
            &cfg,
            &Material::constant(duration, 0., [0.; 3])?,
            Some(&lie),
            None,
            ExpansionEquation::GaussReduced,
            0.0224 / 0.674f64.powi(2) / 0.315,
            &SolveOptions::default(),
        )?;
        let nodes = geom
            .history
            .iter()
            .map(|s| s.node.clone())
            .collect::<Vec<_>>();
        (geom.records, nodes)
    };
    let nh = 0.18981984507140268 * 21f64.powi(3);
    let fhe = 0.2454 / (4. * (1. - 0.2454));
    let init = IgmGasState::from_temperature([xp, 0., 0.], nh * 1e-6, nh * 1e-6 * fhe, tm)?;
    let start = std::time::Instant::now();
    let s = evolve_with_compression(
        &records,
        LiveInput {
            a0,
            h0_s: h,
            nh0_m3: nh,
            f_he: fhe,
            tcmb0_k: 2.7255,
            initial_gas: init,
            escape_fraction: 0.2,
            energy_subdivisions: sub,
            n_mu: nmu,
        },
        width,
    )?;
    fs::create_dir(out)?;
    let mut f = BufWriter::new(fs::File::create(out.join("history.tsv"))?);
    writeln!(f,"eta\ttime_s\tH_s\tnH_m3\tx_HII\tx_HeII\tx_HeIII\txe\tTm_K\tw_eV_per_H\tN\tU_eV\tpackets\topacity\ttau\tnumber_defect\tenergy_defect\troot_residual\tsupport_error\temitted_N\temitted_U\tabsorbed_N\tescaped_U\tboundary_N\tboundary_U\tthermal_work\tredshift_work\tcmb_input\tphoto_HI\tphoto_HeI\tphoto_HeII")?;
    for r in &s.history {
        let [x, y, z] = r.gas.fractions;
        let l = &r.ledger;
        let vals = [
            r.eta,
            r.time_s,
            r.h_s,
            r.nh_m3,
            x,
            y,
            z,
            r.xe,
            r.tm_k,
            w_erg_per_h_to_ev(r.gas.w_erg_per_h)?,
            r.photons_n,
            r.photons_u,
            r.packets as f64,
            r.opacity,
            r.tau,
            r.number_defect,
            r.energy_defect,
            r.root_residual,
            r.max_support_error,
            l.emitted_n,
            l.emitted_u,
            l.absorbed_n,
            l.escaped_u,
            l.boundary_n,
            l.boundary_u,
            l.thermal_work,
            l.redshift_work,
            l.cmb_input,
            l.photo_events[0],
            l.photo_events[1],
            l.photo_events[2],
        ];
        writeln!(
            f,
            "{}",
            vals.iter()
                .map(|v| format!("{v:.17e}"))
                .collect::<Vec<_>>()
                .join("\t")
        )?;
    }
    f.flush()?;
    let mut f = BufWriter::new(fs::File::create(out.join("packets.tsv"))?);
    writeln!(
        f,
        "ray\tenergy_eV\tN_per_H\tbirth_eta\tbirth_energy_eV\tmu_final"
    )?;
    for p in &s.photons.packets {
        writeln!(
            f,
            "{}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            p.ray,
            p.energy_ev,
            p.per_h,
            p.birth_eta,
            p.birth_energy_ev,
            s.photons.directions[p.ray][2]
        )?;
    }
    f.flush()?;
    let mut f = BufWriter::new(fs::File::create(out.join("geometry.tsv"))?);
    writeln!(
        f,
        "eta\tH_ratio\tSigma_xx\tSigma_yy\tSigma_zz\tGauss\tCodazzi_max"
    )?;
    for n in &nodes {
        writeln!(
            f,
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            n.eta,
            n.hubble_ratio,
            n.shear[0][0],
            n.shear[1][1],
            n.shear[2][2],
            n.gauss_residual,
            n.codazzi_residual
                .iter()
                .map(|x| x.abs())
                .fold(0., f64::max)
        )?;
    }
    f.flush()?;
    let mut f = BufWriter::new(fs::File::create(out.join("cmb.tsv"))?);
    writeln!(f, "ex\tey\tez\tweight_sr\tI\tQxx\tQyy\tQzz")?;
    for p in &s.cmb {
        let [x, y, z] = p.direction();
        let m = p.screen();
        writeln!(
            f,
            "{x:.17e}\t{y:.17e}\t{z:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            p.weight(),
            m[0][0] + m[1][1] + m[2][2],
            m[0][0],
            m[1][1],
            m[2][2]
        )?;
    }
    f.flush()?;
    let stress = s.photons.lrs_stress(s.history.last().unwrap().nh_m3)?;
    fs::write(out.join("uv_stress.txt"),format!("rho_J_m3={:.17e}\nflux_z_J_m3={:.17e}\nP_parallel_J_m3={:.17e}\nP_perp_J_m3={:.17e}\nDelta_J_m3={:.17e}\n",stress.rho_j_m3,stress.flux_z_j_m3,stress.p_parallel_j_m3,stress.p_perp_j_m3,stress.delta_j_m3))?;
    let ledger = &s.history.last().unwrap().ledger;
    fs::write(out.join("compression.txt"),format!("width={width:?}\nanalytic_flrw={long}\nisotropic_uv_reduced={}\nremoved={}\npeak_before={}\npeak_after={}\nmax_N_relative={:.17e}\nmax_U_relative={:.17e}\nmax_log_span={:.17e}\n",s.isotropic_uv_reduced,ledger.compression_removed,ledger.compression.before,ledger.compression.after,ledger.compression.max_number_relative,ledger.compression.max_energy_relative,ledger.compression.max_log_span))?;
    fs::write(out.join("run.txt"),format!("scope=live_REI_on_accepted_BASS_LRS_I_geometry\ngeometry_feedback_from_REI=false\nthermal_CMB=isotropic\nsteps={}\nrhs={}\nwall_s={:.17e}\n",s.history.len()-1,s.rhs,start.elapsed().as_secs_f64()))?;
    Ok(())
}
