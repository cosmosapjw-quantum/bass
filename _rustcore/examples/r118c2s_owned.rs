use bianchi_rustcore::kinetic::owned_vlasov::OwnedModel;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = std::env::args().skip(1).collect::<Vec<_>>();
    let eps: f64 = p[0].parse()?;
    let n: usize = p[1].parse()?;
    let nr: usize = p[2].parse()?;
    let nt: usize = p[3].parse()?;
    let model = OwnedModel::new(eps, nr, nt, 2 * nt)?;
    let mut s = model.initial(1. / 21., [eps / 3., 0., 0., 0., eps / 4.])?;
    let du = (21_f64 / 5.).ln() / n as f64;
    println!("u,a,h,S0,S1,S2,S3,S4,F00,F01,F02,F10,F11,F12,F20,F21,F22,gauss,det,rho,p,photon");
    for j in 0..=n {
        let m = model.matter(s.a, &s.f)?;
        print!("{:.17e},{:.17e},{:.17e}", j as f64 * du, s.a, s.h);
        for v in s.s {
            print!(",{v:.17e}")
        }
        for i in 0..3 {
            for k in 0..3 {
                print!(",{:.17e}", s.f[(i, k)])
            }
        }
        println!(
            ",{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            model.constraint(&s)?,
            s.f.determinant(),
            m.rho,
            m.pressure.trace() / 3.,
            m.photon_rho
        );
        if j < n {
            s = model.step(&s, du)?;
        }
    }
    Ok(())
}
