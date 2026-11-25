//! Native live REI source/chemistry on accepted BASS geometry. Restore
//! F08 characteristic-born packets without the historical hot-FT03 domain
//! restriction. Actual chemistry uses the shared REI AXBI stage, not xe table.
//! Geometry is frozen to the accepted BASS trajectory; CMB Thomson is a
//! tracer driven by live charge, with isotropic CMB thermal bath retained.
use super::replay::StepRecord;
use super::{
    birth_packets::{sum, BirthPackets, TransportLedger},
    geometric_one, initial_sky, scatter_with, CollisionScheme, Photon,
};
use crate::kinetic::lie_history::RayNode;
use rec_microphysics::thomson_history::C_SIGMA_T_M3_S;
use rei_microphysics::{
    axbi_driver::{packet_chemistry_stage, PacketStageInput},
    axbi_sources::AxbiSource,
    coupled_primary::PrimaryPacket,
    igm_state::{w_erg_per_h_to_ev, IgmGasState},
    HHeModel,
};

#[derive(Clone, Copy, Debug)]
pub struct LiveInput {
    pub a0: f64,
    pub h0_s: f64,
    pub nh0_m3: f64,
    pub f_he: f64,
    pub tcmb0_k: f64,
    pub initial_gas: IgmGasState,
    pub escape_fraction: f64,
    pub energy_subdivisions: usize,
    pub n_mu: usize,
}
#[derive(Clone, Debug, Default)]
pub struct LiveLedger {
    pub emitted_n: f64,
    pub emitted_u: f64,
    pub absorbed_n: f64,
    pub escaped_u: f64,
    pub boundary_n: f64,
    pub boundary_u: f64,
    pub thermal_work: f64,
    pub redshift_work: f64,
    pub cmb_input: f64,
    pub photo_events: [f64; 3],
}
#[derive(Clone, Debug)]
pub struct LiveRow {
    pub eta: f64,
    pub time_s: f64,
    pub h_s: f64,
    pub nh_m3: f64,
    pub gas: IgmGasState,
    pub tm_k: f64,
    pub xe: f64,
    pub photons_n: f64,
    pub photons_u: f64,
    pub packets: usize,
    pub opacity: f64,
    pub tau: f64,
    pub number_defect: f64,
    pub energy_defect: f64,
    pub root_residual: f64,
    pub max_support_error: f64,
    pub ledger: LiveLedger,
}
pub struct LiveResult {
    pub history: Vec<LiveRow>,
    pub photons: BirthPackets,
    pub cmb: Vec<Photon>,
    pub rhs: usize,
}
fn midpoint(a: &RayNode, b: &RayNode) -> RayNode {
    RayNode {
        eta: (a.eta + b.eta) * 0.5,
        shear: std::array::from_fn(|i| {
            std::array::from_fn(|j| (a.shear[i][j] + b.shear[i][j]) * 0.5)
        }),
        n: a.n,
        a: a.a,
        rotation: a.rotation,
        hubble_ratio: (a.hubble_ratio * b.hubble_ratio).sqrt(),
        ..a.clone()
    }
}
fn thermal(g: IgmGasState) -> Result<f64, String> {
    w_erg_per_h_to_ev(g.w_erg_per_h).map_err(|e| e.to_string())
}
fn binding(y: IgmGasState, fhe: f64) -> f64 {
    let c = HHeModel::controlled_fixture().threshold_ev;
    c[0] * y.fractions[0] + fhe * (c[1] * y.fractions[1] + (c[1] + c[2]) * y.fractions[2])
}
fn apply_transport(l: &mut LiveLedger, m: TransportLedger) {
    l.boundary_n += m.boundary_n;
    l.boundary_u += m.boundary_u;
    l.redshift_work += m.redshift_work;
}
fn coordinates(n: &RayNode, input: &LiveInput) -> (f64, f64, f64) {
    (
        input.a0 * n.eta.exp(),
        input.h0_s * n.hubble_ratio,
        input.nh0_m3 * (-3. * n.eta).exp(),
    )
}
fn snapshot(
    n: &RayNode,
    input: &LiveInput,
    gas: IgmGasState,
    p: &BirthPackets,
    ledger: &LiveLedger,
    t: f64,
    tau: f64,
    initial_e: f64,
    res: f64,
    support: f64,
) -> Result<LiveRow, String> {
    let (_, h, nh) = coordinates(n, input);
    let eos = gas
        .eos(nh * 1e-6, nh * 1e-6 * input.f_he)
        .map_err(|e| e.to_string())?;
    let xe = eos.electron_density_cm3 / (nh * 1e-6);
    let opacity = C_SIGMA_T_M3_S * nh * xe / h;
    let (count, energy) = p.inventory();
    let nd = count + ledger.absorbed_n + ledger.boundary_n - ledger.emitted_n;
    let ed = thermal(gas)?
        + binding(gas, input.f_he)
        + energy
        + ledger.escaped_u
        + ledger.boundary_u
        + ledger.thermal_work
        + ledger.redshift_work
        - ledger.emitted_u
        - ledger.cmb_input
        - initial_e;
    if !opacity.is_finite()
        || opacity < 0.
        || !ed.is_finite()
        || !nd.is_finite()
        || nd.abs() > 1e-8 * ledger.emitted_n.max(1.)
        || ed.abs() > 1e-8 * ledger.emitted_u.max(1.)
    {
        return Err(format!(
            "live REI ledger residual number={nd:e} energy={ed:e}"
        ));
    }
    Ok(LiveRow {
        eta: n.eta,
        time_s: t,
        h_s: h,
        nh_m3: nh,
        gas,
        tm_k: eos.temperature_k,
        xe,
        photons_n: count,
        photons_u: energy,
        packets: p.packets.len(),
        opacity,
        tau,
        number_defect: nd,
        energy_defect: ed,
        root_residual: res,
        max_support_error: support,
        ledger: ledger.clone(),
    })
}
pub fn evolve(records: &[StepRecord], input: LiveInput) -> Result<LiveResult, String> {
    if records.is_empty()
        || records[0].left.eta != 0.
        || input.a0 != 1. / 21.
        || ![input.h0_s, input.nh0_m3, input.f_he, input.tcmb0_k]
            .iter()
            .all(|v| v.is_finite() && *v > 0.)
        || records.windows(2).any(|p| p[0].right.eta != p[1].left.eta)
        || records.iter().any(|r| {
            !r.first.is_empty()
                || !r.second.is_empty()
                || r.left.hubble_ratio <= 0.
                || r.right.hubble_ratio <= 0.
        })
    {
        return Err("expected continuous collision-free BASS geometry from zbar20".into());
    }
    let src = AxbiSource::new(
        input.nh0_m3 * 1e-6 * input.a0.powi(3),
        input.escape_fraction,
        input.energy_subdivisions,
        input.n_mu,
    )
    .map_err(|e| e.to_string())?;
    let dirs = src
        .angular_cells
        .iter()
        .map(|a| [(1. - a.mu * a.mu).sqrt(), 0., a.mu])
        .collect();
    let weights = src.angular_cells.iter().map(|a| a.count_fraction).collect();
    let cells: Vec<_> = src
        .spectral_cells
        .iter()
        .map(|c| (c.energy_ev, c.photon_fraction))
        .collect();
    let mut p = BirthPackets::new(dirs, weights)?;
    let mut gas = input.initial_gas;
    let mut ledger = LiveLedger::default();
    let initial_e = thermal(gas)? + binding(gas, input.f_he);
    let (mut t, mut tau, mut support) = (0_f64, 0_f64, 0_f64);
    let mut counter = 0;
    let mut cmb = initial_sky(input.n_mu, 8)?;
    let mut history = vec![snapshot(
        &records[0].left,
        &input,
        gas,
        &p,
        &ledger,
        t,
        tau,
        initial_e,
        0.,
        support,
    )?];
    for record in records {
        let l = &record.left;
        let r = &record.right;
        let m = midpoint(l, r);
        let h = r.eta - l.eta;
        let (a0, h0, _) = coordinates(l, &input);
        let (am, hm, nh) = coordinates(&m, &input);
        let (a1, h1, _) = coordinates(r, &input);
        if !(h > 0. && h0 > 0. && h1 > 0. && am.is_finite() && a1 <= 0.2 + 1e-15) {
            return Err("live REI clock outside AXBI domain".into());
        }
        let dt = h * (1. / h0 + 4. / hm + 1. / h1) / 6.;
        // Geometry and adiabatic work half map.
        let q = p.transport(l, &m)?;
        support = support.max(q.max_support_error);
        apply_transport(&mut ledger, q);
        let old = thermal(gas)?;
        gas = gas.adiabatic_to(a0, am).map_err(|e| e.to_string())?;
        ledger.thermal_work += old - thermal(gas)?;
        let source = src.at_redshift(1. / am - 1.).map_err(|e| e.to_string())?;
        let (sn, su) = p.inject(m.eta, source.per_h_s, dt, &cells)?;
        ledger.emitted_n += sn;
        ledger.emitted_u += su;
        let inputs: Vec<_> = p
            .packets
            .iter()
            .map(|p| PrimaryPacket {
                energy_ev: p.energy_ev,
                per_h: p.per_h,
            })
            .collect();
        let q = packet_chemistry_stage(
            PacketStageInput {
                n_h_cm3: nh * 1e-6,
                n_he_cm3: nh * 1e-6 * input.f_he,
                tcmb_k: input.tcmb0_k / am,
            },
            gas,
            &inputs,
            dt,
            &mut counter,
            20_000_000,
        )
        .map_err(|e| format!("REI packet stage eta={:e}: {e}", m.eta))?;
        let direct_loss = sum(inputs.iter().zip(&q.stocks).map(|(a, b)| a.per_h - b));
        if (direct_loss - q.ledgers.absorbed_n).abs() > 1e-10 * ledger.emitted_n.max(1.) {
            return Err("live REI event count mismatch".into());
        }
        gas = q.gas;
        for (p, n) in p.packets.iter_mut().zip(q.stocks) {
            p.per_h = n;
        }
        ledger.absorbed_n += q.ledgers.absorbed_n;
        ledger.escaped_u += q.ledgers.escaped_u;
        ledger.cmb_input += q.ledgers.cmb_input;
        for i in 0..3 {
            ledger.photo_events[i] += q.ledgers.photo_events[i]
        }
        let root = q.max_residual;
        let q = p.transport(&m, r)?;
        support = support.max(q.max_support_error);
        apply_transport(&mut ledger, q);
        let old = thermal(gas)?;
        gas = gas.adiabatic_to(am, a1).map_err(|e| e.to_string())?;
        ledger.thermal_work += old - thermal(gas)?;
        // Actual newly evolved endpoint charge, not tabulated xe.
        let last = history.last().unwrap();
        let n = snapshot(
            r,
            &input,
            gas,
            &p,
            &ledger,
            t + dt,
            tau,
            initial_e,
            root,
            support,
        )?;
        let k0 = last.opacity;
        let k1 = n.opacity;
        let d0 = h * (3. * k0 + k1) / 8.;
        let d1 = h * (k0 + 3. * k1) / 8.;
        if d0 > 0. {
            scatter_with(&mut cmb, d0, [0.; 3], CollisionScheme::Sdirk2)?;
        }
        for c in &mut cmb {
            geometric_one(c, l, r)?;
        }
        if d1 > 0. {
            scatter_with(&mut cmb, d1, [0.; 3], CollisionScheme::Sdirk2)?;
        }
        tau += d0 + d1;
        t += dt;
        history.push(LiveRow { tau, ..n });
    }
    Ok(LiveResult {
        history,
        photons: p,
        cmb,
        rhs: counter,
    })
}
