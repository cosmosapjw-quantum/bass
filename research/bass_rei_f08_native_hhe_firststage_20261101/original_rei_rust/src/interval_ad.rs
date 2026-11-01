//! Seven-variable second-order interval automatic differentiation.
use crate::interval_math::{Interval, IntervalError, Result};

const N: usize = 7;

#[derive(Clone, Debug)]
pub struct Jet {
    pub value: Interval,
    pub gradient: [Interval; N],
    pub hessian: [[Interval; N]; N],
}

fn zero() -> Interval {
    Interval { lo: 0.0, hi: 0.0 }
}

impl Jet {
    pub fn constant(value: Interval) -> Result<Self> {
        value.valid()?;
        Ok(Self {
            value,
            gradient: [zero(); N],
            hessian: [[zero(); N]; N],
        })
    }
    pub fn variable(value: Interval, index: usize) -> Result<Self> {
        if index >= N {
            return Err(IntervalError);
        }
        let mut out = Self::constant(value)?;
        out.gradient[index] = Interval::point(1.0)?;
        Ok(out)
    }
    fn valid(&self) -> Result<()> {
        self.value.valid()?;
        for v in self.gradient.iter().chain(self.hessian.iter().flatten()) {
            v.valid()?;
        }
        Ok(())
    }
    pub fn add(&self, rhs: &Self) -> Result<Self> {
        self.valid()?;
        rhs.valid()?;
        let mut out = Self::constant(self.value.add(&rhs.value)?)?;
        for i in 0..N {
            out.gradient[i] = self.gradient[i].add(&rhs.gradient[i])?;
            for j in 0..N {
                out.hessian[i][j] = self.hessian[i][j].add(&rhs.hessian[i][j])?;
            }
        }
        Ok(out)
    }
    pub fn neg(&self) -> Result<Self> {
        self.valid()?;
        let mut out = Self::constant(self.value.neg()?)?;
        for i in 0..N {
            out.gradient[i] = self.gradient[i].neg()?;
            for j in 0..N {
                out.hessian[i][j] = self.hessian[i][j].neg()?;
            }
        }
        Ok(out)
    }
    pub fn sub(&self, rhs: &Self) -> Result<Self> {
        self.add(&rhs.neg()?)
    }
    pub fn mul(&self, rhs: &Self) -> Result<Self> {
        self.valid()?;
        rhs.valid()?;
        let mut out = Self::constant(self.value.mul(&rhs.value)?)?;
        for i in 0..N {
            out.gradient[i] = self.gradient[i]
                .mul(&rhs.value)?
                .add(&self.value.mul(&rhs.gradient[i])?)?;
            for j in 0..N {
                out.hessian[i][j] = self.hessian[i][j]
                    .mul(&rhs.value)?
                    .add(&self.gradient[i].mul(&rhs.gradient[j])?)?
                    .add(&self.gradient[j].mul(&rhs.gradient[i])?)?
                    .add(&self.value.mul(&rhs.hessian[i][j])?)?;
            }
        }
        Ok(out)
    }
    fn chain(&self, value: Interval, first: Interval, second: Interval) -> Result<Self> {
        self.valid()?;
        let mut out = Self::constant(value)?;
        for i in 0..N {
            out.gradient[i] = first.mul(&self.gradient[i])?;
            for j in 0..N {
                out.hessian[i][j] = second
                    .mul(&self.gradient[i])?
                    .mul(&self.gradient[j])?
                    .add(&first.mul(&self.hessian[i][j])?)?;
            }
        }
        Ok(out)
    }
    fn inverse(&self) -> Result<Self> {
        self.valid()?;
        let one = Interval::point(1.0)?;
        let two = Interval::point(2.0)?;
        let value = one.div(&self.value)?;
        let square = value.mul(&value)?;
        let first = square.neg()?;
        let second = two.mul(&square)?.mul(&value)?;
        self.chain(value, first, second)
    }
    pub fn div(&self, rhs: &Self) -> Result<Self> {
        self.mul(&rhs.inverse()?)
    }
    pub fn exp(&self) -> Result<Self> {
        let value = self.value.exp()?;
        self.chain(value, value, value)
    }
    pub fn ln(&self) -> Result<Self> {
        let value = self.value.ln()?;
        let first = Interval::point(1.0)?.div(&self.value)?;
        let second = first.mul(&first)?.neg()?;
        self.chain(value, first, second)
    }
    pub fn powf(&self, p: f64) -> Result<Self> {
        self.valid()?;
        if self.value.lo <= 0.0 || !p.is_finite() {
            return Err(IntervalError);
        }
        if p == 0.0 {
            return Self::constant(Interval::point(1.0)?);
        }
        if p == 1.0 {
            return Ok(self.clone());
        }
        let value = self.value.powf(p)?;
        let ip = Interval::point(p)?;
        let first = ip.mul(&value)?.div(&self.value)?;
        let p_minus_one = ip.sub(&Interval::point(1.0)?)?;
        let second = ip
            .mul(&p_minus_one)?
            .mul(&value)?
            .div(&self.value.mul(&self.value)?)?;
        self.chain(value, first, second)
    }
}
