# S3: 고정 spectral owner를 유지하는 새 등방 source adapter

## 적용 범위와 원 소스

물리 범위는 non-tilted axisymmetric Bianchi I, signature `(-,+,+,+)`이다.
`a_perp = a exp(-b)`, `a_parallel = a exp(2b)`, `s = dot b`,
`Sigma = sqrt(3)|s|/H`를 유지한다. Native stock 단위는 photons / total-H
nucleus 및 eV / total-H nucleus이다. 이 adapter에서 `a^-3`를 곱하지 않는다.

원 spectral owner는 `cosmosapjw-quantum/rei_bianchi`의 commit
`0e25846433170d0f420c4cda44a0bedbf02cd177`이다. 핵심 blob은 다음과 같다.

| 파일 | 원 Git blob SHA |
|---|---|
| `rust/rei_microphysics/src/axbi_covariant_transport.rs` | `9915d05a00f9c2ad9e0346a1e61ba1d2f37822d3` |
| `rust/rei_microphysics/src/axbi_sources.rs` | `36d24eb13db3fc42321cb0ddb165e003c0a086c7` |
| `rust/rei_microphysics/src/axbi_driver.rs` | `02c6e82c2265f238e5ff77abab1909028e3aa3c2` |

이 파일들을 포함한 compile dependency closure는
`native_owner_manifest.json`의 57개 파일, 614313 bytes이다. 원 파일은
연구 트리 밖에 staging하고 blob SHA 및 SHA256를 검증한다. 고정 owner의
production 파일, source normalization, spectrum, bin, frame은 수정하지 않는다.

## 구현 의미

`native_adapter.rs::inject_new_isotropic`는 명시적으로
`LocallyIsotropicNewBirth`와 `NonTiltedLocalOrthonormal`로 선언된 새 emission만
받는다. Reflection parity만으로 물리적 등방성을 추론하지 않는다. 물리적으로
anisotropic하거나 선언되지 않은 source와 다른 frame은 mutation 전에 거절한다.

현재 source frame의 ray `j`에 대해 원 angular weight를 `q_j>0`, 선택한
보정 weight를 `alpha_j>0`라 하자. 원 native `inject`를 빈 임시 photon state에
호출하여 새 birth `B_jk`를 만든다. 이후 number와 reference-energy increment를
동일한 `alpha_j/q_j`로 곱하고 원 old state에 더한다. 원 `inject`의 spectral
계산이 `B_jk = q_j C_jk`이므로 이 연산은 `alpha_j C_jk`를 만든다.
따라서 spectral shape와 각 bin의 physical support는 그대로다. 양의 배율 때문에
occupied support를 재구성하거나 spectral cell을 이동할 필요가 없다.

원 photon stock `S_jk`는 배율 연산에 들어가지 않는다. 최종 상태는
`S_jk + B_jk(alpha)`이며, support는 두 양의 성분의 envelope 합집합이다.
별도 clone에 모든 연산을 수행하고 원 `validate_state`가 성공한 뒤 한 번만
commit한다. 잘못된 선언, frame, weight, 불가능한 projection, 음의 `dt`,
원 native support 검증 실패 시 old state는 그대로 남는다.

기존 native `CovariantTransport::inject` API가 기본 경로로 유지된다.
이 외부 adapter를 명시적으로 호출해야 새 angular 보정이 적용된다.

## 분리해서 관측하는 항목

`sum alpha_j = 1` 및 `sum alpha_j P2(mu_j) = 0`을 `3e-15`로 검사한다.
P2P4 모드만 같은 tolerance로 P4도 검사한다. 이 tolerance는 dimensionless
angular moment tolerance이며 연속 angular error의 상한이 아니다.

