//! Bounded C2D experiment: source-lifted scalar collision plus two-moment
//! local reservoir advection. No thermochemistry or angular transport.
use bianchi_rustcore::homogeneous_sky::{
    dual_source::{Cell, DualTransport},
    positive_event::Graph,
};
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
fn sum(x: impl Iterator<Item = f64>) -> f64 {
    let (mut s, mut c) = (0., 0.);
    for v in x {
        let y = v - c;
        let t = s + y;
        c = (t - s) - y;
        s = t;
    }
    s
}
fn get(a: usize, order: &[usize], ext: usize, full: &[Vec<Cell>]) -> Vec<f64> {
    let mut m = vec![0.; 2 * a * order.len()];
    for (j, i) in order.iter().enumerate() {
        for k in 0..a {
            m[(2 * i) * a + k] = full[k][ext + j].left;
            m[(2 * i + 1) * a + k] = full[k][ext + j].right;
        }
    }
    m
}
fn set(a: usize, order: &[usize], ext: usize, full: &mut [Vec<Cell>], m: &[f64]) {
    for (j, i) in order.iter().enumerate() {
        for k in 0..a {
            full[k][ext + j] = Cell {
                left: m[2 * i * a + k],
                right: m[(2 * i + 1) * a + k],
            };
        }
    }
}
#[derive(Default)]
struct Ledger {
    esc_n: f64,
    esc_x: f64,
    work: f64,
    collision: f64,
    core_projection: f64,
    core_work_x: f64,
    face_x: f64,
    core_centered: f64,
    exterior_centered: f64,
    ext_projection: f64,
    ri: f64,
    ro: f64,
    bi: f64,
    bo: f64,
    dn: f64,
    dx: f64,
    cn: f64,
    en: f64,
    collision_n: f64,
    collision_x: f64,
    force: f64,
    free_inc: f64,
}
fn run() -> Result<(), Box<dyn std::error::Error>> {
    let arg: Vec<_> = env::args().skip(1).collect();
    if arg.len() != 3 {
        return Err("usage: dual_source_bridge GRAPH CASE OUT".into());
    }
    let g = Graph::load(Path::new(&arg[0]))?;
    let a = g.angles();
    let n = g.modes.len();
    if n != 70 {
        return Err("expected 70 lifted modes".into());
    }
    let raw = fs::read_to_string(&arg[1])?;
    let mut t = Tok(raw.split_whitespace());
    if t.word()? != "rec_dual_source_case_v1" {
        return Err("invalid case".into());
    }
    let dt: f64 = t.num()?;
    let steps: usize = t.num()?;
    let nu0: f64 = t.num()?;
    let dnu: f64 = t.num()?;
    if !dt.is_finite() || dt < 0. || steps > 4096 || steps == 0 && dt > 0. || nu0 <= 0. || dnu <= 0.
    {
        return Err("invalid clock/line".into());
    }
    let x = t.vec(n)?;
    let clock = t.vec(a)?;
    let f = t.vec(n * a)?;
    let initial = g.to_mass(&f, &clock)?;
    let mut moment_err: f64 = 0.;
    for i in 0..n {
        moment_err = moment_err.max((g.modes[i].p / (H * (nu0 + dnu * x[i]) / C) - 1.).abs());
    }
    if moment_err > 1e-12 {
        return Err("incompatible source node momenta".into());
    }
    let action = g.action(&initial, &clock)?;
    let action_x = sum(action.rate.iter().enumerate().map(|(i, v)| v * x[i / a]));
    let mut transport = None;
    let mut full = vec![];
    let mut order = vec![];
    let mut ext = 0;
    let mut shift1 = vec![];
    let mut shift2 = vec![];
    let flag: usize = t.num()?;
    if flag != 0 {
        if steps == 0 || steps % 2 != 0 || clock.iter().any(|v| *v != 1.) {
            return Err("live drift requires material clock and even steps".into());
        }
        ext = t.num()?;
        let extent: f64 = t.num()?;
        if ext == 0 || ext > 128 || extent <= 21.25 {
            return Err("invalid exterior".into());
        }
        order = (0..n / 2).collect::<Vec<_>>();
        order.sort_by(|i, j| x[2 * i].total_cmp(&x[2 * j]));
        if x[2 * order[0]] != -21.25
            || x[2 * order[order.len() - 1] + 1] != 21.25
            || order.windows(2).any(|v| x[2 * v[0] + 1] != x[2 * v[1]])
        {
            return Err("noncontiguous source".into());
        }
        let mut edges = (0..ext)
            .map(|i| -extent + (extent - 21.25) * i as f64 / ext as f64)
            .collect::<Vec<_>>();
        edges.extend(order.iter().map(|i| x[2 * i]));
        edges.push(21.25);
        edges.extend((1..=ext).map(|i| 21.25 + (extent - 21.25) * i as f64 / ext as f64));
        let tr = DualTransport::new(edges, nu0, dnu, -21.25, 21.25)?;
        shift1 = t.vec(a)?;
        shift2 = t.vec(a)?;
        let outside = t.vec(2 * ext * a)?;
        let b = dnu / nu0;
        let fac = 8. * std::f64::consts::PI * nu0 * nu0 * dnu / C.powi(3);
        // Exact phase-space endpoint hat volumes for constant occupation.
        let hat = |l: f64, r: f64, f: f64, w: f64| {
            let u = 1. + b * l;
            let v = 1. + b * r;
            let scale = fac * (r - l) * f * w / 12.;
            Cell {
                left: scale * (3. * u * u + 2. * u * v + v * v),
                right: scale * (u * u + 2. * u * v + 3. * v * v),
            }
        };
        for k in 0..a {
            let mut m = vec![Cell::default(); n / 2 + 2 * ext];
            for j in 0..ext {
                let j1 = ext + n / 2 + j;
                m[j] = hat(
                    tr.edges[j],
                    tr.edges[j + 1],
                    outside[2 * ext * k + j],
                    g.weights[k],
                );
                m[j1] = hat(
                    tr.edges[j1],
                    tr.edges[j1 + 1],
                    outside[2 * ext * k + ext + j],
                    g.weights[k],
                );
            }
            full.push(m)
        }
        set(a, &order, ext, &mut full, &initial);
        transport = Some(tr);
    }
    if t.0.next().is_some() {
        return Err("trailing case input".into());
    }
    let state = |m: &[f64], full: &Vec<Vec<Cell>>| -> (f64, f64) {
        if let Some(tr) = &transport {
            (
                sum(full.iter().map(|m| tr.number(m))),
                sum(full.iter().map(|m| tr.detuning(m))),
            )
        } else {
            (
                sum(m.iter().copied()),
                sum(m.iter().enumerate().map(|(i, v)| v * x[i / a])),
            )
        }
    };
    let mut m = initial.clone();
    let (n0, x0) = state(&m, &full);
    let mut l = Ledger::default();
    let mut history = vec![(0., n0, x0, 0., 0., 0., 0., 0., 0.)];
    for k in 0..steps {
        let shift = if k < steps / 2 { &shift1 } else { &shift2 };
        let drift = |full: &mut Vec<Vec<Cell>>, l: &mut Ledger| -> Result<(), String> {
            if let Some(tr) = &transport {
                for (j, v) in full.iter_mut().enumerate() {
                    let q = tr.shift(v, shift[j] / steps as f64)?;
                    l.esc_n += q.escaped_mass;
                    l.esc_x += q.escaped_x;
                    l.work += q.work_x;
                    l.core_projection += q.projection_core_x;
                    l.core_work_x += q.core_work_x;
                    l.face_x += q.face_x;
                    l.core_centered = l.core_centered.max(q.core_centered_defect);
                    l.exterior_centered = l.exterior_centered.max(q.exterior_centered_defect);
                    l.ext_projection += q.projection_exterior_x;
                    l.ri += q.red_in;
                    l.ro += q.red_out;
                    l.bi += q.blue_in;
                    l.bo += q.blue_out;
                    l.dn = l.dn.max(q.number_defect);
                    l.dx = l.dx.max(q.centered_defect);
                    l.cn = l.cn.max(q.core_number_defect);
                    l.en = l.en.max(q.exterior_number_defect);
                    *v = q.cells;
                }
            }
            Ok(())
        };
        if transport.is_some() {
            drift(&mut full, &mut l)?;
            m = get(a, &order, ext, &full);
        }
        let q = g.step_with_detuning(&m, &clock, dt / steps as f64, &x)?;
        l.collision += q.centered_exchange;
        l.collision_n = l.collision_n.max(q.number_defect);
        l.collision_x = l.collision_x.max(q.centered_defect);
        l.force = l.force.max(q.force_defect);
        l.free_inc = l.free_inc.max(q.free_change);
        m = q.mass;
        if transport.is_some() {
            set(a, &order, ext, &mut full, &m);
            drift(&mut full, &mut l)?;
            m = get(a, &order, ext, &full);
        }
        let (n, xx) = state(&m, &full);
        history.push((
            (k + 1) as f64 * dt / steps as f64,
            n,
            xx,
            l.esc_n,
            l.esc_x,
            l.work,
            l.collision,
            l.core_projection,
            l.ext_projection,
        ));
    }
    let out = Path::new(&arg[2]);
    if out.exists() {
        return Err("output exists".into());
    }
    fs::create_dir_all(out)?;
    let final_f = g.to_occupation(&m, &clock)?;
    let mut file = BufWriter::new(fs::File::create(out.join("state.tsv"))?);
    writeln!(
        file,
        "mode\tangle\tx\tinitial_f\tfinal_f\tinitial_mass\tfinal_mass\tmass_action"
    )?;
    for i in 0..m.len() {
        writeln!(
            file,
            "{}\t{}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            i / a,
            i % a,
            x[i / a],
            f[i],
            final_f[i],
            initial[i],
            m[i],
            action.rate[i]
        )?;
    }
    file.flush()?;
    let mut file = BufWriter::new(fs::File::create(out.join("history.tsv"))?);
    writeln!(file,"t_s\tmass\tx_mass\tescape_mass\tescape_x\twork_x\tcollision_x\tcore_projection_x\texterior_projection_x")?;
    for q in &history {
        writeln!(
            file,
            "{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
            q.0, q.1, q.2, q.3, q.4, q.5, q.6, q.7, q.8
        )?;
    }
    file.flush()?;
    if let Some(tr) = &transport {
        let mut file = BufWriter::new(fs::File::create(out.join("full.tsv"))?);
        writeln!(file, "angle\txlo\txhi\tleft_mass\tright_mass")?;
        for (k, v) in full.iter().enumerate() {
            for (j, m) in v.iter().enumerate() {
                writeln!(
                    file,
                    "{}\t{:.17e}\t{:.17e}\t{:.17e}\t{:.17e}",
                    k,
                    tr.edges[j],
                    tr.edges[j + 1],
                    m.left,
                    m.right
                )?;
            }
        }
        file.flush()?;
    }
    let (_, n1, x1, _, _, _, _, _, _) = *history.last().unwrap();
    let scale = n0.max(f64::MIN_POSITIVE);
    let xs = scale
        * transport
            .as_ref()
            .map(|t| t.edges.iter().map(|x| x.abs()).fold(1., f64::max))
            .unwrap_or(21.25)
        + l.work.abs();
    let mut file = BufWriter::new(fs::File::create(out.join("run.txt"))?);
    writeln!(file,"scope=dual_source_local_frozen_scalar\nangles={a}\nsteps={steps}\nnumber_defect={:.17e}\ncentered_balance_defect={:.17e}\ncentered_absolute_defect={:.17e}\ncollision_x={:.17e}\ncollision_energy_j_m3={:.17e}\ncore_projection_x={:.17e}\nexterior_projection_x={:.17e}\nmax_collision_number_defect={:.17e}\nmax_collision_centered_defect={:.17e}\nmax_force_defect={:.17e}\nmax_drift_number_defect={:.17e}\nmax_drift_centered_defect={:.17e}\nmax_core_number_defect={:.17e}\nmax_exterior_number_defect={:.17e}\nred_in={:.17e}\nred_out={:.17e}\nblue_in={:.17e}\nblue_out={:.17e}\ninterface_atom_energy=0\naction_number_defect={:.17e}\naction_x={:.17e}\naction_force_defect={:.17e}\nminimum_occupation={:.17e}\nmax_free_increase={:.17e}\nmomentum_node_error={:.17e}",
    (n1+l.esc_n-n0).abs()/scale,(x1+l.esc_x-x0-l.work-l.collision).abs()/xs,(x1+l.esc_x-x0-l.work-l.collision).abs(),l.collision,l.collision*H*dnu,l.core_projection,l.ext_projection,l.collision_n,l.collision_x,l.force,l.dn,l.dx,l.cn,l.en,l.ri,l.ro,l.bi,l.bo,action.number_defect,action_x,action.force_defect,final_f.iter().copied().fold(f64::INFINITY,f64::min),l.free_inc,moment_err)?;
    writeln!(file,"core_work_x={:.17e}\ninterface_face_x={:.17e}\nmax_core_centered_defect={:.17e}\nmax_exterior_centered_defect={:.17e}\ninterface_face_energy_j_m3={:.17e}",l.core_work_x,l.face_x,l.core_centered,l.exterior_centered,H*(nu0*(l.ri+l.bi-l.ro-l.bo)+dnu*l.face_x))?;
    for i in 0..4 {
        writeln!(file, "action_q_{i}={:.17e}", action.q[i])?;
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
