//! Fresh, fixed-initial-geometry H/He component trial; no checkpoint or geometry evolution.
use rei_microphysics::axbi_covariant_transport::PhotonState;
use rei_microphysics::axbi_driver::{Driver, DriverConfig, DriverState};
use rei_microphysics::axbi_background::BackgroundPoint;
use std::error::Error;
use std::{collections::BTreeMap, env, fs, path::Path, process::Command};

const NEWTON_TOLERANCE: f64 = 1e-11;
const ABSORPTION_NUMBER_TOLERANCE: f64 = 1e-10;
const VALIDATION_TOLERANCE: f64 = 1e-8;

fn check(condition: bool, message: &'static str) -> Result<(), Box<dyn Error>> {
    if condition { Ok(()) } else { Err(message.into()) }
}

fn photons(state: &DriverState) -> PhotonState {
    PhotonState {
        number: state.photons.clone(),
        energy_ref: state.photon_energy_ref.clone(),
        support_lo: state.photon_support_lo.clone(),
        support_hi: state.photon_support_hi.clone(),
    }
}

fn read_input(path: &Path) -> Result<(BackgroundPoint, f64, String, String, String), Box<dyn Error>> {
    let contents = fs::read_to_string(path)?;
    let mut fields = BTreeMap::new();
    for line in contents.lines() {
        let (key, value) = line.split_once('=').ok_or("INPUT_FORMAT")?;
        check(fields.insert(key, value).is_none(), "DUPLICATE_INPUT_FIELD")?;
    }
    let get = |key: &str| -> Result<&str, Box<dyn Error>> {
        Ok(*fields.get(key).ok_or("MISSING_INPUT_FIELD")?)
    };
    check(fields.len() == 13, "INPUT_FIELD_COUNT")?;
    check(get("schema")? == "bass.rei.pr165.hhe_component_input.v1", "INPUT_SCHEMA")?;
    check(get("case")? == "COLD_FLRW", "INPUT_CASE")?;
    let source_sha = get("source_csv_sha256")?.to_owned();
    let receipt_sha = get("source_receipt_sha256")?.to_owned();
    check(source_sha == "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133", "SOURCE_SHA")?;
    check(receipt_sha == "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed", "RECEIPT_SHA")?;
    let number = |key: &str| -> Result<f64, Box<dyn Error>> {
        let value = get(key)?.parse::<f64>()?;
        check(value.is_finite(), "NONFINITE_INPUT")?;
        Ok(value)
    };
    check(number("clock_delta_ln_a")? == 1e-4, "CLOCK_INTERVAL")?;
    let point = BackgroundPoint {
        a: number("initial_a")?, b: number("initial_b")?,
        time_s: number("initial_time_s")?,
        h_flrw_per_s: number("initial_h_flrw_per_s")?,
        h_per_s: number("initial_h_per_s")?,
        s_per_s: number("initial_s_per_s")?,
        sigma: number("initial_sigma_signed")?,
    };
    let dt = number("proper_dt_s")?;
    check(point.a == 1.0 / 21.0 && point.b == 0.0 && point.time_s == 0.0,
        "INITIAL_POINT")?;
    check(dt > 0.0 && point.h_per_s > 0.0 && point.sigma == point.s_per_s / point.h_per_s,
        "GEOMETRY_OR_CLOCK_DOMAIN")?;
    let digest = Command::new("sha256sum").arg(path).output()?;
    check(digest.status.success(), "INPUT_HASH_COMMAND")?;
    let digest = String::from_utf8(digest.stdout)?;
    let input_sha = digest.split_whitespace().next().ok_or("INPUT_HASH_OUTPUT")?.to_owned();
    Ok((point, dt, source_sha, receipt_sha, input_sha))
}