원 native finite-bin 적분은 ray별 energy mapping과 bin intersection을 거친다.
따라서 정확히 보정된 angular weights와 실제 birth의 photon/energy-weighted
P2 및 P4가 bitwise 같다고 가정하지 않는다. `NATIVE_ADAPTER.jsonl`에는 이 세
종류의 moments를 각각 기록한다. 또한 source emissivity가 지정한 총 photons와
고정 source spectral-cell energy moment에 대한 차이도 독립적으로 기록한다.
이 차이를 맞추기 위해 총량을 다시 normalize하거나 tolerance를 넓히지 않는다.

Native transfer ledger는 비어 있지 않은 old anisotropic delta stock을 가진
manufactured test에서 검사한다. `inventory_after - inventory_before`와 새 birth
ledger를 비교하며 상대 기준은 emitted photons/H 또는 eV/H에 대한 `1e-11`이다.
이는 source transfer ledger의 제한된 검증이고 모든 native finite-bin spectral
수렴성의 승인을 뜻하지 않는다.

전단 응답은 공통 평균팽창 인자를 분리한 뒤, 고정 `a`에서 `b`만 변형한
kinematic family로 독립 측정한다. 이는 새로운 cosmological history를 적분한
것이 아니다. 실제 birth energy-weighted moments를 `m2_E`, `m4_E`라 하면

```text
d(Delta/U_birth)/dd at d=0 = -8/5 - (10/7)m2_E + (36/35)m4_E.
```

고정 native source state를 `b +/- 1e-5`의 geometry에 inventory하여 구한 central
difference를 위 식과 비교한다. 보고서는 numerical differentiation 오차와
residual P4가 일으킨 물리적 slope 차이를 구분한다.

## 실행

Rust는 표준 라이브러리만 필요하고 Cargo 패키지 다운로드는 필요 없다.
새 output 경로를 골라 이 연구 디렉터리에서 다음 명령 하나로 진행한다.

```bash
python3 run_native_adapter.py --out /absolute/new/bass_s3_native_output --workers 4 --timeout 1800
```

Runner는 인접한 기존 `rei_bianchi` Git checkout이 있으면 고정 commit의 blob을
읽고, 없으면 57개 고정 GitHub source 파일을 직접 취득한다. `--rei-repo`로
기존 checkout을 지정할 수 있고, `--owner-root`로 이미 검증 가능한 source
staging을 재사용할 수 있다. 어느 경로든 같은 manifest를 검증한다. 컴파일러가
PATH에 없으면 `--rustc /absolute/path/to/rustc`를 지정한다. 예외나 실패는
`RETURN_NATIVE_ADAPTER.json`에 남고 기존 output은 덮어쓰지 않는다.

새 native 검사는 `native_tests::` 7개만 실행하며 완료된 PR173 58행 캠페인과
PR174 기존 5개 Rust test를 다시 실행하지 않는다. 새 측정은 angular node
`8,16,32`, birth `b=-0.3,0,0.3`, P2 및 P2P4 모드의 18행과, 같은 angular
조건 중 `n_mu=8, b=0.3`에서 energy bin만 `96 -> 24`로 바꾼 2행이다.
18행의 energy bin 수는 모두 96이다. 원 source panel은 모든
경우 segment당 16개로 고정한다.

추가 worker 상한 16, RAM 16GiB, disk 4GiB, 개별 job 1800초를 지킨다.
현재 runner의 기본 source-fetch worker는 4개, native thread는 1개다.
새 original-owner compilation, 7개 native tests, 20행 측정 및 6개 Python
parser/source-identity regression을 실제 실행했고 모두 해당 범위에서 통과했다.
실제 결과는 `evidence_native_s3/run01/`에 있다. Native command 전체 wall time은
14.96초, 관측된 child peak RSS는 339804 KiB, 생성한 파일은 16409633 bytes였다.
Native source aggregate는 61개 input의 고정 logical path와 SHA256 목록으로
정의하며, `NATIVE_SOURCE_AGGREGATE.json`에 재현 가능한 recipe와 입력을 보존했다.

