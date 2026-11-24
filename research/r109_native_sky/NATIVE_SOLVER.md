# BASS native homogeneous-sky solver

하나의 Bianchi 기하, 초기 등방·비편광 복사, 물질 이력과 관측자로부터 전천 온도·편광의 모든 부호 있는 조화계수와 스펙트럼 곱을 계산한다. 시간은 η=ln(a/a_emit)이다. [기준 아틀라스](README_KO.md)는 12개 계열에서 사용자 지정 물질과 해상도에 따라 결과가 얼마나 변하는지 보여 준다.

## 실행

저장소 루트에서 시작한다. Cargo의 고정 git 의존성을 처음 받을 때 네트워크가 필요할 수 있다. 매 실행에 새 출력 디렉터리를 지정한다.

~~~bash
export CARGO_TARGET_DIR="$PWD/_rustcore/target"
cargo build --release --locked --manifest-path _rustcore/Cargo.toml \
  --example homogeneous_sky --example sky_covariance
sky="$CARGO_TARGET_DIR/release/examples/homogeneous_sky"
law="$CARGO_TARGET_DIR/release/examples/sky_covariance"
work=$(mktemp -d)
"$sky" --out "$work/vii" --family VIIh:0.25 --shear 0.18 --duration 0.35 \
  --steps 36 --nmu 16 --nphi 40 --lmax 4 --feedback recoil --tau 0.22 \
  --dust-fraction 0.22 --dust-beta 0.16,-0.08,0.04 --observer-beta 0.1,0.035,-0.025
~~~

| 파일 | 해석 |
|---|---|
| `modes.tsv` | 각 ℓ에서 m=−ℓ,…,+ℓ. T/E/B의 실수·허수 및 TT, TE, TB, EE, EB, BB의 복소 곱. ℓ<2에서 편광은 0. |
| `cl.tsv` | 각 채널을 모든 m에 합해 (2ℓ+1)로 나눈 실수. 관측 잡음·마스크·빔이 적용되지 않은 전천 결과. |
| `diagnostics.tsv` | 시점별 H/H_emit, 정상계 복사·먼지 밀도 모수, 부호 있는 Gauss/Codazzi 잔차, Jacobi 노름, 입체각·에너지·플럭스, 스크린 최소 고유값·누설, bare optical depth, 누적 충돌 에너지 불균형 및 산란 host의 β. |
| `run.txt` | 계산 경로·시간·정규화·편광기저·원 명령. 외부 입력 파일과 실행 파일도 해시로 보존한다. |

## 기하·물질 초기조건

서명 (−,+,+,+)와 오른손 직교 법선 tetrad에서 Σ=σ/H, N=n/H, A=a/H를 사용한다. 구조상수는 Cᵏᵢⱼ=εᵢⱼᵣNʳᵏ+Aᵢδᵏⱼ−Aⱼδᵏᵢ다. Fermi 삼각대와 H>0인 팽창 구간을 다룬다. `--family`는 I, II, III, IV, V, VI0, VIh, VIstar, VII0, VIIh, VIII, IX, 평탄 FLRW를 받는다. III=VI₋₁, VIstar=VI₋₁/₉, VIh와 VIIh의 콜론 인자는 각각 음·양의 h=A²/(N₂N₃)이다. 지정한 계열의 초기 구조상수 규모는 0.3이고 `--shear`는 미리 정한 STF 형상의 초기 진폭이다. FLRW는 `--shear 0`을 명시한다.

행렬 전체와 구조벡터를 지정할 때는 `--lie-ic PATH`를 사용하고 `--family`·`--shear`를 생략한다. 계수는 무차원 초기 Hubble 단위이며 대칭행렬 포장은 11,22,33,12,13,23이다. 예시에서는 VIII의 대각 N과 비대각 Σ가 서로 교환하지 않는다.

