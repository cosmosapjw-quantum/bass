//! I3 · 결합 루프 전면화 (69차) — I1d `coupled_tilted.coupled_rhs` 의 항별 미러
//! + RK4 루프.  R5b 교훈: 루프째로 (FFI 왕복 제거).  블록표는 J3 상수 재사용;
//!
//! U-기저 (l=1: 3×3, l=2: 9×5) 는 **Python U_basis 를 호출 인자로 캐리**
//! (좌표-동일 — 재유도 0).
//!
//! 상태: [Σ5(5), N3(3), lnH, {(Ω_c, v_c3)}_{c<nc}, J(l=0..l_max)] — i=0 층,
//! 무질량 별칭·단순절단.  운동 계층 = coeff_hier::rhs_grid + N-항 (67차 정정:
//! α_up=(l+1)/(2l+3)·ov, α_dn=1·cv) + 회전항 (68차 핀 sign=−1).
//!
//! 게이트: Python 두-경로 차등 (tests/test_i3_rust_coupled.py).  비트-정확
//! 주장 안 함 (R5b 합 순서 경계).

use super::coeff_hier as ch;

const GUARD_EPS: f64 = 1e-12;
const SQ3: f64 = 1.7320508075688772;
const CART_TO_CANON: [usize; 3] = [2, 0, 1];

fn safe(x: f64) -> f64 {
    if x.abs() < GUARD_EPS {
        if x >= 0.0 {
            GUARD_EPS
        } else {
            -GUARD_EPS
        }
    } else {
        x
    }
}

fn shear_matrix(s5: &[f64]) -> [[f64; 3]; 3] {
    let (sp, sm) = (s5[0], s5[1]);
    [
        [-2.0 * sp, SQ3 * s5[2], SQ3 * s5[3]],
        [SQ3 * s5[2], sp + SQ3 * sm, SQ3 * s5[4]],
        [SQ3 * s5[3], SQ3 * s5[4], sp - SQ3 * sm],
    ]
}

fn alpha_up(l: usize) -> f64 {
    (l as f64 + 1.0) / (2.0 * l as f64 + 3.0)
}

fn nterm_add(y: &mut [f64], l: usize, n3: &[f64], j_lm1: Option<&[f64]>, j_lp1: Option<&[f64]>) {
    for d in 0..3 {
        if n3[d] == 0.0 {
            continue;
        }
        let s = CART_TO_CANON[d];
        let mut e_cart = [0.0; 3];
        e_cart[d] = 1.0;
        let mut e_can = [0.0; 3];
        e_can[s] = 1.0;
        if l >= 2 {
            if let Some(jm) = j_lm1 {
                let lin = l - 1;
                let mut t = ch::apply("rot", lin, jm, &e_cart);
                for v in t.iter_mut() {
                    *v *= lin as f64;
                }
                let m = ch::apply("ov", l, &t, &e_can);
                let a = alpha_up(lin);
                for (yy, mm) in y.iter_mut().zip(m) {
                    *yy -= n3[d] * a * mm;
                }
            }
        }
        if let Some(jp) = j_lp1 {
            let lin = l + 1;
            let mut t = ch::apply("rot", lin, jp, &e_cart);
            for v in t.iter_mut() {
                *v *= lin as f64;
            }
            let m = ch::apply("cv", l, &t, &e_can);
            for (yy, mm) in y.iter_mut().zip(m) {
                *yy -= n3[d] * mm;
            }
        }
    }
}

fn rot_add(y: &mut [f64], l: usize, r: &[f64; 3], j: &[f64]) {
    if l == 0 {
        return;
    }
    let m = ch::apply("rot", l, j, r);
    for (yy, mm) in y.iter_mut().zip(m) {
        *yy -= l as f64 * mm;
    }
}

pub struct Layout {
    pub nc: usize,
    pub l_max: usize,
}

impl Layout {
    pub fn j_off(&self) -> usize {
        9 + 4 * self.nc
    }
    pub fn j_len(&self) -> usize {
        (0..=self.l_max).map(|l| 2 * l + 1).sum()
    }
    pub fn total(&self) -> usize {
        self.j_off() + self.j_len()
    }
    pub fn j_slice<'a>(&self, y: &'a [f64], l: usize) -> &'a [f64] {
        let mut o = self.j_off();
        for lp in 0..l {
            o += 2 * lp + 1;
        }
        &y[o..o + 2 * l + 1]
    }
}

