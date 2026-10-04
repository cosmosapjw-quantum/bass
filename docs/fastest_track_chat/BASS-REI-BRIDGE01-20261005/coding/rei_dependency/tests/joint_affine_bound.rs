use rei_microphysics::{
    below_strict_error_limit, joint_affine_difference, AffineEnclosure, ClosedInterval, JointParent,
};

fn interval(lower: f64, upper: f64) -> ClosedInterval {
    ClosedInterval::new(lower, upper).unwrap()
}

fn image<'a>(id: &'a str, offset: f64, coefficients: &'a [f64]) -> AffineEnclosure<'a> {
    AffineEnclosure {
        parent_id: id,
        offset,
        coefficients,
        remainder: interval(0.0, 0.0),
    }
}

#[test]
fn shared_parent_cancels_identical_affine_paths_despite_wide_separate_boxes() {
    // H(x)=x/2+1/4 and F(x)=x/4+3/8. H(H(x)) and F(x) have the
    // same output box [3/8,5/8], whose cross-box extreme distance is 1/4.
    let deviations = [interval(0.0, 1.0)];
    let parent = JointParent {
        coordinate_id: "original-x",
        deviations: &deviations,
    };
    let full_coefficients = [0.25];
    let half_coefficients = [0.25];
    let full = image("original-x", 0.375, &full_coefficients);
    let two_half = image("original-x", 0.375, &half_coefficients);
    let difference = joint_affine_difference(parent, full, two_half).unwrap();
    assert_eq!(difference, interval(0.0, 0.0));
    assert_eq!(0.625 - 0.375, 0.25);
    assert!(below_strict_error_limit(difference, 2e-4).unwrap());
}

#[test]
fn strict_failure_preserves_absence_of_candidate_state() {
    // F(x)=x, H(x)=x/2, hence F(x)-H(H(x))=3x/4 on [0,1].
    let deviations = [interval(0.0, 1.0)];
    let parent = JointParent {
        coordinate_id: "original-x",
        deviations: &deviations,
    };
    let full_coefficients = [1.0];
    let half_coefficients = [0.25];
    let full = image("original-x", 0.0, &full_coefficients);
    let two_half = image("original-x", 0.0, &half_coefficients);
    let difference = joint_affine_difference(parent, full, two_half).unwrap();
    assert!(difference.contains(0.0));
    assert!(difference.contains(0.75));
    let mut candidate_state = None;
    if below_strict_error_limit(difference, 0.5).unwrap() {
        candidate_state = Some(());
    }
    assert_eq!(candidate_state, None);
}

#[test]
fn multiple_coordinates_cancel_before_parent_width_is_applied() {
    let deviations = [interval(-1.0, 1.0), interval(0.0, 2.0)];
    let parent = JointParent {
        coordinate_id: "two-site-parent",
        deviations: &deviations,
    };
    let full_coefficients = [2.0, -1.0];
    let half_coefficients = [2.0, -1.0];
    let full = image("two-site-parent", 0.5, &full_coefficients);
    let two_half = image("two-site-parent", 0.5, &half_coefficients);
    assert_eq!(
        joint_affine_difference(parent, full, two_half).unwrap(),
        interval(0.0, 0.0)
    );
    let changed_coefficients = [1.5, -1.0];
    let changed_half = image("two-site-parent", 0.5, &changed_coefficients);
    let difference = joint_affine_difference(parent, full, changed_half).unwrap();
    assert!(difference.contains(-0.5));
    assert!(difference.contains(0.5));
}

#[test]
fn dyadic_grid_reference_stays_inside_rounded_joint_bound() {
    let deviations = [interval(-1.0, 1.0), interval(-1.0, 1.0)];
    let parent = JointParent {
        coordinate_id: "dyadic-grid",
        deviations: &deviations,
    };
    let full_coefficients = [0.25, -0.5];
    let half_coefficients = [0.5, -0.25];
    let full = image("dyadic-grid", 0.375, &full_coefficients);
    let two_half = image("dyadic-grid", 0.125, &half_coefficients);
    let bound = joint_affine_difference(parent, full, two_half).unwrap();
    // Every arithmetic operation below is exact for this small dyadic grid.
    for x in [-1.0, -0.5, 0.0, 0.5, 1.0] {
        for y in [-1.0, -0.5, 0.0, 0.5, 1.0] {
            let expected = (0.375 + 0.25 * x - 0.5 * y) - (0.125 + 0.5 * x - 0.25 * y);
            assert!(bound.contains(expected), "x={x}, y={y}, bound={bound:?}");
        }
    }
}