~~~bash
cat > "$work/viii.lie" <<'DATA'
shear 0.17 -0.13 -0.04 0.042 -0.028 0.034
n -0.35 0.53 0.72 0 0 0
a 0 0 0
DATA
"$sky" --out "$work/viii" --lie-ic "$work/viii.lie" --duration 0.35 \
  --steps 36 --nmu 16 --nphi 40 --lmax 4 --feedback recoil --dust-fraction 0.28 \
  --tau 0.22 --observer-beta 0.13,-0.07,0.04
~~~

유효 입력은 N=Nᵀ, tr Σ=0, NA=0, Ω_tot=1−Σ:Σ/6+³R/(6H²)>0을 만족한다. 모멘텀 제약은 3Ω_tot fᵢ=3ΣᵢⱼAⱼ+εᵢₘₙNₘᵦΣᵦₙ, f=q/E_tot이다. 이는 Dⱼσʲᵢ=−κqᵢ 규약이다. diagnostics.tsv에는 양변을 왼쪽으로 옮긴 (Dⱼσʲᵢ+κqᵢ)/H²를 기록한다. 필수 f를 정하는 위 식의 우변과 출력 잔차의 기하항은 부호가 서로 반대다. 초기 광자는 등방이므로 flux=0. 필수 총 f가 0이면 두 먼지 흐름에 서로 반대인 `--dust-beta`를 줄 수 있다. f가 0이 아니면 초기 먼지분율 d에서 β_dust=f/d인 동행 두 흐름을 구성한다. 이때 `--dust-beta`를 생략하고 |f|<d<1을 만족시킨다. 모든 계열의 구조상수를 입력할 수 있지만 각 계열에서 수렴성·재수축 경계·관측 식별은 별도의 문제다.

| `--feedback` | 배경과 산란 |
|---|---|
| `tracer` | 충돌 없는 스칼라 복사로 만든 기하 위에서 bolometric 편광을 수송한다. 처방된 전자 β·opacity를 적용한다. 산란한 편광장의 응력과 전자 반작용은 기하 소스에서 제외된다. 초기 등방 스칼라 복사와 양립하는 Codazzi flux가 필요하다. |
| `active` | 실제 광자 P/E, q/E 및 선택적 timelike 먼지의 응력을 기하에 공급한다. 광학률은 0이다. |
| `recoil` | 능동 광자 및 양의 먼지분율을 사용한다. 첫 흐름이 전자 host가 되어 광자 momentum 변화와 반대인 반작용을 받는다. 두 번째 흐름은 이 충돌에서 spectator다. 전자 정지계의 cold Thomson 근사와 유한질량 host의 벌크 운동량 교환이다. 전자 열분포, 내부 에너지, Klein–Nishina 광자 반동과 Compton 주파수 재분배는 별도 모델이다. |
| `auto` | 상수·외부 물질의 bare rate가 0이면 active, 양이면 tracer. host의 반작용에는 recoil을 명시한다. |

감속도 q_dec=Σ:Σ/3+Ω_tot[1+tr(P/E)]/2와 d ln H/dη=−(1+q_dec)를 사용한다. 전단 원천은 3Ω_tot[P/E−I tr(P/E)/3]. 운동론적 모멘트의 필요조건은 P/E−(q/E)(q/E)ᵀ⪰0이다. 이 닫힌 복사·먼지 기하에 별도의 ΛCDM 팽창률을 동시에 강제할 수 없다. 절대 초·밀도 단위는 물리적 앵커로 부여한다.

능동 경로의 기본 `--expansion-equation raychaudhuri`는 실제 총에너지 Ω_tot로 q_dec를 계산한다. `--expansion-equation gauss-reduced`는 중간 단계에서 q_dec에 들어가는 Ω만 Ω_geo=1−Σ:Σ/6−K, K=−³R/(6H²)로 바꾼다. 실제 압력의 STF, 광자·먼지 에너지·운동량, H와 종단 Gauss 잔차는 계속 진화하거나 측정한다. 제약면에서는 두 연산자가 일치한다. Ω_geo≤0이면 Hubble-normalized expanding branch의 해당 감소식을 사용할 수 없다. 긴 재결합 구간에는 해상도별 실제 물질–기하 잔차와 두 정식의 차이를 확인한다. [장시간 실행기·원자료](hyrec_1100/README.md)

