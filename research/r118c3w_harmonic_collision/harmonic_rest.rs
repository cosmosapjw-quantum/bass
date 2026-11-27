
    // Research-only homogeneous Bianchi-I rest-electron closure.
    // Preserve inversion parity exactly; no O(1) pixel collision round trip.
    fn c3w_parity(s: &mut HarmonicSky) {
        use crate::kinetic::spin_sht::{index,C64};
        for l in 0..=s.lmax() {
            for m in -(l as i64)..=l as i64 {
                let k=index(l,m);
                if l%2==1 {s.coefficients[0][k]=C64::new(0.,0.);}
                if l<2 {s.coefficients[1][k]=C64::new(0.,0.);s.coefficients[2][k]=C64::new(0.,0.);}
                else if l%2==0 {
                    let e=(s.coefficients[1][k]+s.coefficients[2][k])*0.5;
                    s.coefficients[1][k]=e;s.coefficients[2][k]=e;
                } else {
                    let b=(s.coefficients[1][k]-s.coefficients[2][k])*0.5;
                    s.coefficients[1][k]=b;s.coefficients[2][k]=-b;
                }
            }
        }
    }
    fn radiation(old:&HarmonicSky,at:&RayNode,du:f64,depth:f64)->Result<(HarmonicSky,f64),String> {
        use crate::kinetic::spin_sht::index;
        if !depth.is_finite()||depth<0.{return Err("C3W depth".into())}
        let mut s=old.clone();
        let a=RayNode{eta:0.,..at.clone()};
        let b=RayNode{eta:du/2.,..a.clone()};
        s.stream(&a,&b)?;Self::c3w_parity(&mut s);
        let e0=s.coefficients[0][0];let d=(8_f64/3.).sqrt();
        let z=(-depth).exp();let t=(-0.3*depth).exp()*(-(-0.7*depth).exp_m1())/0.7;
        for l in 1..=s.lmax() {
            for m in -(l as i64)..=l as i64 {
                let k=index(l,m);
                if l==2{
                    let i=s.coefficients[0][k];let e=-(s.coefficients[1][k]+s.coefficients[2][k])*0.5;
                    let ni=z*i+t*(0.1*i+0.4/d*e);
                    let ne=z*e+t*(0.15*d*i+0.6*e);
                    s.coefficients[0][k]=ni;s.coefficients[1][k]=-ne;s.coefficients[2][k]=-ne;
                } else {for slot in &mut s.coefficients{slot[k]*=z;}}
            }
        }
        assert_eq!(s.coefficients[0][0],e0);
        let c=RayNode{eta:du,..a.clone()};s.stream(&b,&c)?;
        Self::c3w_parity(&mut s);s.moments()?;Ok((s,0.))
    }