/// u1: (3·3) row-major [a·3+m] — from_ccoef(l=1); u2: (9·5) [pq·5+m].
/// s5(σ) = to_ccoef: s5[m] = Σ_pq u2[pq·5+m]·S[pq]  (U 직교정규).
#[allow(clippy::too_many_arguments)]
pub fn coupled_rhs(
    y: &[f64],
    gammas: &[f64],
    kappa: Option<&[f64]>,
    l_max: usize,
    nterm_on: bool,
    u1: &[f64],
    u2: &[f64],
    sigma_signs: &[f64; 3],
    nu_bgk: f64,
) -> Vec<f64> {
    let nc = gammas.len();
    let lay = Layout { nc, l_max };
    let s5 = &y[0..5];
    let n3 = &y[5..8];
    let lnh = y[8];
    let s = shear_matrix(s5);
    let sigma2: f64 = s5.iter().map(|v| v * v).sum();
    let h2 = (2.0 * lnh).exp();
    // 운동 소스
    let j0 = lay.j_slice(y, 0)[0];
    let om_k = j0 / (3.0 * h2);
    let mut pik = [[0.0f64; 3]; 3];
    if l_max >= 2 {
        let c2 = lay.j_slice(y, 2);
        for p in 0..3 {
            for q in 0..3 {
                let mut acc = 0.0;
                for m in 0..5 {
                    acc += u2[(p * 3 + q) * 5 + m] * c2[m];
                }
                pik[p][q] = acc / h2;
            }
        }
    }
    // 유체 소스 + q
    let mut q = 2.0 * sigma2 + om_k;
    let mut pi_tot = pik;
    let mut om = vec![0.0; nc];
    let mut vv = vec![[0.0f64; 3]; nc];
    let mut v2 = vec![0.0; nc];
    let mut gp = vec![0.0; nc];
    let mut gm = vec![0.0; nc];
    let mut sv2 = vec![0.0; nc];
    for c in 0..nc {
        let o = 9 + 4 * c;
        om[c] = y[o];
        vv[c] = [y[o + 1], y[o + 2], y[o + 3]];
        v2[c] = vv[c].iter().map(|x| x * x).sum();
        gp[c] = safe(1.0 + (gammas[c] - 1.0) * v2[c]);
        gm[c] = safe(1.0 - (gammas[c] - 1.0) * v2[c]);
        let mut acc = 0.0;
        for a in 0..3 {
            for b in 0..3 {
                acc += s[a][b] * vv[c][a] * vv[c][b];
            }
        }
        sv2[c] = acc;
        q += 0.5 * ((3.0 * gammas[c] - 2.0) + (2.0 - gammas[c]) * v2[c]) * om[c] / gp[c];
        let cpi = 3.0 * gammas[c] * om[c] / gp[c];
        for a in 0..3 {
            for b in 0..3 {
                pi_tot[a][b] +=
                    cpi * (vv[c][a] * vv[c][b] - if a == b { v2[c] / 3.0 } else { 0.0 });
            }
        }
    }
    // 게이지 W (n-대각 유지 — F3/H'1 공식)
    let w12 = SQ3 * s5[2] * (n3[0] + n3[1]) / safe(n3[0] - n3[1]);
    let w13 = SQ3 * s5[3] * (n3[0] + n3[2]) / safe(n3[0] - n3[2]);
    let w23 = SQ3 * s5[4] * (n3[1] + n3[2]) / safe(n3[1] - n3[2]);
    let w = [[0.0, w12, w13], [-w12, 0.0, w23], [-w13, -w23, 0.0]];
    let r_cart = [-w23, w13, -w12];
    // dΣ = −(2−q)S − ³S + Π + [W,S] − tr/3 (G.rhs 미러)
    let tn: f64 = n3.iter().sum();
    let mut b = [0.0; 3];
    for i in 0..3 {
        b[i] = 2.0 * n3[i] * n3[i] - tn * n3[i];
    }
    let bm = (b[0] + b[1] + b[2]) / 3.0;
    let mut ds = [[0.0f64; 3]; 3];
    for a in 0..3 {
        for bb in 0..3 {
            let s3 = if a == bb { b[a] - bm } else { 0.0 };
            let mut comm = 0.0;
            for k in 0..3 {
                comm += w[a][k] * s[k][bb] - s[a][k] * w[k][bb];
            }
            ds[a][bb] = -(2.0 - q) * s[a][bb] - s3 + pi_tot[a][bb] + comm;
        }
    }
    let tr = (ds[0][0] + ds[1][1] + ds[2][2]) / 3.0;
    for (a, row) in ds.iter_mut().enumerate() {
        row[a] -= tr;
    }
    let ds5 = [
        -ds[0][0] / 2.0,
        (ds[1][1] - ds[2][2]) / (2.0 * SQ3),
        ds[0][1] / SQ3,
        ds[0][2] / SQ3,
        ds[1][2] / SQ3,
    ];
    let sig_d = [-2.0 * s5[0], s5[0] + SQ3 * s5[1], s5[0] - SQ3 * s5[1]];
    let dn3 = [
        (q + 2.0 * sig_d[0]) * n3[0],
        (q + 2.0 * sig_d[1]) * n3[1],
        (q + 2.0 * sig_d[2]) * n3[2],
    ];
    let dlnh = -(1.0 + q);
    // 유체 진화 (+κ)
    let mut dom = vec![0.0; nc];
    let mut dv = vec![[0.0f64; 3]; nc];
    for c in 0..nc {
        let g = gammas[c];
        dom[c] = (om[c] / gp[c])
            * (2.0 * q - (3.0 * g - 2.0) + (2.0 * q * (g - 1.0) - (2.0 - g)) * v2[c] - g * sv2[c]);
        let t = ((3.0 * g - 4.0) * (1.0 - v2[c]) + (2.0 - g) * sv2[c]) / gm[c];
        let nvv = [n3[0] * vv[c][0], n3[1] * vv[c][1], n3[2] * vv[c][2]];
        let p = [
            vv[c][1] * nvv[2] - vv[c][2] * nvv[1],
            vv[c][2] * nvv[0] - vv[c][0] * nvv[2],
            vv[c][0] * nvv[1] - vv[c][1] * nvv[0],
        ];
        for a in 0..3 {
            let mut sv = 0.0;
            let mut wv = 0.0;
            for bb in 0..3 {
                sv += s[a][bb] * vv[c][bb];
                wv += w[a][bb] * vv[c][bb];
            }
            dv[c][a] = t * vv[c][a] - sv + wv - p[a];
        }
    }
    if let Some(k) = kappa {
        for c in 0..nc {
            let mut rr = [0.0f64; 3];
            for d in 0..nc {
                let kcd = k[c * nc + d];
                if kcd == 0.0 {
                    continue;
                }
                let wgt = kcd * om[c] * om[d];
                for a in 0..3 {
                    rr[a] += wgt * (vv[d][a] - vv[c][a]);
                }
            }
            let vr: f64 = (0..3).map(|a| vv[c][a] * rr[a]).sum();
            let g = gammas[c];
            let coef = gp[c] / (3.0 * g * safe(om[c]));
            for a in 0..3 {
                dv[c][a] += coef * (rr[a] + 2.0 * (g - 1.0) / gm[c] * vr * vv[c][a]);
            }
        }
    }
    // 운동 계층: s5(σ), 패딩 (별칭 i·절단 l) → rhs_grid + N-항 + 회전항
    let mut s5c = [0.0f64; 5];
    for m in 0..5 {
        let mut acc = 0.0;
        for pq in 0..9 {
            acc += u2[pq * 5 + m] * s[pq / 3][pq % 3];
        }
        s5c[m] = acc;
    }
    let (l_pad, i_pad) = (l_max + 2, 2usize);
    let mut padded = vec![0.0; ch::grid_len(l_pad, i_pad)];
    {
        let mut o = 0;
        for l in 0..=l_pad {
            let n = 2 * l + 1;
            for _i in 0..=i_pad {
                if l <= l_max {
                    padded[o..o + n].copy_from_slice(lay.j_slice(y, l));
                }
                o += n;
            }
        }
    }
    let mut dj = ch::rhs_grid(&padded, l_max, 0, 1.0, &s5c, sigma_signs);
    {
        let mut o = 0;
        for l in 0..=l_max {
            let n = 2 * l + 1;
            let jm = if l >= 1 {
                Some(lay.j_slice(y, l - 1))
            } else {
                None
            };
            let jp = if l < l_max {
                Some(lay.j_slice(y, l + 1))
            } else {
                None
            };
            let yslice = &mut dj[o..o + n];
            if nterm_on {
                nterm_add(yslice, l, n3, jm, jp);
            }
            rot_add(yslice, l, &r_cart, lay.j_slice(y, l));
            // G2 사다리의 BGK-보존 (l≥2 만 완화 — 수·에너지·운동량 보존):
            //   dJ_l += −ν J_l  (PSTF 기저에서 P_{l≤1} 사영의 정확 판)
            if nu_bgk != 0.0 && l >= 2 {
                let jl = lay.j_slice(y, l);
                for (yy, jj) in yslice.iter_mut().zip(jl) {
                    *yy -= nu_bgk * jj;
                }
            }
            o += n;
        }
    }
    let _ = u1; // (q⃗ 소스는 Codazzi 감시
                //  전용 — RHS 에는 안 씀;
                //  Python monitors 몫)
                // 조립
    let mut out = vec![0.0; lay.total()];
    out[0..5].copy_from_slice(&ds5);
    out[5..8].copy_from_slice(&dn3);
    out[8] = dlnh;
    for c in 0..nc {
        let o = 9 + 4 * c;
        out[o] = dom[c];
        out[o + 1..o + 4].copy_from_slice(&dv[c]);
    }
    out[lay.j_off()..].copy_from_slice(&dj);
    out
}

