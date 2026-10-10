# ACCEL02 독립 판정: N1·N4

N1은 **조건부 point provider 연결 범위에 한해 PROMOTE**, N4는 **이미 실행된 두 frozen history 수신 결과의 재사용 범위에 한해 PROMOTE**한다. 후보 구현·시험 설계에 관여하지 않은 별도 reviewer가 실제 코드, 계약, 원 실패 로그, 양성 실행 증거와 git diff를 읽었다. 새 계산이나 RUN002 재실행은 하지 않았다. 현재 모델 identity는 UNKNOWN이다.

## N1: source와 native gas 경계

검토한 commit은 `e4ef92be7685bae4bba5b421c3ef558da81516a6`이다. 16개 SOURCE_IDENTITY 항목의 실제 파일 해시는 기록과 일치한다. 물리 판단은 그 identity 확인과 별개로 다음 코드 흐름에 근거한다.

HM12 UVB는 초기 photon Cauchy state에만, emissivity는 이후 photon birth에만 쓰인다. 고정 q·μ₀ 좌표에서 에너지비 R=E/q와 각도 Jacobian dΩ/dΩ₀=1/(a_rel³R³)를 사용하므로 reference-volume source의 w/R³ 계수는 일관된다. 후대 50keV source를 담도록 q최대값을 확장하되 아직 physical E>50keV인 빈 특성선만 비활성화한다. active photon을 atomic energy guard 밖에서 허용하지 않는다.

같은 stage의 photon sink를 H/He ionization과 excess heating에 사용하고, imported Case-A provider의 CI/RR/DR/CE/freefree·binding·escape·signed CMB를 실제 axisym_coupled_derivative로 전달한다. proper density↔reference-volume 변환, w=u_th/n_H의 expansion −2Hw, photon work H uγ+2sΔpγ, gas work2H u_th가 선언한 energy ledger와 맞는다. charge·baryon·local energy source의 실제 native guard를 우회하지 않는다.

저장된 Rust4/Python3 targeted tests와 selected8-row literal-C 비교 및51개 domain point 검사는 선언된 기준 안에서 통과했다. 최초 cargo부재, source-band test-oracle 누락, CMB差 cancellation 실패가 보존되어 있다. 마지막 것은 고정 상대기준을 유지하면서 다른 큰 항을 제거해 CMB만 분리한 검증이며 기준 완화가 아니다.

이 결과는 실제 history convergence가 아니다. 초기20K, xHII=2×10⁻⁴는 chosen conditional data이고, neutral helium·prescribed isotropic CMB·primary-only Case-A escape·HM12를 Bianchi의 prescribed source로 사용하는 근사가 남는다. z4에서50keV이상 누락 source 에너지는7.668%이므로 작은 photon-count 누락만으로 full energy/deposition 모델 정확도를 주장할 수 없다. N1은 이 한계를 보고하고 있으므로 scoped binding의 blocker가 되지는 않지만 N3 과학 해석에 그대로 전파해야 한다.

## N4: 기존 native receiver의 의미 보존

검토한 연결 commit은 `6643c70106b329de5b0d9b8fe610b41792c862da`, 실제 수신 증거는 PR137 commit`8904c18e65095cac0fa0526edc364317fcdc953f`이다. PR137→139 native diff를 직접 확인했다. 기존 함수·상수·helper 동작은 바뀌지 않았고 실행 경로에 쓰이지 않는 sampled-rate wrapper만 추가되었다.

C02B의 두16384-cell payload는 실제 수신에 사용된 과학 payload와 연결되어 있다. proper seconds와 properm⁻³를 사용하고 추가 a⁻³ 또는 Doppler계수를 넣지 않는다. REI/BASS의 σT차이는 명시적 비율로 남기며 density를 재조정하지 않는다. 원 decimal-token oracle 실패832개를 보존한 뒤 binary64 input값을 Decimal60으로 비교하도록 oracle 의미를 명시한 V2 판정을 재사용한다. 이 변경은 물리 입력·허용오차 변경이 아니다.

n_e,eff는 producer Δτ로 정의되므로 native 일치는 projection·단위·시계 검증이다. underlying chemistry 또는 history의 독립 재검증이 아니다. τ_end=0에 대한 finite-segment 경계 커널만 판정하며 실제 observer tail은UNKNOWN이다. totalCMBτ, observed-z별 방향 커널, 셀 내부 peak, 전체14-case BASS승격을 주장하면 안 된다.

## 남은 판정

N1·N4 범위에서 발견된 blocking semantic bug는 없다. N2의 전체15.9→4 시간·스펙트럼 refinement와 N3 coupled history는 이번 판정의 대상이 아니다. root가 보존한 NATIVE001 source-entry/energy-ledger 실패는 새로운 수정·증거로 해소되어야 한다. 이 단계에서 전구간 native history를 PROMOTE하거나 N2를 DONE으로 바꾸지 않는다.