#[test]
fn tiny_nonzero_product_remains_enclosed_when_binary64_underflows() {
    let deviations = [interval(f64::from_bits(1), f64::from_bits(1))];
    let parent = JointParent {
        coordinate_id: "subnormal",
        deviations: &deviations,
    };
    let full_coefficients = [f64::MIN_POSITIVE];
    let half_coefficients = [0.0];
    let bound = joint_affine_difference(
        parent,
        image("subnormal", 0.0, &full_coefficients),
        image("subnormal", 0.0, &half_coefficients),
    )
    .unwrap();
    assert!(bound.lower <= 0.0);
    assert!(bound.upper > 0.0);
}

#[test]
fn independently_bounded_remainders_are_not_cancelled() {
    let deviations = [interval(-1.0, 1.0)];
    let parent = JointParent {
        coordinate_id: "original-x",
        deviations: &deviations,
    };
    let coefficients = [1.0];
    let full = AffineEnclosure {
        remainder: interval(-0.125, 0.25),
        ..image("original-x", 0.0, &coefficients)
    };
    let two_half = AffineEnclosure {
        remainder: interval(-0.25, 0.125),
        ..image("original-x", 0.0, &coefficients)
    };
    let difference = joint_affine_difference(parent, full, two_half).unwrap();
    assert!(difference.contains(-0.25));
    assert!(difference.contains(0.5));
    assert!(!below_strict_error_limit(difference, 0.25).unwrap());
}

#[test]
fn rejects_invalid_identity_shape_domains_and_overflow() {
    let deviations = [interval(0.0, 1.0)];
    let parent = JointParent {
        coordinate_id: "original-x",
        deviations: &deviations,
    };
    let coefficients = [1.0];
    let full = image("original-x", 0.0, &coefficients);
    let other = image("independent-x", 0.0, &coefficients);
    assert_eq!(
        joint_affine_difference(parent, full, other)
            .unwrap_err()
            .code(),
        "JOINT_PARENT_ID_MISMATCH"
    );

    let empty: [ClosedInterval; 0] = [];
    let empty_parent = JointParent {
        coordinate_id: "original-x",
        deviations: &empty,
    };
    assert_eq!(
        joint_affine_difference(empty_parent, full, full)
            .unwrap_err()
            .code(),
        "JOINT_PARENT_DIMENSION_MISMATCH"
    );
    let two_coefficients = [1.0, 1.0];
    assert_eq!(
        joint_affine_difference(parent, full, image("original-x", 0.0, &two_coefficients))
            .unwrap_err()
            .code(),
        "JOINT_PARENT_DIMENSION_MISMATCH"
    );
    assert_eq!(
        ClosedInterval::new(1.0, 0.0).unwrap_err().code(),
        "JOINT_INTERVAL_REVERSED"
    );
    assert_eq!(
        ClosedInterval::new(f64::NAN, 0.0).unwrap_err().code(),
        "JOINT_INTERVAL_NONFINITE"
    );
    assert_eq!(
        joint_affine_difference(
            JointParent {
                deviations: &[ClosedInterval {
                    lower: f64::NEG_INFINITY,
                    upper: 1.0
                }],
                ..parent
            },
            full,
            full
        )
        .unwrap_err()
        .code(),
        "JOINT_INTERVAL_NONFINITE"
    );
    assert_eq!(
        joint_affine_difference(parent, image("original-x", f64::NAN, &coefficients), full)
            .unwrap_err()
            .code(),
        "JOINT_INTERVAL_NONFINITE"
    );
    assert_eq!(
        joint_affine_difference(
            parent,
            image("original-x", f64::MAX, &coefficients),
            image("original-x", -f64::MAX, &coefficients)
        )
        .unwrap_err()
        .code(),
        "JOINT_ARITHMETIC_OVERFLOW"
    );
    assert_eq!(
        below_strict_error_limit(interval(0.0, 0.0), f64::NAN)
            .unwrap_err()
            .code(),
        "JOINT_ERROR_LIMIT_INVALID"
    );
}
