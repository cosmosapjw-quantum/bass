//! Positive REC event graph replay and frozen-direction local live exterior.
//! Source atomic calibration fixed. Not a complete HyRec exterior or a
//! self-consistent Bianchi trajectory.
use bianchi_rustcore::homogeneous_sky::positive_event::{Drift, Graph, Transport};
use std::{
    env, fs,
    io::{BufWriter, Write},
    path::Path,
};
const H: f64 = 6.62607015e-34;
const C: f64 = 299792458.;
struct Tok<'a>(std::str::SplitWhitespace<'a>);
impl<'a> Tok<'a> {
    fn word(&mut self) -> Result<&'a str, String> {
        self.0.next().ok_or("missing case token".into())
    }
    fn num<T: std::str::FromStr>(&mut self) -> Result<T, String> {
        self.word()?.parse().map_err(|_| "bad case token".into())
    }
    fn vec(&mut self, n: usize) -> Result<Vec<f64>, String> {
        (0..n).map(|_| self.num()).collect()
    }
}
#[derive(Default)]
struct Ledger {
    nerr: f64,
    eerr: f64,
    esc_n: f64,
    esc_e: f64,
    work: f64,
    projection: f64,
    projection_core: f64,
    projection_exterior: f64,
    core_number_defect: f64,
    exterior_number_defect: f64,
    red_in: f64,
    red_out: f64,
    blue_in: f64,
    blue_out: f64,
    red_e: f64,
    blue_e: f64,
    q: f64,
    collision_defect: f64,
    force: f64,
    free_increase: f64,
}
impl Ledger {
    fn drift(&mut self, d: &Drift) {
        self.nerr = self.nerr.max(d.number_defect);
        self.eerr = self.eerr.max(d.energy_defect);
        self.esc_n += d.escaped_mass;
        self.esc_e += d.escaped_energy;
        self.work += d.work;
        self.projection += d.projection;
        self.projection_core += d.projection_core;
        self.projection_exterior += d.projection_exterior;
        self.core_number_defect = self.core_number_defect.max(d.core_number_defect);
        self.exterior_number_defect = self.exterior_number_defect.max(d.exterior_number_defect);
        self.red_in += d.red_in;
        self.red_out += d.red_out;
        self.blue_in += d.blue_in;
        self.blue_out += d.blue_out;
        self.red_e += d.red_face_energy;
        self.blue_e += d.blue_face_energy;
    }
}
fn get_core(a: usize, order: &[usize], ext: usize, full: &[Vec<f64>]) -> Vec<f64> {
    let mut m = vec![0.; a * order.len()];
    for (j, i) in order.iter().enumerate() {
        for k in 0..a {
            m[i * a + k] = full[k][ext + j];
        }
    }
    m
}
fn set_core(a: usize, order: &[usize], ext: usize, full: &mut [Vec<f64>], m: &[f64]) {
    for (j, i) in order.iter().enumerate() {
        for k in 0..a {
            full[k][ext + j] = m[i * a + k];
        }
    }
}
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let arg: Vec<_> = env::args().skip(1).collect();
    if arg.len() != 3 {
        return Err("usage: positive_event_bridge GRAPH CASE OUT".into());
    }
    let started = std::time::Instant::now();
    let g = Graph::load(Path::new(&arg[0]))?;
    let n = g.modes.len();
    let a = g.angles();
    let raw = fs::read_to_string(&arg[1])?;
    let mut t = Tok(raw.split_whitespace());
    if t.word()? != "rec_positive_case_v1" {
        return Err("invalid case schema".into());
    }
    let duration: f64 = t.num()?;
    let steps: usize = t.num()?;
    if !duration.is_finite() || duration < 0. || steps > 8192 || duration > 0. && steps == 0 {
        return Err("invalid clock duration".into());
    }
    let clock = t.vec(a)?;
    let f = t.vec(n * a)?;
    let initial = g.to_mass(&f, &clock)?;
    let action = g.action(&initial, &clock)?;
    let eq: Vec<_> = g
        .modes
        .iter()
        .flat_map(|m| {
            let z = m.pi / m.g;
            let f = 0.5 * z / g.modes.iter().map(|m| m.pi / m.g).fold(0., f64::max);
            std::iter::repeat_n(f / (1. - f), a)
        })
        .collect();
    let eqm = g.to_mass(&eq, &clock)?;
    let eqa = g.action(&eqm, &clock)?;
    let eq_norm = eqm.iter().sum::<f64>();
    let eq_null = eqa.rate.iter().map(|v| v.abs()).sum::<f64>() / eq_norm;
    let drift: usize = t.num()?;
    let mut order = vec![];
    let mut full: Vec<Vec<f64>> = vec![];
    let mut trans = None;
    let mut ext = 0;
    let mut shift1 = vec![];
    let mut shift2 = vec![];
    let mut measure_gap: f64 = 0.;
    let mut centroid_gap: f64 = 0.;
    if drift != 0 {
        if clock.iter().any(|v| *v != 1.) || steps == 0 || steps % 2 != 0 {
            return Err("local exterior transport requires even material-clock steps".into());
        }
        let nu0: f64 = t.num()?;
        let dnu: f64 = t.num()?;
        ext = t.num()?;
        let extent: f64 = t.num()?;
        if !(1..=128).contains(&ext) || extent <= 21.25 {
            return Err("invalid exterior resolution".into());
        }
        let bounds: Vec<_> = (0..n)
            .map(|_| Ok([t.num::<f64>()?, t.num::<f64>()?]))
            .collect::<Result<_, String>>()?;
        order = (0..n).collect();
        order.sort_by(|i, j| bounds[*i][0].total_cmp(&bounds[*j][0]));
        if bounds[order[0]][0] != -21.25
            || bounds[*order.last().unwrap()][1] != 21.25
            || order.windows(2).any(|q| bounds[q[0]][1] != bounds[q[1]][0])
        {
            return Err("source domain not exact contiguous COM partition".into());
        }
        let mut edges = (0..ext)
            .map(|i| -extent + (extent - 21.25) * i as f64 / ext as f64)
            .collect::<Vec<_>>();
        edges.extend(order.iter().map(|i| bounds[*i][0]));
        edges.push(21.25);
        edges.extend((1..=ext).map(|i| 21.25 + (extent - 21.25) * i as f64 / ext as f64));
        let tr = Transport::new(edges, nu0, dnu, -21.25, 21.25)?;
        let b = dnu / nu0;
        let fac = 8. * std::f64::consts::PI * nu0 * nu0 * dnu / C.powi(3);
        let volume = |l: f64, r: f64| {
            let x = 1. + b * l;
            let y = 1. + b * r;
            fac * (r - l) * (x * x + x * y + y * y) / 3.
        };
        for i in 0..n {
            let l = bounds[i][0];
            let r = bounds[i][1];
            let x = 1. + b * l;
            let y = 1. + b * r;
            let v = volume(l, r);
            let p = H * nu0 / C * 0.75 * (x * x * x + x * x * y + x * y * y + y * y * y)
                / (x * x + x * y + y * y);
            measure_gap = measure_gap.max((v / g.modes[i].g - 1.).abs());
            centroid_gap = centroid_gap.max((p / g.modes[i].p - 1.).abs());
        }
        if measure_gap > 1e-10 || centroid_gap > 1e-10 {
            return Err("source transport moments do not match graph".into());
        }
        shift1 = t.vec(a)?;
        shift2 = t.vec(a)?;
        let outside = t.vec(2 * ext * a)?;
        if outside.iter().any(|x| !x.is_finite() || *x < 0.) {
            return Err("invalid exterior occupation".into());
        }
        for k in 0..a {
            let mut m = vec![0.; n + 2 * ext];
            for j in 0..ext {
                m[j] =
                    outside[k * 2 * ext + j] * g.weights[k] * volume(tr.edges[j], tr.edges[j + 1]);
                let j1 = ext + n + j;
                m[j1] = outside[k * 2 * ext + ext + j]
                    * g.weights[k]
                    * volume(tr.edges[j1], tr.edges[j1 + 1]);
            }
            full.push(m);
        }
        set_core(a, &order, ext, &mut full, &initial);
        trans = Some(tr);
    }
    if t.0.next().is_some() {
        return Err("trailing case token".into());
    }
    let mut ledger = Ledger::default();
    let mut m = initial.clone();
    let n0 = if trans.is_some() {
        full.iter().flatten().sum::<f64>()
    } else {
        m.iter().sum()
    };
    let e0 = if let Some(tr) = &trans {
        full.iter().map(|v| tr.energy(v)).sum::<f64>()
    } else {
        m.iter()
            .enumerate()
            .map(|(i, m)| C * g.modes[i / a].p * m)
            .sum()
    };
    let mut history = vec![(0., n0, e0, 0., 0., 0., 0., 0., 0., 0., 0.)];
    for k in 0..steps {
        let shift = if k < steps / 2 { &shift1 } else { &shift2 };
        let drift_half = |full: &mut Vec<Vec<f64>>, l: &mut Ledger| -> Result<(), String> {
            if let Some(tr) = &trans {
                for (j, r) in full.iter_mut().enumerate() {
                    let q = tr.shift(r, shift[j] / steps as f64)?;
                    l.drift(&q);
                    *r = q.mass;
                }
            }
            Ok(())
        };
        // Each half of the time interval uses its prescribed total log
        // shift; two half shifts per step make total shift exactly shift1/2+shift2/2 times 2.
        if trans.is_some() {
            drift_half(&mut full, &mut ledger)?;
            m = get_core(a, &order, ext, &full);
        }
        let q = g.step(&m, &clock, duration / steps as f64)?;
        ledger.collision_defect = ledger.collision_defect.max(q.number_defect);
        ledger.force = ledger.force.max(q.force_defect);
        ledger.free_increase = ledger.free_increase.max(q.free_change);
        ledger.q += C * q.event_q[0];
        m = q.mass;
        if trans.is_some() {
            set_core(a, &order, ext, &mut full, &m);
            drift_half(&mut full, &mut ledger)?;
            m = get_core(a, &order, ext, &full);
        }
        let nf = if trans.is_some() {
            full.iter().flatten().sum()
        } else {
            m.iter().sum::<f64>()
        };
        let ef = if let Some(tr) = &trans {
            full.iter().map(|r| tr.energy(r)).sum()
        } else {
            m.iter()
                .enumerate()
                .map(|(i, m)| C * g.modes[i / a].p * m)
                .sum::<f64>()
        };
        history.push((
            (k + 1) as f64 * duration / steps as f64,
            nf,
            ef,
            ledger.esc_n,
            ledger.esc_e,
            ledger.work,
            ledger.projection,
            ledger.q,
            ledger.red_in + ledger.blue_in,
            ledger.red_out + ledger.blue_out,
            ledger.red_e + ledger.blue_e,
        ));
    }
    let out = Path::new(&arg[2]);
    if out.exists() {
        return Err("output exists".into());
    }
    fs::create_dir_all(out)?;
    let final_f = g.to_occupation(&m, &clock)?;
    let mut file = BufWriter::new(fs::File::create(out.join("state.tsv"))?);
    writeln!(file,"state\tangle\tinitial_f\tfinal_f\tinitial_mass\tfinal_mass\tmass_action\toccupation_action")?;
    for i in 0..m.len() {
        let v = g.modes[i / a].g * g.weights[i % a] / clock[i % a];
        writeln!(
            file,
            "{}\t{}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            i / a,
            i % a,
            f[i],
            final_f[i],
            initial[i],
            m[i],
            action.rate[i],
            action.rate[i] / v
        )?;
    }
    file.flush()?;
    let mut file = BufWriter::new(fs::File::create(out.join("history.tsv"))?);
    writeln!(file,"t_s\tmass\tenergy_j_m3\tescape_mass\tescape_energy\tdrift_work\tprojection\tcollision_energy\tinterface_in\tinterface_out\tinterface_net_energy")?;
    for r in &history {
        writeln!(file,"{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",r.0,r.1,r.2,r.3,r.4,r.5,r.6,r.7,r.8,r.9,r.10)?;
    }
    file.flush()?;
    if let Some(tr) = &trans {
        let mut file = BufWriter::new(fs::File::create(out.join("full.tsv"))?);
        writeln!(file, "angle\tx_lo\tx_hi\tmass")?;
        for (k, r) in full.iter().enumerate() {
            for (j, m) in r.iter().enumerate() {
                writeln!(
                    file,
                    "{k}\t{:.17e}\t{:.17e}\t{m:.17e}",
                    tr.edges[j],
                    tr.edges[j + 1]
                )?;
            }
        }
        file.flush()?;
    }
    let last = history.last().unwrap();
    let number_defect = (last.1 + last.3 - n0).abs() / n0.max(f64::MIN_POSITIVE);
    let energy_defect =
        (last.2 + last.4 - e0 - last.5 - last.6 - last.7).abs() / e0.max(f64::MIN_POSITIVE);
    let mut file = BufWriter::new(fs::File::create(out.join("run.txt"))?);
    writeln!(file,"scope=positive_source_scalar_event_graph_local_conditional_drift\nangles={a}\nstates={n}\nblocks={}\nduration_s={duration:.17e}\nsteps={steps}\naction_number_defect={:.17e}\naction_force_defect={:.17e}\nfree_derivative={}\nequilibrium_null_per_s={eq_null:.17e}\nnumber_defect={number_defect:.17e}\nenergy_defect={energy_defect:.17e}\nmax_collision_number_defect={:.17e}\nmax_collision_force_defect={:.17e}\nmax_free_increase={:.17e}\nmax_drift_number_defect={:.17e}\nmax_drift_energy_defect={:.17e}\nminimum_occupation={:.17e}\nred_in={:.17e}\nred_out={:.17e}\nblue_in={:.17e}\nblue_out={:.17e}\nred_face_energy={:.17e}\nblue_face_energy={:.17e}\ninterface_atom_energy=0\nsource_measure_gap={measure_gap:.17e}\nsource_centroid_gap={centroid_gap:.17e}\nwall_s={:.9}",
        g.blocks.len(),action.number_defect,action.force_defect,action.free_derivative,ledger.collision_defect,ledger.force,ledger.free_increase,ledger.nerr,ledger.eerr,final_f.iter().copied().fold(f64::INFINITY,f64::min),ledger.red_in,ledger.red_out,ledger.blue_in,ledger.blue_out,ledger.red_e,ledger.blue_e,started.elapsed().as_secs_f64())?;
    writeln!(file,"projection_core={:.17e}\nprojection_exterior={:.17e}\nmax_core_number_defect={:.17e}\nmax_exterior_number_defect={:.17e}",ledger.projection_core,ledger.projection_exterior,ledger.core_number_defect,ledger.exterior_number_defect)?;
    for i in 0..4 {
        writeln!(
            file,
            "action_q_{i}={:.17e}\naction_event_q_{i}={:.17e}",
            action.q[i], action.event_q[i]
        )?;
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