## Opacity와 관측자

- `--tau`는 전체 구간의 bare Thomson depth다. 움직이는 전자와 만나는 광선에서는 Dₑ=γₑ(1−βₑ·e)가 곱해진다. `--electron-beta`는 tracer에서 처방하는 전자 속도이고, recoil에서는 실제 host가 이를 정한다.
- `--material FILE`의 헤더는 `eta rate_per_eta beta_x beta_y beta_z`다. 최소 2행, 엄격한 시간 증가, 유한한 비음수 rate, |β|<1, 요청 구간 전체 지원이 필요하다. rate=cσ_T nₑ,proper/H. 각 knot 사이 선형 rate를 적분하고 중점에서 β를 읽는다. β=0인 rate 전용 표는 recoil의 전자 속도를 덮어쓰지 않는다. 같은 실행에서 상수 τ와 재료표를 중복 지정하지 않는다.
- `--ionization FILE --n-h-emit-m3 N --h-emit-s H`는 외부 전자 분율을 host의 시계·고유밀도와 결합한다. 헤더 `eta xe_per_H`, 첫 η=0, 엄격한 증가, 유한한 xₑ≥0, 양의 앵커가 필요하다. dτ₀/dη=(cσ_T n_H,emit/H_emit)(n_H,host/n_H,emit)/(H/H_emit)·xₑ. xₑ를 knot별로 적분하고 host substep의 수소 고유밀도·허블률로 scale한다. 전자의 Doppler는 산란에서 한 번 적용한다. 입력 범위 밖은 외삽하지 않는다. [고정 REC 원자료 및 추출기](hyrec_1100/source.json)

REC HYREC 원자료는 z=1100→0을 덮는다. 아래는 분율표의 처음 0.04 e-fold 구간을 실행한 예시다. 선택한 다른 배경에 외부 xₑ를 이식하는 계산이며, 그 배경에서 원자 반응과 복사장을 동시에 풀거나 천체물리적 재이온화를 복원하는 계산은 별도로 필요하다.

~~~bash
"$sky" --out "$work/hyrec" --family I --shear 0.0001 --feedback recoil \
  --dust-fraction 0.75 --dust-beta 0.001,0,0 --ionization research/r109_native_sky/hyrec_1100/hyrec_xe.tsv \
  --n-h-emit-m3 253202790.82151973 --h-emit-s 5.148602492099132e-14 \
  --duration 0.04 --steps 48 --nmu 10 --nphi 24 --lmax 4
~~~

이 예시에서 실제 종단 bare 깊이는 0.4517254031, 종단 Gauss 잔차는 7.12×10⁻¹⁰이었다. 오늘까지의 전체 간격은 ln(1101)=7.00397413672268이고, 그 장시간 계산에는 별도의 시간·각도·제약 수렴 검사가 필요하다.

광자 진행방향 e에서 E′=DE, dΩ′=D⁻²dΩ, D=γ(1−β·e)다. Bolometric coherency는 D⁴ 및 screen 사상으로 변환된다. 관측자 `--observer-beta`는 최종 법선 tetrad에서 속도/c이며 변환 뒤 outward sky 방향은 −e′다. 삼각대의 proper rotation, 물질의 유한 상대속도, 관측자 boost는 서로 다른 연산이다. 관측자와 기하가 함께 회전하면 개별 m은 섞이고 전 m 합은 보존된다. boost에서는 물리적 에너지·방향·스크린·면적이 달라진다.

## T/E/B와 통계

기하 전송은 유한 전단의 주파수 변화, 방향·스크린의 회전, 입체각 Jacobian을 수송한다. 초기 복사는 단위 세기의 등방·무편광 하늘이다. 실수 대칭 coherency로 I,Q,U를 담으며 원편광 V나 유한 에너지빈은 이 상태에 들어 있지 않다. 전자 정지계 Thomson 이득원의 실수 대칭 3×3 텐서로 매 산란 substep에서 6차원 선형계를 푼다. 산란은 backward Euler 방식으로 광학 step에 대해 1차다. 대칭적으로 배치한 산란 반 step만으로 전체 2차 정확도가 보장되지는 않는다.