#[allow(clippy::too_many_arguments)]
pub fn rk4_evolve(
    y0: &[f64],
    gammas: &[f64],
    kappa: Option<&[f64]>,
    l_max: usize,
    tau: f64,
    nsteps: usize,
    nterm_on: bool,
    keep: bool,
    u1: &[f64],
    u2: &[f64],
    sigma_signs: &[f64; 3],
    nu_bgk: f64,
) -> (Vec<f64>, Vec<f64>) {
    let mut y = y0.to_vec();
    let h = tau / nsteps as f64;
    let mut traj = Vec::new();
    if keep {
        traj.extend_from_slice(&y);
    }
    let axpy = |a: &[f64], f: f64, b: &[f64]| -> Vec<f64> {
        a.iter().zip(b).map(|(x, k)| x + f * k).collect()
    };
    for _ in 0..nsteps {
        let k1 = coupled_rhs(
            &y,
            gammas,
            kappa,
            l_max,
            nterm_on,
            u1,
            u2,
            sigma_signs,
            nu_bgk,
        );
        let k2 = coupled_rhs(
            &axpy(&y, 0.5 * h, &k1),
            gammas,
            kappa,
            l_max,
            nterm_on,
            u1,
            u2,
            sigma_signs,
            nu_bgk,
        );
        let k3 = coupled_rhs(
            &axpy(&y, 0.5 * h, &k2),
            gammas,
            kappa,
            l_max,
            nterm_on,
            u1,
            u2,
            sigma_signs,
            nu_bgk,
        );
        let k4 = coupled_rhs(
            &axpy(&y, h, &k3),
            gammas,
            kappa,
            l_max,
            nterm_on,
            u1,
            u2,
            sigma_signs,
            nu_bgk,
        );
        for i in 0..y.len() {
            y[i] += (h / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
        }
        if keep {
            traj.extend_from_slice(&y);
        }
    }
    (y, traj)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn layout_offsets() {
        let lay = Layout { nc: 2, l_max: 3 };
        assert_eq!(lay.j_off(), 17);
        assert_eq!(lay.j_len(), 16);
        assert_eq!(lay.total(), 33);
    }

    #[test]
    fn safe_guards_zero() {
        assert_eq!(safe(0.0), GUARD_EPS);
        assert_eq!(safe(-0.0), GUARD_EPS);
        assert_eq!(safe(-1e-15), -GUARD_EPS);
    }

    #[test]
    fn nterm_iso_n_cancels() {
        // 등방 N: l=2←(1,3) 조합이 연산자 수준에서 0 이 되는지는 격자합에서
        // 확인 — 여기선 rot(l=1) 스칼라 케이스 가드만 (l=0 조기반환).
        let mut y = [0.0f64; 1];
        rot_add(&mut y, 0, &[1.0, 2.0, 3.0], &[5.0]);
        assert_eq!(y[0], 0.0);
    }
}
