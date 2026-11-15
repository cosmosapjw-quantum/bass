"""Compare saved Sachs rows with a representation check for the magnitude."""

import argparse
import csv
import gzip
import json
import math
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from itertools import zip_longest
from pathlib import Path

PREFIX = "BASS_REI_F08_S0_"
ROWS = 10752
KEYS = ("window_fraction", "angular_nmu", "angular_nphi", "mu_bin", "phi_bin")
FLUX = "conditional_screened_flux_ratio_BI_over_FLRW"
MAG = "conditional_delta_magnitude_BI_minus_FLRW"
NEAR = Context(prec=80)
DOWN = Context(prec=80, rounding=ROUND_FLOOR)
UP = Context(prec=80, rounding=ROUND_CEILING)
FACTOR = Decimal("2.5")


class ReplayError(ValueError):
    pass


def ln_interval(value):
    # Decimal.ln is correctly rounded to nearest. Adjacent Decimal values
    # enclose the exact log, including at powers of the context radix.
    center = NEAR.ln(value)
    return NEAR.next_minus(center), NEAR.next_plus(center)


LN10_LO, LN10_HI = ln_interval(Decimal(10))


def magnitude_residual(flux, magnitude, label):
    if not math.isfinite(flux) or flux <= 0 or not math.isfinite(magnitude):
        raise ReplayError(f"{label}: invalid flux or magnitude")
    if (magnitude == 0) != (flux == 1):
        raise ReplayError(f"{label}: zero magnitude requires unit flux and vice versa")
    if flux == 1:
        return Decimal(0), (Decimal(0), Decimal(0))
    low, high = ln_interval(Decimal.from_float(flux))
    # The numerator reverses sign and endpoints. The denominator is positive;
    # enclose both choices to cover either numerator sign.
    nlo = DOWN.multiply(FACTOR.copy_negate(), high)
    nhi = UP.multiply(FACTOR.copy_negate(), low)
    mlo = min(DOWN.divide(nlo, d) for d in (LN10_LO, LN10_HI))
    mhi = max(UP.divide(nhi, d) for d in (LN10_LO, LN10_HI))
    stored = Decimal.from_float(magnitude)
    residual = max(UP.subtract(stored, mlo), UP.subtract(mhi, stored))
    limit = DOWN.multiply(Decimal(2), Decimal.from_float(math.ulp(magnitude)))
    if residual > limit:
        raise ReplayError(f"{label}: magnitude residual {residual} exceeds {limit}")
    return residual, (mlo, mhi)


def compare_row(old, new, index):
    if old.keys() != new.keys() or None in old or any(
        k not in old for k in (*KEYS, FLUX, MAG)
    ):
        raise ReplayError(f"row {index}: invalid or changed columns")
    values = []
    for k in old:
        if old[k] is None or new[k] is None:
            raise ReplayError(f"row {index}: missing field {k}")
        if k in KEYS:
            if old[k] != new[k]:
                raise ReplayError(f"row {index}: changed key {k}")
            if not math.isfinite(float(old[k])):
                raise ReplayError(f"row {index}: nonfinite key {k}")
            continue
        if k == MAG:
            continue
        u, v = float(old[k]), float(new[k])
        if not all(map(math.isfinite, (u, v))) or not math.isclose(
            u, v, rel_tol=2e-12, abs_tol=1e-20
        ):
            raise ReplayError(f"row {index}: primitive mismatch {k}: {u} vs {v}")
    for label, row in (("original", old), ("replay", new)):
        values.append(
            magnitude_residual(float(row[FLUX]), float(row[MAG]), f"row {index} {label}")
        )
    (r0, (lo0, hi0)), (r1, (lo1, hi1)) = values
    propagation = max(UP.subtract(hi1, lo0), UP.subtract(hi0, lo1))
    return propagation, r0, r1


def compare_identity(old, new, count):
    if not isinstance(old.get("source_pair_id"), str) or not old["source_pair_id"]:
        raise ReplayError("missing source pair identity")
    if (
        old["source_pair_id"] != new.get("source_pair_id")
        or old.get("num_physical_ray_rows") != count
        or new.get("num_physical_ray_rows") != count
    ):
        raise ReplayError("source pair identity or physical ray count differs")


def verify(results, replay):
    csv_name = PREFIX + "SOURCE_MATCHED_SACHS_OBSERVABLES.csv.gz"
    json_name = PREFIX + "MATCHED_SACHS_RESULT.json"
    maxima = [Decimal(0)] * 3
    count = 0
    with gzip.open(results / csv_name, "rt", newline="") as a, gzip.open(
        replay / csv_name, "rt", newline=""
    ) as b:
        old, new = csv.DictReader(a), csv.DictReader(b)
        if (
            not old.fieldnames
            or old.fieldnames != new.fieldnames
            or len(set(old.fieldnames)) != len(old.fieldnames)
        ):
            raise ReplayError("invalid or changed CSV header")
        for index, (x, y) in enumerate(zip_longest(old, new)):
            if x is None or y is None:
                raise ReplayError(f"row {index}: row counts differ")
            maxima = list(map(max, zip(maxima, compare_row(x, y, index))))
            count += 1
    if count != ROWS:
        raise ReplayError(f"observed {count} rows, expected {ROWS}")
    with (results / json_name).open() as a, (replay / json_name).open() as b:
        compare_identity(json.load(a), json.load(b), count)
    return dict(zip(
        ("max_primitive_propagated_magnitude", "max_original_transform_residual",
         "max_replay_transform_residual"),
        map(str, maxima),
    ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--replay", type=Path, default=Path("replay"))
    args = parser.parse_args()
    try:
        summary = verify(args.results, args.replay)
    except (OSError, ValueError, ArithmeticError) as error:
        parser.exit(1, f"Sachs replay comparison failed: {error}\n")
    print(json.dumps(summary, sort_keys=True))
    print(f"BASS_REI_S0_CLEAN_PHYSICS_REPLAY_PASS_{ROWS}")
