//! Source-conditioned scalar REC native bridge. Input arrays exported
//! losslessly from the pinned owner NPZ; physical units preserved.
//! No full BASS trajectory remapping/atomic feedback in this example.
use bianchi_rustcore::homogeneous_sky::rec_angular::{
    frame_map, Bridge, Direction, Grid, Network, Packet, Scope, Side, State,
};
use bianchi_rustcore::kinetic::lie_history::RayNode;
use nalgebra::DMatrix;
use std::{
    env, fs,
    io::{BufWriter, Write},
    path::Path,
};
struct Tokens<'a> {
    s: std::str::SplitWhitespace<'a>,
}
impl<'a> Tokens<'a> {
    fn new(s: &'a str) -> Self {
        Self {
            s: s.split_whitespace(),
        }
    }
    fn word(&mut self) -> Result<&'a str, String> {
        self.s.next().ok_or("missing token".into())
    }
    fn num<T: std::str::FromStr>(&mut self) -> Result<T, String> {
        self.word()?
            .parse()
            .map_err(|_| "invalid numeric token".into())
    }
    fn vec(&mut self, n: usize) -> Result<Vec<f64>, String> {
        (0..n).map(|_| self.num()).collect()
    }
    fn triple(&mut self) -> Result<[f64; 3], String> {
        Ok([self.num()?, self.num()?, self.num()?])
    }
    fn matrix(&mut self) -> Result<[[f64; 3]; 3], String> {
        Ok([self.triple()?, self.triple()?, self.triple()?])
    }
    fn end(&mut self) -> Result<(), String> {
        if self.s.next().is_some() {
            Err("unexpected trailing input".into())
        } else {
            Ok(())
        }
    }
}
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<_> = env::args().skip(1).collect();
    if args.len() != 3 && args.len() != 10 {
        return Err("usage rec_angular_bridge NETWORK CASE OUT".into());
    }
    let network = fs::read_to_string(&args[0])?;
    let mut t = Tokens::new(&network);
    if t.word()? != "rec_angular_network_v1" {
        return Err("invalid network schema".into());
    }
    let n: usize = t.num()?;
    let l: usize = t.num()?;
    if n != 35 || l != 24 {
        return Err("source requires released 35-state, L24 tensor".into());
    }
    let mut states = vec![];
    for _ in 0..n {
        states.push(State {
            label: t.word()?.into(),
            lo: t.num()?,
            hi: t.num()?,
            g: t.num()?,
            pi: t.num()?,
            p: t.num()?,
        });
    }
    let labels: Vec<_> = (0..17)
        .map(|i| format!("I{i:02}"))
        .chain((0..6).map(|i| format!("NR{i:02}")))
        .chain((0..6).map(|i| format!("NB{i:02}")))
        .chain((0..3).map(|i| format!("FR{i:02}")))
        .chain((0..3).map(|i| format!("FB{i:02}")))
        .collect();
    if states.iter().map(|s| &s.label).ne(labels.iter()) {
        return Err("source label identity mismatch".into());
    }
    let pair = t.vec((l + 1) * n * n)?;
    let same = t.vec((l + 1) * n)?;
    t.end()?;
    let network = Network::new(states, l, pair, same)?;
    let case = fs::read_to_string(&args[1])?;
    let mut t = Tokens::new(&case);
    if t.word()? != "rec_angular_case_v1" {
        return Err("invalid case schema".into());
    }
    let na: usize = t.num()?;
    let ell: usize = t.num()?;
    let mut h: f64 = t.num()?;
    let beta = t.triple()?;
    let bp = t.triple()?;
    let mut node = RayNode {
        shear: t.matrix()?,
        n: t.matrix()?,
        a: t.triple()?,
        rotation: t.triple()?,
        ..Default::default()
    };
    let dt: f64 = t.num()?;
    let clock_name = t.word()?;
    let mut dir = vec![];
    let mut weight = vec![];
    for _ in 0..na {
        dir.push(t.triple()?);
        weight.push(t.num()?);
    }
    let grid = Grid::new(dir, weight, ell)?;
    let b = Bridge::new(network, grid)?;
    let mut f = DMatrix::from_column_slice(na, n, &t.vec(na * n)?);
    let mut v = DMatrix::from_column_slice(na, n, &t.vec(na * n)?);
    let count: usize = t.num()?;
    let nh: f64 = t.num()?;
    if count > 2 {
        return Err("at most two source packets".into());
    }
    let mut packets = vec![];
    for _ in 0..count {
        let side = match t.word()? {
            "red" => Side::Red,
            "blue" => Side::Blue,
            _ => return Err("invalid side".into()),
        };
        let direction = match t.word()? {
            "into" => Direction::IntoCom,
            "out" => Direction::OutOfCom,
            _ => return Err("invalid direction".into()),
        };
        let p = Packet {
            side,
            direction,
            frequency_hz: t.num()?,
            number_per_h: t.num()?,
            energy_j_per_h: t.num()?,
        };
        packets.push(p);
    }
    t.end()?;
    let mut sampled = None;
    let mut landing_error = 0.;
    let mut temp_gap: f64 = 0.;
    let mut bass_steps = 0;
    if args.len() == 10 {
        if !packets.is_empty() {
            return Err("BASS characteristic sample cannot use frozen source packet".into());
        }
        use bianchi_rustcore::homogeneous_sky::{
            material::Material,
            rec_angular::sample_collisionless_planck,
            replay::arrival,
            solve::{solve_general, Settings, SolveOptions},
            CollisionScheme,
        };
        use bianchi_rustcore::kinetic::radiation_feedback::{ExpansionEquation, LieUpdate};
        let duration: f64 = args[5].parse()?;
        let steps: usize = args[6].parse()?;
        let temp: f64 = args[7].parse()?;
        let nu: f64 = args[8].parse()?;
        let width: f64 = args[9].parse()?;
        let cfg = Settings {
            family: &args[3],
            shear: args[4].parse()?,
            duration,
            steps,
            nmu: 8,
            nphi: 16,
            active: true,
            recoil: false,
            dust_fraction: 0.,
            dust_beta: [0.; 3],
            collision: CollisionScheme::Sdirk2,
            omega_lambda: 0.,
            lie_update: LieUpdate::Congruence,
        };
        let sol = solve_general(
            &cfg,
            &Material::constant(duration, 0., [0.; 3])?,
            None,
            None,
            ExpansionEquation::Raychaudhuri,
            0.5,
            &SolveOptions::default(),
        )?;
        node = sol.history.last().ok_or("empty BASS history")?.node.clone();
        h *= node.hubble_ratio;
        let fm = frame_map(&b.grid, &node, beta, bp, h)?;
        let q = sample_collisionless_planck(&b.network, &fm, &sol.records, temp, nu, width)?;
        if q.source_measure_defect > 1e-10 || q.source_momentum_defect > 1e-10 {
            return Err("REC source measure mismatch".into());
        }
        for (i, e) in b.grid.directions.iter().enumerate() {
            let a = arrival(&sol.records, beta, e.map(|v| -v))?;
            landing_error = f64::max(landing_error, a.landing_error);
            let tr = a.screen[0][0] + a.screen[1][1] + a.screen[2][2];
            temp_gap = temp_gap.max((temp * tr.powf(0.25) / q.temperature_h[i] - 1.).abs());
        }
        f = q.occupation.clone();
        v = DMatrix::from_fn(f.nrows(), f.ncols(), |a, i| {
            f[(a, i)]
                * 0.03
                * ((b.network.states[i].lo + b.network.states[i].hi) / 6.2 + 0.017 * a as f64).sin()
        });
        bass_steps = sol.records.len();
        sampled = Some(q);
    }
    let frame = frame_map(&b.grid, &node, beta, bp, h)?;
    let clock = match clock_name {
        "material" => vec![1.; na],
        "normal" => frame.doppler.clone(),
        _ => return Err("invalid clock".into()),
    };
    let a = b.action(&f, Scope::Full)?;
    let boundary = b.action(&f, Scope::CoreExterior)?;
    let jvp = b.jvp(&f, &v, Scope::Full)?;
    let bjvp = b.jvp(&f, &v, Scope::CoreExterior)?;
    let normal = b.normal_ledger(&a, &frame)?;
    let eq = b.equilibrium(
        0.5 / b
            .network
            .states
            .iter()
            .map(|s| s.pi / s.g)
            .fold(0., f64::max),
    )?;
    let null = b.action(&eq, Scope::Full)?;
    let mut inc = DMatrix::zeros(na, n);
    let mut ledger = vec![];
    for p in &packets {
        let (df, q) = b.packet(p, nh)?;
        inc += df;
        ledger.push(q);
    }
    let started = std::time::Instant::now();
    let solve = b.implicit(&f, dt, &clock, &inc);
    let elapsed = started.elapsed().as_secs_f64();
    let (updated, step_err) = match &solve {
        Ok(q) => (q.occupation.clone(), None),
        Err(e) => (f.clone(), Some(e)),
    };
    let out = Path::new(&args[2]);
    if out.exists() {
        return Err("output exists".into());
    }
    fs::create_dir_all(out)?;
    let mut file = BufWriter::new(fs::File::create(out.join("action.tsv"))?);
    writeln!(file,"state\tangle\toccupation\tfull_action\tboundary_action\tjvp\tboundary_jvp\tnormal_eta_action\tupdated\tincrement")?;
    for i in 0..n {
        for k in 0..na {
            writeln!(
                file,
                "{i}\t{k}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
                f[(k, i)],
                a.occupation[(k, i)],
                boundary.occupation[(k, i)],
                jvp[(k, i)],
                bjvp[(k, i)],
                normal.occupation_per_eta[(k, i)],
                updated[(k, i)],
                inc[(k, i)]
            )?;
        }
    }
    file.flush()?;
    let mut file = BufWriter::new(fs::File::create(out.join("frame.tsv"))?);
    writeln!(file, "angle\tnx\tny\tnz\tD\tweight_normal\tdlognu_deta")?;
    for k in 0..na {
        let e = frame.directions_normal[k];
        writeln!(
            file,
            "{k}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            e[0],
            e[1],
            e[2],
            frame.doppler[k],
            frame.weights_normal[k],
            frame.log_frequency_drift[k]
        )?;
    }
    file.flush()?;
    let mut file = BufWriter::new(fs::File::create(out.join("packets.tsv"))?);
    writeln!(file,"index\tnative_number_per_h\tcom_number_per_h\tnative_energy_j_per_h\tcom_energy_j_per_h\tcentroid_proxy_j_per_h\tunresolved_j_per_h\tatom_energy_j_per_h")?;
    for (i, q) in ledger.iter().enumerate() {
        writeln!(
            file,
            "{i}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            q.native_number_per_h,
            q.com_number_per_h,
            q.native_energy_j_per_h,
            q.com_energy_j_per_h,
            q.centroid_proxy_j_per_h,
            q.unresolved_j_per_h,
            q.atom_energy_j_per_h
        )?;
    }
    file.flush()?;
    let mut file = BufWriter::new(fs::File::create(out.join("run.txt"))?);
    let (number, free, implicit_residual, it, kr) = if let Ok(q) = &solve {
        (
            q.number_defect,
            q.free_energy_change,
            q.residual,
            q.iterations,
            q.krylov,
        )
    } else {
        (-1., -1., -1., 0, 0)
    };
    writeln!(file,"scope=source_conditioned_scalar_COM_KHW_no_population_feedback\nangles={na}\nell={ell}\nclock={clock_name}\ndt_s={dt:.17e}\ngram_defect={:.17e}\nframe_roundtrip={:.17e}\nforce_relative_defect={:.17e}\nnumber_relative_to_l1={:.17e}\nnumber_residual={:.17e}\nboundary_number_relative_to_l1={:.17e}\nnormal_number_per_eta={:.17e}\nnumber_l1={:.17e}\nentropy_rate={:.17e}\nequilibrium_action_max={:.17e}\nimplicit_status={}\nimplicit_residual={implicit_residual:.17e}\nimplicit_iterations={it}\nimplicit_krylov={kr}\nimplicit_number_defect={number:.17e}\nimplicit_free_energy_change={free:.17e}\nimplicit_wall_s={elapsed:.9}\nexplicit_min={:.17e}",
 b.grid.gram_defect,frame.roundtrip,normal.force_relative_defect,a.number_residual.abs()/a.number_l1.max(f64::MIN_POSITIVE),a.number_residual,boundary.number_residual.abs()/boundary.number_l1.max(f64::MIN_POSITIVE),normal.number_per_eta,a.number_l1,a.entropy_rate,null.occupation.amax(),if solve.is_ok(){"PASS"}else{"REJECTED"},DMatrix::from_fn(na,n,|k,i|f[(k,i)]+dt*clock[k]*a.occupation[(k,i)]+inc[(k,i)]).min())?;
    if let Some(e) = step_err {
        writeln!(file, "implicit_error={e}")?;
    }
    for k in 0..4 {
        writeln!(file,"q_gamma_{k}={:.17e}\nq_atom_{k}={:.17e}\nq_normal_eta_{k}={:.17e}\nq_atom_normal_eta_{k}={:.17e}",a.q_gamma[k],a.q_atom[k],normal.q_gamma_per_eta[k],normal.q_atom_per_eta[k])?;
    }
    if let Some(s) = &sampled {
        writeln!(file,"bass_characteristic_steps={bass_steps}\nbass_landing_error={landing_error:.17e}\nbass_temperature_gap={temp_gap:.17e}\nbass_source_measure_defect={:.17e}\nbass_source_momentum_defect={:.17e}\nbass_cell_energy_projection_defect={:.17e}\nbass_H_s={h:.17e}",s.source_measure_defect,s.source_momentum_defect,s.cell_energy_projection_defect)?;
        let mut tf = BufWriter::new(fs::File::create(out.join("temperature.tsv"))?);
        writeln!(tf, "angle\tT_h_K")?;
        for (i, t) in s.temperature_h.iter().enumerate() {
            writeln!(tf, "{i}\t{t:.17e}")?;
        }
        tf.flush()?;
    }
    file.flush()?;
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("{e}");
        std::process::exit(1)
    }
}
