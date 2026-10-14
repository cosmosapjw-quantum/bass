# FA03-C5: 실제 BASS angular-cap coding loop

2026-10-15 KST. 선택 단계 **C5 (구현과 stage-local 실행)**. 이 코드는 R5–R10에서 보존된 FA03 아이디어와 동결된 R7 검출기 코드를 실제로 돌리는 **새 개발 연구**다. 역사적 `FA03 R5–R10` 연구 루프를 다시 실행하거나 REI의 원자흡수 계수를 변경하지 않는다.

## 실행 가능한 산출물
- `angular_sweep.py`: GL inclination × uniform azimuth cap 격자의 6-state ε=0 grey/opacity jet ODE를 자체 RK4로 적분하고, 정확한 finite-ε 에너지 band quadrature를 독립 검산한다. `chi=1/125`, `psi=1/100`, `delta=1/50 rad`, `x∈[1/2,1]`, `e∈[49/50,51/50]`, ε∈[-1/10,1/10], source frozen FA02/FA03 original. R7 original certificate copied exactly into `reference/`; root BASS checkout 바깥으로 옮겨도 실행 가능하다.
- `test_angular_sweep.py`: 15 focused tests with exact provenance, image-domain positivity, weight/first-second μ cap integrals, unchanged R7 original 64-step numerical coefficients, φ phase shift, source angular nontriviality, time vs angle and finite-ε photonic state, negative tests.
- `evidence/ANGULAR_STUDY_C5_FINAL.json`, `TIME_REFINEMENT.json`, RED→GREEN logs: original actual Ubuntu local execution, no fake/heavy REI solver.

## 수학적 quadrature invariant
[\mu(r)=\cos r=1-(1+t)\sin^2(\delta/2),\quad t\in[-1,1],\]
그래서 normalized solid angle 적분은 `∫dt/2∫dφ/(2π)`. (\langle\mu\rangle=(1+\cos\delta)/2), (\langle\mu^2\rangle=(1+\cos\delta+\cos^2\delta)/3)이므로 GL2 이상에서 **해당 저차 기하학적 모멘트는 이론상 정확**하다. Wolfram15.0.1에서 scalar 4개 관계(True,1,0,0) 직접 확인. **그러나 전체 비선형 편광 전파 integrand가 다항식이라는 뜻은 아니다.**

## 실제 숫자
상태 순서 `{S0,S1,S2,V0,V1,W0}`, trace-norm differences. `steps=128` 고정, cap GL2×8(16rays), GL3×12(36), GL4×16(64), GL6×24(144), GL10×48(480), GL14×64(896)의 여섯 상태 전체 차이(원36rays 대비) 최대 `6.122369811137812e-16`. `P3` 투영 source는 실제 ray 방향에 따라 변하며 `P_11` span `0.00057444` at original36. φ quadrature phase +0.37-grid-offset의 최대 여섯 상태 차이 `8.33415e-17`. Angle 조정이 source 불변이라서 얻은 것은 아니다.

Original 36ray에서 64→128 RK4 step 최대 차이 `1.0245310242545942e-11`이고, 32/64/128/256/512 step 순서의 비교된 차이 비율 `15.99667187,15.99972706,15.99967492`로 RK4 O(h⁴)와 일치한다. 원 R7 64step `reference_stokes_display`를 byte-pinned 원 소스로 재생산한 Stokes 최대 차이 `1.1102230246251565e-16`.

Finite ε energy integration(36ray, steps128, GL-energy8/16):
| epsilon | finite energy vs 2nd polynomial trace-norm | min coherency eigenvalue |
|:--:|--:|--:|
| -0.1 | 3.3306053748294318e-9 | 0.1268428401755171 |
| 0 | ~2.2283e-16 | 0.12650186895662555 |
| +0.1 | 3.3195542981090406e-9 | 0.12616274668946265 |

Higher angular energy 480ray changes those results by only ~10⁻¹⁵. Energy quadrature order8→16 trace-norm changes max `3.080868893360836e-15`. **All above are IEEE binary64 empirical comparisons**, not theorem-bound continuum cap errors. The only established rigorous combination remains R8 **fixed36ray** trace-norm bound `<4.75e-7` and PSD eigenvalue bound `>0.12548`. We do not add 36→896 difference as a rigorously bounded continuum angular remainder. Do not claim physical EoR-ionization, continuous cap, joint observer derivatives or measured opacity.

## 실행
```bash
python3 research/fa03_c5_angular_cap_20261015/angular_sweep.py --steps 128 --out /tmp/fa03_c5_new_run.json
python3 -m unittest discover -s research/fa03_c5_angular_cap_20261015 -p test_angular_sweep.py -v
```

Linux Ubuntu24.04, Python3.12.3, numpy2.4.2. Original source files exact SHA under `evidence/PROVENANCE.json`, R7 archive SHA256 `551ca3cd...`. Focused 15/15 tests pass (corrected from observed RED 1 fail +1 error). Old `tests/test_p_polarization.py` returned 22 pass / 1 fail because optional `jax` is absent in system Python; `test_m11_rays.py` was blocked at collection by the same missing JAX. This is a separate environment dependency, NOT a green full-BASS suite or an FA03 C5 failure. No installation or owner environment modification was performed.

Primary-method context: [Bestard Jaume et al. 2021, A&A, polarised angular quadrature](https://www.aanda.org/articles/aa/full_html/2021/01/aa39424-20/aa39424-20.html). This paper studies other polarized transfer models and **does not certify** the BASS numerical values. [Fleury–Pitrou–Uzan 2015, PRD 91 043511](https://doi.org/10.1103/PhysRevD.91.043511) is the Bianchi I ray background source. New FA03 code reuses the exact already-preserved (−,+,+,+) original frame and xAct R10 checks rather than silently rerunning theory.

## 다음 단계 및 REI
C5 complete-scoped, **C6 READY/NOT_RUN**, C7/C8 unadmitted. C6 should independently test roundoff and observer chart sensitivity and construct a true derivative/interval angular error bound if needed before continuum-cap publication. `bass_cr` PR65 has **its own** threshold-aware injection/moving-source counterexample and should not be copied into BASS. `rec_bianchi` PR85 independently provides a finite-clock Python background. Cold AXBI H/He chemistry stays owned by separate Codex, not imported into FA03 toy.