### 실행 식별과 저장 증거 readback

다음 값은 저장된 `run01/RETURN_NATIVE_ADAPTER.json`과 직접 대조했다.
현재 코드와 실행 당시 source snapshot의 hash도 일치한다. 이 readback에서는
native 실행이나 테스트를 재실행하지 않았다. 전체 파일별 bytes와 SHA256는
`delivery/native_publish_manifest.json`, 대조 결과는
`delivery/NATIVE_EVIDENCE_READBACK.json`에 기록한다.

| 식별 대상 | SHA256 |
|---|---|
| 61개 native source input aggregate | `16a5efa08f31b9ef7cdabe5158f3e654586d25097be5f3aab19c88fdb6b23d23` |
| `evidence_native_s3/run01/NATIVE_ADAPTER.jsonl` | `a552cfa04fe2bd1c4141191da24e9417da0121a05597f4daa121a51cbe7022ff` |
| `native_owner_manifest.json` | `2cd4d9fdfc49c499f1c99c9373680d7056a4223b0107b10e39d7472756bc8cb2` |
| `native_adapter.rs` | `de6c6fa54cb7a7dde3a4f8fc67a8b36093debf3c16e6e9d90d07daaf84277acc` |
| `native_probe.rs` | `d392075a49c2c24f3f232f2db7ee11700ed7b883b76de89303177dddd26605c7` |
| `balance.rs` | `3053e69d6a501b8beb6c4640db7826af742a85693dabe9b6b8ea523790b93e8a` |
| `balance_p24.rs` | `ad88b0902207747c61145b65d60818efa567999daaf5715dfed7d8352b7f4f14` |
| `run_native_adapter.py` | `33d6ab09ca831e8a3db633fe1705c1a3f16fa5ca2e44333d0cfeda0147d96159` |

| 검증·진단 | 이 20행에서 관측된 최대값 |
|---|---:|
| Nonempty old-stock photon transfer ledger 상대 잔차 | `8.627859456293078e-14` |
| Nonempty old-stock energy transfer ledger 상대 잔차 | `1.4367906288760241e-13` |
| Central derivative와 실제 energy moments 식의 절대 차이 | `1.3014900268615293e-10` |
| Native 총 photons와 source emissivity의 상대 차이 | `2.220446049250313e-16` |
| Native energy와 고정 source-cell mean energy의 상대 차이 | `5.369926725506957e-12` |

마지막 energy 차이는 angular node 및 두 energy-bin 수를 바꿔도 거의 일정했다.
이는 이 두 고정 owner quadrature 사이의 진단값이다. 이 측정만으로 spectral
오차의 전체 원인이나 수렴성을 인증하지 않는다.

Native `n_mu=8`, `b=-0.3`에서 P2-only source의 energy-weighted P4는
`-0.07753410240674052`였다. 이 moments로 예측한 `G'(0)`은
`-1.6797493624755059`이고 central difference는 `-1.6797493625837951`이었다.
같은 grid에서 P2P4 제약을 추가하면 energy-weighted P4는
`1.1453158283861235e-16`, 예측 기울기는 `-1.5999999999999994`, 실제 central
difference는 `-1.6000000001301484`였다. 예측 residual과 finite-difference
정확도를 구별한다. 이론식에 measured moments를 넣은 값이 machine precision에
가깝다고 해서 native 미분 실행 자체가 그 자릿수까지 정확한 것은 아니다.

P2-only angular refinement에서 같은 `b=-0.3`의 native P4는 `n_mu=16`일 때
`-4.305257650834903e-4`, `n_mu=32`일 때 `-2.535081622537971e-9`로 줄었다.
새 P4 제약과 ray 수 증가는 이 비교에서 독립된 축으로 비교된다.

남은 의무는 continuum angular accuracy, source-age/reactive coupling,
finite-bin spectral refinement, Einstein feedback, REI production 및 full EoR이다.
