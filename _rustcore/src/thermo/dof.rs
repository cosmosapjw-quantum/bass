//! B1 · 유효 자유도 g_*(T), g_*s(T) — Python `thermo.dof` 와 동일한 로그-선형 보간.
//!
//! 표는 `dof_table.rs` (자동생성, Python 이 단일 진리원).  경계 밖은 상수 외삽
//! (numpy `np.interp` 의 left/right 규약과 일치).

use crate::thermo::dof_table as tbl;

#[inline]
fn interp(log10_t: f64, ys: &[f64; tbl::N]) -> f64 {
    let xs = &tbl::LOG10_T;
    if log10_t <= xs[0] {
        return ys[0];
    }
    if log10_t >= xs[tbl::N - 1] {
        return ys[tbl::N - 1];
    }
    // 이분탐색 후 선형보간
    let mut lo = 0usize;
    let mut hi = tbl::N - 1;
    while hi - lo > 1 {
        let mid = (lo + hi) / 2;
        if xs[mid] <= log10_t {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    let t = (log10_t - xs[lo]) / (xs[hi] - xs[lo]);
    ys[lo] + t * (ys[hi] - ys[lo])
}

/// 에너지밀도 유효자유도 g_*(T[GeV]).
pub fn g_star(t_gev: f64) -> f64 {
    interp(t_gev.log10(), &tbl::G_STAR)
}

/// 엔트로피 유효자유도 g_*s(T[GeV]).
pub fn g_star_s(t_gev: f64) -> f64 {
    interp(t_gev.log10(), &tbl::G_STAR_S)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn asymptotes() {
        assert!((g_star(1e4) - 106.75).abs() < 1e-9); // 10 TeV
        assert!((g_star(1e-5) - 3.36).abs() < 1e-9); // 10 keV
        assert!((g_star_s(1e-5) - 3.91).abs() < 1e-9);
    }

    #[test]
    fn qcd_region_values() {
        // A1 에서 고친 구간 — 구표는 1 GeV 에서 106.75 였다 (참 76.34)
        assert!((g_star(1.0) - 76.34).abs() < 1e-9);
        assert!((g_star(0.1) - 18.00).abs() < 1e-9);
    }

    #[test]
    fn monotone_decreasing_with_cooling() {
        let ts = [1e4, 1e2, 10.0, 1.0, 0.3, 0.15, 0.01, 1e-4];
        for w in ts.windows(2) {
            assert!(g_star(w[0]) >= g_star(w[1]), "{:?}", w);
        }
    }
}
