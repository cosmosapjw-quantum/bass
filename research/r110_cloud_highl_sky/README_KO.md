# R110 · 비섭동 균질 Bianchi 배경에서 임의 ℓ의 결정론적 C_ℓm^XY

기준: BASS `3966f2a08`(R109). 이론 루프는 [THEORY.md](THEORY.md)(Phase 1–10, D1–D10), 수치 검산은 [THEORY_CHECKS.json](THEORY_CHECKS.json)에 있다. 기본 설정의 출력은 R109와 바이트 단위로 같다(VIIh recoil·FLRW observer의 modes/cl/diagnostics 대조).

## 코딩 루프 C1–C10

| 단계 | 개발 | 판별 결과 |
|---|---|---|
| C1 기준선 | R109 빌드·테스트 | 181개 통과, 기본 실행 시간 0.13 s |
| C2 사건 기록 | 모든 Thomson cell의 깊이·전자 β·gain map·단계별 정지계 원천 3×3 텐서와 두 node를 `StepRecord`로 저장(능동 predictor 제외) | 기본 출력 바이트 동일 |
| C3 replay | `replay`, `trace_back`, `arrival`: 같은 이산 사상을 임의 방향에 적용 | 순방향 광선 재현 상대차 **0**(bitwise), 4개 경로(BE/SDIRK2 recoil, tracer, VIII Lie coflow); 역추적 ≤1.2×10⁻¹⁵ |
| C4 고리 변환 | `analyze_rings`: GL×균일 φ에서 O(L³), R109 `analyze`와 같은 Wigner 열·E/B 부호 | 표본별 분석과 차 1.0×10⁻¹⁶(척도 0.13) |
| C5 LoS 하늘 | `los_sky` + CLI `--los-lmax/--los-ntheta/--los-nphi` → `los_modes.tsv`, `los_cl.tsv`(R109 열 구조) | 정지 FLRW ℓ≤40 \|a\|<10⁻¹⁴; 부스트 FLRW 점별 <2×10⁻¹⁴, a_ℓ0 vs 독립 Legendre 구적 <10⁻¹³; Bianchi I 닫힌형 2.09×10⁻⁵→5.21×10⁻⁶→1.30×10⁻⁶(2차) |
| C6 저ℓ 일치 | 순방향 Lagrangian 구적 vs LoS(1≤ℓ≤4) | 2.88×10⁻⁵→7.20×10⁻⁶→1.80×10⁻⁶(steps 12/24/48). 순방향 가중치(이동 입체각)의 O(Δη²) Jacobian 오차이며 LoS에는 없다 |
| C7 SDIRK2 | `--collision sdirk2`(Alexander 1977, γ=1−√2/2). ETD2는 이론 루프에서 기각 | 연속 변화비 BE≈2, SDIRK2≈4.0(VIstar recoil, VIIh τ=3, VIII tracer). 288 스텝 E 변화 2.37×10⁻⁴→1.25×10⁻⁵, 두꺼운 VIIh 1.38×10⁻³→1.02×10⁻⁵ |
| C8 Λ | `--omega-lambda`: Ω_Λ=Ω_Λ,i/h², Gauss·Raychaudhuri에만 진입 | ΛCDM FLRW h(η) 8.9×10⁻⁴→2.1×10⁻⁴→5.1×10⁻⁵(2차), Gauss 잔차도 2차 |
| C9 Lie 합동 | `--lie-update congruence`: N→PNPᵀ, A→det P·P^{−T}A, P=exp[Δη(Σ+W+qI/2)] | 14개 계열 사례 모두 유형 보존, 1/h 표류 ≤2.2×10⁻¹⁵. additive는 III·IV·VI₋₁/₉가 VI_h로 바뀜(2–5×10⁻⁷ 표류) |
| C10 아틀라스 | [run_highl_atlas.py](run_highl_atlas.py): A) R109 recoil 12계열 ℓ≤32, B) z=1100→0 HYREC x_e·Λ·recoil 장기 4계열 ℓ≤48 | 아래 |

