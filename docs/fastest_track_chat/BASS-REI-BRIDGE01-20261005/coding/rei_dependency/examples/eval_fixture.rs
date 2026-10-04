//! Bounded whitespace protocol frontend. Calls the library, never an oracle.
use rei_microphysics::*;
use std::io::{self, BufRead};

struct Tokens<'a>(std::str::SplitWhitespace<'a>);
impl<'a> Tokens<'a> {
    fn text(&mut self) -> Result<&'a str, ForwardError> {
        self.0.next().ok_or(ForwardError::InvalidInput("BAD_SHAPE"))
    }
    fn number(&mut self) -> Result<f64, ForwardError> {
        match self.text()? {
            "NaN" => Ok(f64::NAN),
            "Inf" => Ok(f64::INFINITY),
            "-Inf" => Ok(f64::NEG_INFINITY),
            s => s
                .parse()
                .map_err(|_| ForwardError::InvalidInput("BAD_FLOAT")),
        }
    }
    fn count(&mut self) -> Result<usize, ForwardError> {
        let n: usize = self
            .text()?
            .parse()
            .map_err(|_| ForwardError::InvalidInput("BAD_SHAPE"))?;
        if n > 65536 {
            return Err(ForwardError::InvalidInput("BAD_SHAPE"));
        }
        Ok(n)
    }
    fn vector(&mut self, n: usize) -> Result<Vec<f64>, ForwardError> {
        (0..n).map(|_| self.number()).collect()
    }
    fn array<const N: usize>(&mut self) -> Result<[f64; N], ForwardError> {
        self.vector(N)?
            .try_into()
            .map_err(|_| ForwardError::InvalidInput("BAD_SHAPE"))
    }
    fn table(&mut self) -> Result<PchipTable, ForwardError> {
        let n = self.count()?;
        if n < 2 {
            return Err(ForwardError::InvalidInput("BAD_TABLE"));
        }
        let knots = self.vector(n)?;
        let c = [
            self.vector(n - 1)?,
            self.vector(n - 1)?,
            self.vector(n - 1)?,
            self.vector(n - 1)?,
        ];
        PchipTable::new(knots, c)
    }
    fn end(&mut self) -> Result<(), ForwardError> {
        if self.0.next().is_some() {
            Err(ForwardError::InvalidInput("BAD_SHAPE"))
        } else {
            Ok(())
        }
    }
}
fn evaluate(op: &str, t: &mut Tokens<'_>) -> Result<Vec<f64>, ForwardError> {
    match op {
        "mass" | "signed" => {
            let v = t.number()?;
            let n = t.count()?;
            let prior = t.vector(n)?;
            t.end()?;
            if op == "mass" {
                positive_mass_projection(&prior, v)
            } else {
                let s = signed_transfer_lift(v, &prior)?;
                Ok([s.positive, s.negative, s.signed].concat())
            }
        }
        "transform" => {
            let z = t.array::<9>()?;
            t.end()?;
            let s = transform_z_to_y(&z);
            let mut out = s.n_comoving_per_cmpc3.to_vec();
            out.push(s.x_hii);
            out.extend(s.helium);
            out.extend([s.u_erg_per_cm3, s.gamma_hi_per_s]);
            Ok(out)
        }
        "pchip" => {
            let x = t.number()?;
            let table = t.table()?;
            t.end()?;
            Ok(vec![pchip_eval(&table, x)?])
        }
        "gamma" | "opacity" | "photons" => {
            let s = State {
                n_comoving_per_cmpc3: t.array()?,
                x_hii: t.number()?,
                helium: t.array()?,
                u_erg_per_cm3: t.number()?,
                gamma_hi_per_s: t.number()?,
            };
            let z = t.number()?;
            let nh = t.number()?;
            let nhe = t.number()?;
            let h = t.number()?;
            let hi = t.array()?;
            let hei = t.array()?;
            let heii = t.array()?;
            let red = t.array()?;
            let fraction = t.array()?;
            let emission = t.array()?;
            let tables = [t.table()?, t.table()?];
            t.end()?;
            let p = GroupParams {
                redshift: z,
                n_h_proper_per_cm3: nh,
                n_he_proper_per_cm3: nhe,
                hubble_per_s: h,
                sigma_hi_cm2: hi,
                sigma_hei_cm2: hei,
                sigma_heii_cm2: heii,
                redshift_coeff: red,
                source_fraction: fraction,
                lowgroup_log_opacity: tables,
            };
            if op == "gamma" {
                let g = gamma_species(&s, &p);
                let mut out = vec![g.hi_per_s, g.hei_per_s, g.heii_per_s];
                out.extend(g.group_hi_per_s);
                Ok(out)
            } else if op == "opacity" {
                Ok(opacity_cMpc_inv(&s, &p)?.to_vec())
            } else {
                Ok(photon_rates(&s, &emission, &p)?.to_vec())
            }
        }
        _ => Err(ForwardError::InvalidInput("BAD_OPERATION")),
    }
}
fn token(v: f64) -> String {
    if v.is_nan() {
        "NaN".into()
    } else if v == f64::INFINITY {
        "Inf".into()
    } else if v == f64::NEG_INFINITY {
        "-Inf".into()
    } else {
        format!("{v:.17e}")
    }
}
/// Convert one complete input record to one reply. A malformed record must
/// not discard the replies of later records. Blank lines remain ignorable.
fn response_line(line: &str) -> Option<String> {
    let mut t = Tokens(line.split_whitespace());
    let id = t.0.next()?;
    let result = match t.text() {
        Ok(op) => evaluate(op, &mut t),
        Err(error) => Err(error),
    };
    Some(match result {
        Ok(values) => format!(
            "{} OK {}{}",
            id,
            values.len(),
            values
                .iter()
                .map(|v| format!(" {}", token(*v)))
                .collect::<String>()
        ),
        Err(error) => format!("{} ERR {}", id, error.code()),
    })
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    for line in io::stdin().lock().lines() {
        if let Some(reply) = response_line(&line?) {
            println!("{reply}");
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::response_line;

    #[test]
    fn blank_input_produces_no_record() {
        assert_eq!(response_line(" \t "), None);
    }

    #[test]
    fn missing_operation_is_a_per_record_error() {
        assert_eq!(
            response_line("missing"),
            Some("missing ERR BAD_SHAPE".into())
        );
    }

    #[test]
    fn malformed_record_does_not_consume_the_next_record() {
        let input = "bad\nok mass 8 2 1 3\n";
        let output: Vec<_> = input.lines().filter_map(response_line).collect();
        assert_eq!(output.len(), 2);
        assert_eq!(output[0], "bad ERR BAD_SHAPE");
        let tokens: Vec<_> = output[1].split_whitespace().collect();
        assert_eq!(&tokens[..3], &["ok", "OK", "2"]);
        assert_eq!(tokens[3].parse::<f64>().unwrap(), 2.0);
        assert_eq!(tokens[4].parse::<f64>().unwrap(), 6.0);
    }

    #[test]
    fn malformed_payload_and_trailing_tokens_are_rejected() {
        for line in ["x mass 0 2 1", "x transform 0", "x mass 0 0 extra"] {
            assert_eq!(response_line(line), Some("x ERR BAD_SHAPE".into()));
        }
        assert_eq!(response_line("x badop"), Some("x ERR BAD_OPERATION".into()));
    }

    #[test]
    fn nonfinite_tokens_reach_the_library_error_branch() {
        assert_eq!(
            response_line("x mass 0 1 NaN"),
            Some("x ERR PRIOR_NOT_FINITE".into())
        );
        assert_eq!(
            response_line("x signed Inf 1 1"),
            Some("x ERR NONFINITE_RATE".into())
        );
    }
}