fn run() -> Result<(), Box<dyn Error>> {
    let input_path = env::args().nth(1).ok_or("USAGE_COMPONENT_INPUT_PATH")?;
    check(env::args().len() == 2, "USAGE_COMPONENT_INPUT_PATH")?;
    let (initial, dt, source_sha, receipt_sha, input_sha) = read_input(Path::new(&input_path))?;
    let (driver, mut state) = Driver::new(DriverConfig::baseline())?;
    let initial_a = 1.0 / 21.0;
    check(state.a == initial_a, "INITIAL_SCALE_MISMATCH")?;
    let geometry = initial.geometry()?;

    let mut injected = photons(&state);
    let source = driver.transport.inject(&mut injected, &geometry, 20.0, dt)?;
    state.photons = injected.number;
    state.photon_energy_ref = injected.energy_ref;
    state.photon_support_lo = injected.support_lo;
    state.photon_support_hi = injected.support_hi;
    state.ledgers.source_n += source.added_photons_per_h;
    state.ledgers.source_u += source.added_energy_ev_per_h;

    let mut rhs_evaluations = 0;
    driver.chemical_stage(&mut state, dt, &mut rhs_evaluations)?;
    check(state.a == initial_a, "GEOMETRY_WAS_ADVANCED")?;
    check(state.max_newton_residual.is_finite()
        && state.max_newton_residual <= NEWTON_TOLERANCE, "NEWTON_RESIDUAL")?;
    let (photon_n, photon_u) = driver.photon_inventory(&state);
    let absorption_number_residual =
        state.ledgers.source_n - photon_n - state.ledgers.absorbed_n;
    check(absorption_number_residual.is_finite()
        && absorption_number_residual.abs()
            <= ABSORPTION_NUMBER_TOLERANCE * state.ledgers.source_n.max(1.0),
        "ABSORPTION_NUMBER_RESIDUAL")?;
    driver.validate(&state, VALIDATION_TOLERANCE)?;
    let eos = state.gas.eos(
        driver.n_h0_cm3 / state.a.powi(3),
        driver.n_he0_cm3 / state.a.powi(3),
    )?;
    check(eos.temperature_k.is_finite() && eos.temperature_k > 0.0,
        "TEMPERATURE_DOMAIN")?;
    check(state.gas.fractions.iter().all(|x| x.is_finite() && *x >= 0.0),
        "HHE_FRACTION_DOMAIN")?;
    check(state.photons.iter().all(|n| n.is_finite() && *n >= 0.0),
        "PHOTON_NUMBER_DOMAIN")?;
    let (number_residual, energy_residual) = driver.residuals(&state)?;
    println!("{{\"status\":\"COMPONENT_PASS\",\"scope\":\"fixed_initial_geometry_same_event_HHe\",\"source_csv_sha256\":\"{source_sha}\",\"source_receipt_sha256\":\"{receipt_sha}\",\"geometry_input_sha256\":\"{input_sha}\",\"a\":{:.17e},\"b\":{:.17e},\"source_zbar\":20,\"clock_delta_ln_a\":1e-4,\"proper_dt_s\":{:.17e},\"rhs_evaluations\":{},\"max_newton_residual\":{:.17e},\"gas_fractions\":{:?},\"temperature_k\":{:.17e},\"photon_number_per_h\":{:.17e},\"photon_energy_ev_per_h\":{:.17e},\"source_n\":{:.17e},\"source_u\":{:.17e},\"absorbed_n\":{:.17e},\"photo_events\":{:?},\"rr_events\":{:?},\"ci_events\":{:?},\"ci_floor_events\":{:?},\"dr_events\":{:.17e},\"escaped_u\":{:.17e},\"cmb_input\":{:.17e},\"thermal_work\":{:.17e},\"photon_work\":{:.17e},\"absorption_number_residual\":{:.17e},\"number_residual\":{:.17e},\"energy_residual\":{:.17e}}}",
        state.a, initial.b, dt, rhs_evaluations,
        state.max_newton_residual, state.gas.fractions, eos.temperature_k,
        photon_n, photon_u, state.ledgers.source_n, state.ledgers.source_u,
        state.ledgers.absorbed_n, state.ledgers.photo_events,
        state.ledgers.rr_events, state.ledgers.ci_events,
        state.ledgers.ci_floor_events, state.ledgers.dr_events,
        state.ledgers.escaped_u, state.ledgers.cmb_input,
        state.ledgers.thermal_work, state.ledgers.photon_work,
        absorption_number_residual, number_residual, energy_residual);
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> { run() }