회전 공변성: 임의 회전한 VIII Lie 자료·관측자 β에서 replay 화면 F_R(n)=R F(Rᵀn)Rᵀ의 최대 상대차 6.1×10⁻¹⁵(20×48 격자).

## 아틀라스 수치 ([RESULTS/HIGHL_ATLAS.json](RESULTS/HIGHL_ATLAS.json))

- A(η 0.35, 초기 전단 0.18, recoil, 관측자 β): 12계열 모두 유형·h 보존, LoS 도착 오차 ≤1.5×10⁻¹⁵, 18→36 스텝 T/E/B 모드 변화 ≈1×10⁻⁵ / 2–8×10⁻⁴ / 1–3×10⁻³. TT는 ℓ=2에서 5×10⁻⁴–2.8×10⁻³, ℓ≈30 부근에서 수치 바닥(≈10⁻³²)에 닿는다.
- B(z=1100→0, dust 75%, Ω_Λ,i=1.23×10⁻⁹, SDIRK2+congruence, 700/1400 스텝): 종단 H/H_emit=4.34×10⁻⁵, 깊이 1.1245, 700→1400 모드 변화 ≤1.1×10⁻³. 작은 구조상수(|A|,|N|≤0.02)와 Σ=10⁻³에서 TT(ℓ=2)는 VII_h 1.9×10⁻⁸, V 1.2×10⁻⁷, IX 5.6×10⁻⁸이며 VIII은 비등방 곡률이 전단을 키워 1.8×10⁻²에 이른다. 매개변수는 시연용이며 관측 귀속이 아니다.
- REI AX08 ZERO와 결합한 표(REI `research/r110_bass_ionization`)를 쓰면 같은 VII_h에서 깊이가 1.1782(Δτ_reio=0.054)가 되고 EE(ℓ=3)는 60% 증가한다.

전 실행은 2코어에서 68 s. 1,400 스텝·ℓ≤48 LoS 한 경우 약 11 s.

## 재현

```bash
cargo build --release --locked --manifest-path _rustcore/Cargo.toml --example homogeneous_sky
cargo test --release --locked --manifest-path _rustcore/Cargo.toml --test r110_replay_los
python research/r110_cloud_highl_sky/theory_checks.py
python research/r110_cloud_highl_sky/convergence_study.py --binary _rustcore/target/release/examples/homogeneous_sky --out /tmp/conv.json
python research/r110_cloud_highl_sky/run_highl_atlas.py --binary _rustcore/target/release/examples/homogeneous_sky --raw "$(mktemp -d)/raw" --summary /tmp/atlas.json --tarball /tmp/atlas.tar.gz
```

예: `homogeneous_sky --out DIR --lie-ic X.lie --feedback recoil --dust-fraction 0.75 --ionization TABLE --n-h-emit-m3 2.532e8 --h-emit-s 5.1486e-14 --duration 7.0 --steps 1400 --collision sdirk2 --lie-update congruence --omega-lambda 1.233e-9 --los-lmax 48`.

## 한계

- 기본값은 R109 재현을 위해 BE·additive다. 생산 계산에는 `--collision sdirk2 --lie-update congruence`를 권한다.
- LoS 장의 정확도는 기록된 원천(6성분 정지계 텐서)의 Lagrangian 구적 정확도와 시간 이산화에 의존한다. 관측 ℓ 해상도와는 무관하다.
- 볼로메트릭 수송이다. 주파수 분해·Compton 재분배, H=0 재수축, z<4 천체물리 REI, 원시 섭동 공분산은 포함하지 않는다.
- HYREC 표는 z=1100에서 시작한다. 가시도 전체를 담으려면 z≈1500 이상에서 시작하는 x_e 표가 필요하다(로컬 인계).
