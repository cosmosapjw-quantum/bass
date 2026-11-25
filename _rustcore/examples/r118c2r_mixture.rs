use bianchi_rustcore::kinetic::{
    massive_memory::FermiMemory,
    memory_mixture::{commutator_invariant, MemoryMixture, MemorySpecies},
};
use std::fs;
const OG: f64 = 5.4437488671046486e-5;
const ON: f64 = 3.7562511328953514e-5;
const OM: f64 = 0.315;
const OL: f64 = 0.684908;
const T: f64 = 0.00016763891604963858;
const H0: f64 = 2.1842852410855023e-18;
const EPS: f64 = 1e-5;
fn mix(case: &str) -> MemoryMixture {
    let (m, j) = match case {
        "misaligned" => (
            [0.001, 0.05],
            [[0., 1., 0., 0., 0.], [0., 0., 0.6, 0.8, 0.]],
        ),
        "equal_mass" => ([0.01, 0.01], [[0., 1., 0., 0., 0.], [0., 0., 0.6, 0.8, 0.]]),
        "aligned" => ([0.001, 0.05], [[0., 1., 0., 0., 0.], [0., 0.7, 0., 0., 0.]]),
        _ => panic!("case"),
    };
    let mut cold = OM + ON;
    let mut species = Vec::new();
    for k in 0..2 {
        let p = FermiMemory::new(m[k], T, ON / 2., 128).unwrap();
        let mem = vec![j[k].map(|x| x * EPS); p.nodes().len()];
        cold -= p.response(1., [0.; 5], &mem).unwrap().rho_a4;
        species.push(MemorySpecies {
            provider: p,
            memory: mem,
        });
    }
    MemoryMixture::new(species, OG, cold, OL).unwrap()
}
fn interp(x: &[(f64, f64)], u: f64) -> f64 {
    let i = x.partition_point(|r| r.0 <= u);
    if i == 0 {
        return x[0].1;
    }
    if i >= x.len() {
        return x[x.len() - 1].1;
    }
    let (a, y) = x[i - 1];
    let (b, z) = x[i];
    y + (z - y) * (u - a) / (b - a)
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let file = fs::read_to_string(&args[0])?;
    let input: Vec<(f64, f64)> = file
        .lines()
        .skip(1)
        .map(|l| {
            let mut p = l.split(',');
            (
                p.next().unwrap().parse().unwrap(),
                p.next().unwrap().parse().unwrap(),
            )
        })
        .collect();
    let name = &args[1];
    let n: usize = args[2].parse()?;
    let m = mix(name);
    let end = (21_f64 / 5.).ln();
    let dt = end / n as f64;
    let rhs = |u: f64, v: [f64; 21]| -> Result<[f64; 21], String> {
        let a = u.exp() / 21.;
        let s: [f64; 5] = std::array::from_fn(|i| EPS * v[i]);
        let a0 = std::array::from_fn(|i| EPS * v[5 + i]);
        let b = std::array::from_fn(|i| EPS * v[15 + i]);
        let x = m.moments(a, b, a0)?;
        let ds = m.shear_rhs(a, s, b, a0)?;
        let k = 299792458. * 6.6524587051e-29 * interp(&input, u) / (H0 * x.h_ratio);
        let mut d = [0.; 21];
        for i in 0..5 {
            d[i] = ds[i] / EPS;
            d[5 + i] = -4. * v[i] - k * (0.9 * v[5 + i] + 0.4 * v[10 + i]);
            d[10 + i] = -k * (0.15 * v[5 + i] + 0.4 * v[10 + i]);
            d[15 + i] = v[i];
        }
        let sn = v[..5].iter().map(|x| x * x).sum::<f64>();
        let loss = (0..5)
            .map(|i| {
                1.8 * v[5 + i].powi(2) + 1.6 * v[5 + i] * v[10 + i] + 32. / 15. * v[10 + i].powi(2)
            })
            .sum::<f64>();
        d[20] =
            20. * sn / x.omega_gamma + k * loss + 30. * x.memory_dissipation_a4 / (OG * EPS * EPS);
        Ok(d)
    };
    let mut v = [0.; 21];
    println!("u,S0,S1,S2,S3,S4,A0,A1,A2,A3,A4,B0,B1,B2,B3,B4,beta0,beta1,beta2,beta3,beta4,Pi0,Pi1,Pi2,Pi3,Pi4,C,L,loss");
    for i in 0..=n {
        let u = dt * i as f64;
        let a = u.exp() / 21.;
        let s = std::array::from_fn(|i| v[i]);
        let beta = std::array::from_fn(|i| EPS * v[15 + i]);
        let aa = std::array::from_fn(|i| EPS * v[5 + i]);
        let x = m.moments(a, beta, aa)?;
        let pi = x.pi.map(|x| x / EPS);
        let lyap = 10. * v[..5].iter().map(|x| x * x).sum::<f64>() / x.omega_gamma
            + v[5..10].iter().map(|x| x * x).sum::<f64>()
            + 8. / 3. * v[10..15].iter().map(|x| x * x).sum::<f64>()
            + 30. * x.memory_energy_a4 / (OG * EPS * EPS);
        print!("{u:.17e}");
        for y in v[..20].iter().chain(pi.iter()) {
            print!(",{y:.17e}");
        }
        println!(
            ",{:.17e},{lyap:.17e},{:.17e}",
            commutator_invariant(s, pi),
            v[20]
        );
        if i < n {
            let k1 = rhs(u, v)?;
            let mid = std::array::from_fn(|j| v[j] + dt * k1[j] / 2.);
            let k2 = rhs(u + dt / 2., mid)?;
            v = std::array::from_fn(|j| v[j] + dt * k2[j]);
        }
    }
    Ok(())
}