T=I¹ᐟ⁴/〈I¹ᐟ⁴〉Ω−1, Q/U는 관측자 자오선·방위각 dyad의 bolometric Stokes를 4〈I〉Ω로 나눈 값이다. 모두 무차원이다. 방향별로 흑체가 유지되지 않으면 I¹ᐟ⁴는 bolometric 유효온도다. 특정 주파수의 열역학온도나 µK 변환에는 절대온도와 bandpass 규약이 필요하다. Condon–Shortley 복소 조화와 HEALPix spin 규약에서 Q±iU=−Σ(Eℓm±iBℓm) {}±₂Yℓm이다. 따라서 같은 천구·기저로 맞춘 October dossier의 양의 E/B 정의와 공통 부호가 다르다. [HEALPix 편광 규약](https://healpix.sourceforge.io/html/intro_HEALPix_conventions.htm)

한 하늘에서 Dℓmˣʸ=aℓmˣaℓmʸ*는 **결정론적 복소 모드 곱**이다. Dℓ,−m=Dℓm*, Cℓ=(2ℓ+1)⁻¹ΣₘDℓm. 개별 m의 TE, TB, EB 허수부는 상대위상 정보를 보존한다. `sky_covariance`는 주어진 양의 가중치에 따른 완전한 하늘 집합 또는 단일 하늘의 SO(3) Haar 회전법칙을 입력으로 받는다. 임의의 (ℓm,ℓ′m′)와 양쪽 T/E/B의 9개 조합에 대해 raw second moment와 centered population covariance를 출력한다. `--all`은 O(ℓmax⁴) 모드 쌍을 생성한다. 단일 고정 sky의 centered covariance는 0이다. 구체적인 공간모드·초기변수의 확률법칙 P와 전달 G가 주어져야 primordial covariance GPG†를 예측할 수 있다. 아래 1:2 가중치는 계산 예시다.

~~~bash
"$law" --member 1 "$work/vii/modes.tsv" --member 2 "$work/viii/modes.tsv" \
  --pair 2 1 3 -2 > "$work/weighted.tsv"
"$law" --haar "$work/vii/modes.tsv" --pair 2 1 2 1 > "$work/haar.tsv"
~~~

## 수치 판정

설정별 실측치는 [기준 아틀라스](README_KO.md)에 있다. 메시의 최소조건 nμ≥ℓmax+1, nφ≥2ℓmax+1은 고ℓ의 수렴 보증이 아니다. 기존 scalar 배경 경로에는 nμ≥4 및 짝수 nφ 조건이 있다. 매우 큰 boost는 각도 집중을 만든다. 시간, 각 quadrature, ℓmax, opacity knot/속도 변화를 각각 세분화하고 복소 alm의 절대 차와 신호가 있는 채널의 상대 L²를 비교한다. 각 모드 수렴과 독립적인 PSD·screen tangency, Hamiltonian/Codazzi, 입체각, 누적 산란 에너지 잔차를 함께 읽는다. 신호가 0인 채널의 상대 변화율은 정의하지 않는다.

### 독립 회전 검사

재현 명령은 다음과 같다. SciPy가 제공하는 스칼라 구면조화를 별도 GL/φ 18×44 격자에서 적분하여 각 proper rotation의 복소 행렬 Dℓ를 구한다. 솔버의 spin-재귀나 Wigner 계산을 호출하지 않는다.

~~~bash
python research/r109_native_sky/verify_lie_rotations.py --binary "$sky" --raw "$work/rotation"
~~~

비대각, 비가환 N·Σ를 가진 VIII, Ω_tot=0.904732, d=0.28, τ₀=0.22, η=0.35에서 기하·관측자 β를 함께 회전했다. 동행 먼지 속도는 Codazzi 식으로 각 입력에 대해 별도로 예측했다. 초기 reference β=(−0.03213,−0.03304,−0.14228), 회전 후 (0.01990,0.02387,−0.14629)이며, 처음 및 종단 Codazzi 노름은 각각 2.9×10⁻¹⁷ 이하, 2.53×10⁻⁷ 이하다. 독립 회전 블록의 유니터리 오차는 9.18×10⁻¹⁵ 이하다. 2개 orientation × 2개 각도 분해능에서 0≤ℓ≤4의 모든 m·채널을 사용했다.

| 광선 격자 | T/E/B의 ‖a′−D a‖₂/‖a‖₂ | 6개 회전 Cℓ 채널 중 최대 상대오차 |
|---|---|---:|
| 10×24 | 3.38×10⁻⁹ / 7.80×10⁻¹⁰ / 1.67×10⁻⁹ | 4.42×10⁻¹⁰ |
| 20×48 | 1.08×10⁻¹⁴ / 7.28×10⁻¹⁴ / 3.12×10⁻¹³ | 6.24×10⁻¹³ |

Cℓ의 상대오차는 각 채널에서 최대 절대 변화량을 그 채널의 기준 max|Cℓ|로 나눈 값이다. D를 생략하면 T/E/B 상대차는 0.518/1.125/1.037이다. 이 검사는 고정된 유한 회전의 covariant sky와 coflow 초기화를 확인하며 공분산이나 우주론적 해석의 독립 증거를 제공하지 않는다. [실행 영수증](LIE_ROTATIONS.json)

장시간 REC 실행에는 두 팽창식·해상도의 개별 결과가 있다. 평탄 무전단 예의 Gauss 감소식 12,288 step에서 τ=1.12442452964, 독립 적분 1.12442423709, 최대 Gauss 잔차 2.53×10⁻⁹이다. VII₀에서 대칭으로 억제되는 B는 성긴 방위각 격자의 누설에 민감하다. 비대각 VIII의 해당 궤적에서는 C₂ᴮᴮ=1.46774×10⁻¹²이다. 이 수치의 입력은 HOWTO의 짧은 η=0.04 예시와 다르다. [장시간 결과](hyrec_1100/long_epoch.json)

## R110 추가 옵션

`--collision sdirk2`(2차 Thomson cell), `--lie-update congruence`(Jacobi·유형·h 보존), `--omega-lambda`(초기 Λ/(3H²)), `--los-lmax L [--los-ntheta --los-nphi]`(기록한 해를 관측자 GL 격자에서 역방향 특성선으로 replay해 임의 ℓ의 `los_modes.tsv`, `los_cl.tsv` 출력). 유도·검증·아틀라스는 [R110](../r110_cloud_highl_sky/README_KO.md).

## R113 추가 옵션

`--route rays|harmonic`(광선 또는 Lie 대수 생성 spin-harmonic PSTF 계층; `--harmonic-lmax L`, 기본 12, 충돌 격자 `--harmonic-ntheta/--harmonic-nphi` 기본 L+3, 2L+6), `--neutrino-fraction f`(초기 복사 에너지 중 무충돌 질량 0 중성미자 비율, active feedback), `--observer-frame normal|host|spectator|radiation|radiation-total`(`--observer-beta` 대신 최종 slice의 관측자 속도), `--recombination matched --t-unit-k T [--recombination-stop-eta E]`(`--ionization` 표에 REC implicit matched 수소 응답을 더함; `recombination.tsv`). 출력에 `lie_constants.tsv`(광자 generator의 Y_LM type 상수), 중성미자가 있으면 `species.tsv`, run.txt에 Lie 불변량·energy frame·local boost·global tilt 키가 추가된다. 기본값의 TSV 출력은 R112와 byte-identical이다 (run.txt에는 키만 추가된다). 유도·검증·아틀라스는 [R113](../r113_cloud_universal_lie_sky/README_KO.md).
