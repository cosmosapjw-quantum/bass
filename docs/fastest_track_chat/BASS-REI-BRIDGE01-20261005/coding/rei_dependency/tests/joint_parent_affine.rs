//! Exact, synthetic shared-parent affine certificates. This fixture makes no
//! claim about rounded production arithmetic or the nonlinear physical map.

use std::cmp::Ordering;

const MAX_EXPONENT: u32 = 64;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum CertificateError {
    ExponentOutOfDomain,
    ArithmeticOverflow,
    ParentIdMismatch,
    ReversedParent,
    ReversedClaim,
    UnderEnclosingClaim,
    StrictGateRejected,
}

type Checked<T> = Result<T, CertificateError>;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Dyadic {
    numerator: i128,
    exponent: u32,
}

impl Dyadic {
    const ZERO: Self = Self {
        numerator: 0,
        exponent: 0,
    };
    const ONE: Self = Self {
        numerator: 1,
        exponent: 0,
    };

    fn new(mut numerator: i128, mut exponent: u32) -> Checked<Self> {
        if exponent > MAX_EXPONENT {
            return Err(CertificateError::ExponentOutOfDomain);
        }
        if numerator == 0 {
            return Ok(Self::ZERO);
        }
        while exponent > 0 && numerator % 2 == 0 {
            numerator /= 2;
            exponent -= 1;
        }
        Ok(Self {
            numerator,
            exponent,
        })
    }

    fn validate(self) -> Checked<()> {
        if self.exponent > MAX_EXPONENT {
            Err(CertificateError::ExponentOutOfDomain)
        } else {
            Ok(())
        }
    }

    fn scaled_numerator(self, exponent: u32) -> Checked<i128> {
        let shift = exponent
            .checked_sub(self.exponent)
            .ok_or(CertificateError::ArithmeticOverflow)?;
        let scale = 2_i128
            .checked_pow(shift)
            .ok_or(CertificateError::ArithmeticOverflow)?;
        self.numerator
            .checked_mul(scale)
            .ok_or(CertificateError::ArithmeticOverflow)
    }

    fn add(self, other: Self) -> Checked<Self> {
        let exponent = self.exponent.max(other.exponent);
        let numerator = self
            .scaled_numerator(exponent)?
            .checked_add(other.scaled_numerator(exponent)?)
            .ok_or(CertificateError::ArithmeticOverflow)?;
        Self::new(numerator, exponent)
    }

    fn sub(self, other: Self) -> Checked<Self> {
        let exponent = self.exponent.max(other.exponent);
        let numerator = self
            .scaled_numerator(exponent)?
            .checked_sub(other.scaled_numerator(exponent)?)
            .ok_or(CertificateError::ArithmeticOverflow)?;
        Self::new(numerator, exponent)
    }

    fn mul(self, other: Self) -> Checked<Self> {
        let exponent = self
            .exponent
            .checked_add(other.exponent)
            .ok_or(CertificateError::ArithmeticOverflow)?;
        if exponent > MAX_EXPONENT {
            return Err(CertificateError::ExponentOutOfDomain);
        }
        let numerator = self
            .numerator
            .checked_mul(other.numerator)
            .ok_or(CertificateError::ArithmeticOverflow)?;
        Self::new(numerator, exponent)
    }

    fn cmp_checked(self, other: Self) -> Checked<Ordering> {
        let exponent = self.exponent.max(other.exponent);
        Ok(self
            .scaled_numerator(exponent)?
            .cmp(&other.scaled_numerator(exponent)?))
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Range {
    lo: Dyadic,
    hi: Dyadic,
}

impl Range {
    fn from_endpoints(left: Dyadic, right: Dyadic) -> Checked<Self> {
        if left.cmp_checked(right)? == Ordering::Greater {
            Ok(Self {
                lo: right,
                hi: left,
            })
        } else {
            Ok(Self {
                lo: left,
                hi: right,
            })
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Parent {
    coordinate_id: &'static str,
    interval: Range,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct AffineMap {
    parent_id: &'static str,
    slope: Dyadic,
    intercept: Dyadic,
}

impl AffineMap {
    fn at(self, x: Dyadic) -> Checked<Dyadic> {
        self.slope.mul(x)?.add(self.intercept)
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Certificate {
    shared_parent_id: &'static str,
    parent: Parent,
    full: AffineMap,
    half: AffineMap,
    claimed_difference: Range,
}

fn validate_parent_identity(parent: Parent, full: AffineMap, half: AffineMap) -> Checked<()> {
    for value in [
        parent.interval.lo,
        parent.interval.hi,
        full.slope,
        full.intercept,
        half.slope,
        half.intercept,
    ] {
        value.validate()?;
    }
    if parent.coordinate_id != full.parent_id || parent.coordinate_id != half.parent_id {
        return Err(CertificateError::ParentIdMismatch);
    }
    if parent.interval.lo.cmp_checked(parent.interval.hi)? == Ordering::Greater {
        return Err(CertificateError::ReversedParent);
    }
    Ok(())
}

// Generator: derive the difference's coefficients symbolically.
fn generate(parent: Parent, full: AffineMap, half: AffineMap) -> Checked<Certificate> {
    validate_parent_identity(parent, full, half)?;
    let slope = full.slope.sub(half.slope.mul(half.slope)?)?;
    let intercept = full
        .intercept
        .sub(half.slope.add(Dyadic::ONE)?.mul(half.intercept)?)?;
    let difference = AffineMap {
        parent_id: parent.coordinate_id,
        slope,
        intercept,
    };
    let claimed_difference = Range::from_endpoints(
        difference.at(parent.interval.lo)?,
        difference.at(parent.interval.hi)?,
    )?;
    Ok(Certificate {
        shared_parent_id: parent.coordinate_id,
        parent,
        full,
        half,
        claimed_difference,
    })
}

// Checker: evaluate F(x)-H(H(x)) directly at each *same* parent endpoint.
// It does not use the generator's derived slope, intercept, or range.
fn check(certificate: Certificate) -> Checked<()> {
    let Certificate {
        shared_parent_id,
        parent,
        full,
        half,
        claimed_difference,
    } = certificate;
    validate_parent_identity(parent, full, half)?;
    claimed_difference.lo.validate()?;
    claimed_difference.hi.validate()?;
    if shared_parent_id != parent.coordinate_id {
        return Err(CertificateError::ParentIdMismatch);
    }
    if claimed_difference.lo.cmp_checked(claimed_difference.hi)? == Ordering::Greater {
        return Err(CertificateError::ReversedClaim);
    }
    let at_shared_parent = |x| -> Checked<Dyadic> { full.at(x)?.sub(half.at(half.at(x)?)?) };
    let actual = Range::from_endpoints(
        at_shared_parent(parent.interval.lo)?,
        at_shared_parent(parent.interval.hi)?,
    )?;
    if claimed_difference.lo.cmp_checked(actual.lo)? == Ordering::Greater
        || claimed_difference.hi.cmp_checked(actual.hi)? == Ordering::Less
    {
        return Err(CertificateError::UnderEnclosingClaim);
    }
    Ok(())
}

fn strict_gate(certificate: Certificate, threshold: Dyadic) -> Checked<()> {
    check(certificate)?;
    let lower_magnitude = Dyadic::ZERO.sub(certificate.claimed_difference.lo)?;
    if lower_magnitude.cmp_checked(threshold)? != Ordering::Less
        || certificate.claimed_difference.hi.cmp_checked(threshold)? != Ordering::Less
    {
        return Err(CertificateError::StrictGateRejected);
    }
    Ok(())
}

fn d(numerator: i128, exponent: u32) -> Dyadic {
    Dyadic::new(numerator, exponent).expect("valid fixture dyadic")
}

fn parent(lo: Dyadic, hi: Dyadic) -> Parent {
    Parent {
        coordinate_id: "shared-x",
        interval: Range { lo, hi },
    }
}

fn map(slope: Dyadic, intercept: Dyadic) -> AffineMap {
    AffineMap {
        parent_id: "shared-x",
        slope,
        intercept,
    }
}

#[test]
fn coincident_maps_cancel_on_shared_parent_despite_independent_box_separation() {
    let parent = parent(d(0, 0), d(1, 0));
    let half = map(d(1, 1), d(1, 2));
    let full = map(d(1, 2), d(3, 3));
    let certificate = generate(parent, full, half).unwrap();
    assert_eq!(
        certificate.claimed_difference,
        Range {
            lo: d(0, 0),
            hi: d(0, 0)
        }
    );
    assert_eq!(check(certificate), Ok(()));

    let full_box = Range::from_endpoints(
        full.at(parent.interval.lo).unwrap(),
        full.at(parent.interval.hi).unwrap(),
    )
    .unwrap();
    let half_box = Range::from_endpoints(
        half.at(half.at(parent.interval.lo).unwrap()).unwrap(),
        half.at(half.at(parent.interval.hi).unwrap()).unwrap(),
    )
    .unwrap();
    let expected_box = Range {
        lo: d(3, 3),
        hi: d(5, 3),
    };
    assert_eq!(full_box, expected_box);
    assert_eq!(half_box, expected_box);
    assert_eq!(full_box.hi.sub(half_box.lo), Ok(d(1, 2)));
}

#[test]
fn nonzero_joint_difference_rejects_strict_gate_without_candidate_state() {
    let certificate = generate(
        parent(d(0, 0), d(1, 0)),
        map(d(1, 0), d(0, 0)),
        map(d(1, 1), d(0, 0)),
    )
    .unwrap();
    assert_eq!(
        certificate.claimed_difference,
        Range {
            lo: d(0, 0),
            hi: d(3, 2)
        }
    );
    assert_eq!(check(certificate), Ok(()));
    let mut candidate_state = None;
    if strict_gate(certificate, d(1, 1)).is_ok() {
        candidate_state = Some(());
    }
    assert_eq!(
        strict_gate(certificate, d(1, 1)),
        Err(CertificateError::StrictGateRejected)
    );
    assert_eq!(candidate_state, None);
}

#[test]
fn invalid_parent_identity_and_intervals_fail_closed() {
    let base_parent = parent(d(0, 0), d(1, 0));
    let full = map(d(1, 0), d(0, 0));
    let half = map(d(1, 1), d(0, 0));
    let valid = generate(base_parent, full, half).unwrap();

    let different_half_parent = AffineMap {
        parent_id: "other-x",
        ..half
    };
    assert_eq!(
        generate(base_parent, full, different_half_parent),
        Err(CertificateError::ParentIdMismatch)
    );
    assert_eq!(
        check(Certificate {
            half: different_half_parent,
            ..valid
        }),
        Err(CertificateError::ParentIdMismatch)
    );
    assert_eq!(
        check(Certificate {
            shared_parent_id: "other-x",
            ..valid
        }),
        Err(CertificateError::ParentIdMismatch)
    );

    let reversed = parent(d(1, 0), d(0, 0));
    assert_eq!(
        generate(reversed, full, half),
        Err(CertificateError::ReversedParent)
    );
    assert_eq!(
        check(Certificate {
            parent: reversed,
            ..valid
        }),
        Err(CertificateError::ReversedParent)
    );
    let reversed_claim = Range {
        lo: d(1, 0),
        hi: d(0, 0),
    };
    assert_eq!(
        check(Certificate {
            claimed_difference: reversed_claim,
            ..valid
        }),
        Err(CertificateError::ReversedClaim)
    );
}

#[test]
fn overflow_and_out_of_domain_exponents_fail_closed() {
    assert_eq!(
        Dyadic::new(1, MAX_EXPONENT + 1),
        Err(CertificateError::ExponentOutOfDomain)
    );
    let overflow_parent = parent(d(2, 0), d(2, 0));
    let full = map(d(i128::MAX, 0), d(0, 0));
    let half = map(d(0, 0), d(0, 0));
    assert_eq!(
        generate(overflow_parent, full, half),
        Err(CertificateError::ArithmeticOverflow)
    );
    let certificate = Certificate {
        shared_parent_id: overflow_parent.coordinate_id,
        parent: overflow_parent,
        full,
        half,
        claimed_difference: Range {
            lo: d(0, 0),
            hi: d(0, 0),
        },
    };
    assert_eq!(
        check(certificate),
        Err(CertificateError::ArithmeticOverflow)
    );
    assert_eq!(
        d(1, MAX_EXPONENT).mul(d(1, 1)),
        Err(CertificateError::ExponentOutOfDomain)
    );

    let valid = generate(
        parent(d(0, 0), d(1, 0)),
        map(d(1, 0), d(0, 0)),
        map(d(1, 1), d(0, 0)),
    )
    .unwrap();
    let out_of_domain = Dyadic {
        numerator: 0,
        exponent: MAX_EXPONENT + 1,
    };
    assert_eq!(
        check(Certificate {
            claimed_difference: Range {
                lo: out_of_domain,
                ..valid.claimed_difference
            },
            ..valid
        }),
        Err(CertificateError::ExponentOutOfDomain)
    );
    assert_eq!(
        check(Certificate {
            full: AffineMap {
                intercept: out_of_domain,
                ..valid.full
            },
            ..valid
        }),
        Err(CertificateError::ExponentOutOfDomain)
    );
}

#[test]
fn claimed_range_must_enclose_both_shared_parent_endpoints() {
    let valid = generate(
        parent(d(0, 0), d(1, 0)),
        map(d(1, 0), d(0, 0)),
        map(d(1, 1), d(0, 0)),
    )
    .unwrap();
    assert_eq!(check(valid), Ok(()));
    let altered_under_enclosure = Range {
        lo: d(0, 0),
        hi: d(1, 1),
    };
    assert_eq!(
        check(Certificate {
            claimed_difference: altered_under_enclosure,
            ..valid
        }),
        Err(CertificateError::UnderEnclosingClaim)
    );
    let altered_lower_endpoint = Range {
        lo: d(1, 2),
        hi: d(3, 2),
    };
    assert_eq!(
        check(Certificate {
            claimed_difference: altered_lower_endpoint,
            ..valid
        }),
        Err(CertificateError::UnderEnclosingClaim)
    );

    // The contract asks for an enclosure, so a wider valid claim is accepted.
    let wider_enclosure = Range {
        lo: d(-1, 0),
        hi: d(1, 0),
    };
    assert_eq!(
        check(Certificate {
            claimed_difference: wider_enclosure,
            ..valid
        }),
        Ok(())
    );
}
