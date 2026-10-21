# 보정된 native source adapter의 독립 검토

상태: **`PASS_SCOPED` — 고정 owner에 대한 20개 native 사례와 신규 7개 native tests의 근거를 확인했다. 현재 범위의 blocker는 없다. Production 또는 full EoR 승인은 포함하지 않는다.**

검토자는 `native_adapter.rs`, `native_probe.rs`, `run_native_adapter.py`, `test_native_adapter.py`를 작성하지 않았다. 해당 source, 원래 owner의 관련 구현, 고정 manifest, 실제 `native_s3_run_01` 및 저장소에 복사된 실행 근거를 읽었다. 이 검토 중 Rust 컴파일, native 실행, test 실행, projection optimizer 실행은 모두 **0회**다. SHA와 저장된 scalar의 대조만 수행했다. 검토자는 별도의 `balance_p24.rs` 작성자이므로 이 문서는 그 모듈 자체에 대한 독립 구현 검토로 세지 않는다. 해당 모듈의 독립 검토는 별도 파일에 있다.

## 1. 고정 source와 실제 실행 identity

Native owner는 `cosmosapjw-quantum/rei_bianchi`의 `0e25846433170d0f420c4cda44a0bedbf02cd177`이다. `native_owner_manifest.json`의 **57개 파일, 614,313 bytes**를 실제 owner 디렉터리에서 다시 읽어 각각의 크기, Git blob SHA1, SHA256을 모두 확인했다. Manifest에 빠진 owner source는 없고, 추가 파일은 provenance용 `ORIGIN.json` 하나뿐이다. Adapter가 owner 파일을 수정하는 경로는 없다.

| source | SHA256 |
|---|---|
| `native_adapter.rs` | `de6c6fa54cb7a7dde3a4f8fc67a8b36093debf3c16e6e9d90d07daaf84277acc` |
| `native_probe.rs` | `d392075a49c2c24f3f232f2db7ee11700ed7b883b76de89303177dddd26605c7` |
| `run_native_adapter.py` | `33d6ab09ca831e8a3db633fe1705c1a3f16fa5ca2e44333d0cfeda0147d96159` |
| `native_owner_manifest.json` | `2cd4d9fdfc49c499f1c99c9373680d7056a4223b0107b10e39d7472756bc8cb2` |
| `test_native_adapter.py` | `47cd4d237994da64e4afde727d8b59dda8168d4722543ecb0de3f16a7dd9e299` |

현재 source, 실행 때의 build source, 보존된 source snapshot이 같은 SHA256임을 확인했다. Native probe, native test binary와 `librei_microphysics.rlib`의 실제 bytes도 receipt의 hash와 일치한다. 고정 owner 57개와 adapter 관련 Rust source 4개의 정렬된 compact JSON으로 이루어진 **61개 입력 aggregate**를 독립적으로 다시 해시한 값은 `16a5efa08f31b9ef7cdabe5158f3e654586d25097be5f3aab19c88fdb6b23d23`이다.

실제 JSONL의 SHA256은 `a552cfa04fe2bd1c4141191da24e9417da0121a05597f4daa121a51cbe7022ff`다. 마지막 completion record의 owner commit, source ID `MD14_Z002_FESC_BB50K_13P6_100_V1`, adapter ID `BASS_NEW_ISOTROPIC_SOURCE_ANGULAR_ADAPTER_V1`, row 수 20을 확인했다. 원래 실행 디렉터리와 `evidence_native_s3/run01` 복사본의 JSONL, execution receipt, aggregate 파일도 동일하다. 이 검토는 로컬 근거 검증이며 클라우드 readback을 대체하지 않는다.

## 2. 새 source만 바꾸는 구조

호출자는 `LocallyIsotropicNewBirth`와 `NonTiltedLocalOrthonormal`을 명시해야 한다. `PhysicallyAnisotropic`, `Unspecified`, 다른 frame은 대칭적인 weights가 주어져도 거절된다. 이 선언은 source의 물리적 의미를 알고 있는 호출자의 의무이며 parity로 물리적 isotropy를 추정하지 않는다. 실제 probe는 고정 `AxbiSource` 생성자로 구성한 새 isotropic source에 그 선언을 명시한다.

Adapter는 다음 순서로 처리한다.

1. 현재 geometry의 두 transverse scale factor와 Hubble 성분의 동일성, 기존 state, native ray domain, 양의 weights, normalization, reflection parity, 요구된 P2/P4를 검사한다.
2. `transport.empty_state()`를 만든 뒤 **기존 `CovariantTransport::inject`**로 새 increment를 생성한다. 스펙트럼 적분, 에너지 bin, source support, source emissivity는 원래 owner가 계산한다.
3. ray j의 새 increment에만 `alpha[j] / ray.angular_weight`를 곱한다. 같은 ray의 모든 energy cell에서 photon number와 `energy_ref`에 동일한 양의 계수를 적용하고 energy support는 그대로 둔다.
4. 원래 owner의 `validate_state`를 통과한 새 birth를 기존 state의 clone에 더한다. 이미 점유된 cell의 support는 owner의 `add_support`와 같은 방식으로 물리적 envelope의 합집합을 취한다. 빈 increment가 있는 cell은 건너뛴다.
5. 합쳐진 state가 다시 owner validator를 통과한 뒤에만 `*state=next`로 commit한다.

기존 anisotropic photon stock의 number 또는 energy에 angular 계수를 곱하는 경로가 없다. 새 birth의 생성/검사 실패도 기존 state를 바꾸지 않는다. 기존 state와 겹치는 cell의 support envelope가 합쳐지는 것은 원래 owner의 유한 cell 표현 방식이다. 기존 광자장을 isotropic하게 초기화하거나 새 angular 분포로 다시 배분하지 않는다.

이 구조를 검증하는 실제 native test 로그에는 기존 anisotropic stock의 cell별 `old+born` 일치, 새 emission이 없는 점유 cell의 support 불변성, spectral support와 ray별 number/energy scaling 일치, source 선언/frame 거절, infeasible support의 비변경, 음의 weights 및 음의 dt 실패의 transactionality, 0 dt의 기존 state 동일성, P24 birth의 양성 및 parity가 포함된다.

## 3. 물리 convention과 고정된 출생 weights

Owner의 `AxisymmetricPoint`는 `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `H_perp=H-s`, `H_parallel=H+2s`를 구현한다. 사용자 convention `(-,+,+,+)`, `s=dot b`, `Sigma=sqrt(3)|s|/H`와 호환되는 non-tilted axisymmetric geometry의 prescribed probe이며 Einstein 방정식을 풀지 않는다. 실제 reference는 isotropic한 `[1/21;3]`으로 고정되고, 출생 mean scale은 `exp(0.5)/21`, `H=1e-16 s^-1`, `s=1e-18 s^-1`, `dt=1e12 s`다. 이 검토의 범위는 해당 고정 reference와 공통 z축을 가진 구성이다.

`future_stress`는 이미 생성한 `PhotonState.energy_ref`를 불변으로 읽고, b만 `b+d`로 옮긴 native characteristic scale과 방향을 이용한다. 그 함수는 이후 epoch의 `angular_weight`를 사용하지 않으며 injection 또는 projection을 다시 호출하지 않는다. 따라서 출생 weights의 고정이라는 연구 조건이 실제 native probe에도 유지된다.

Native state의 단위는 photons/total-H nucleus, `energy_ref`는 reference eV/total-H nucleus다. Birth 시점의 물리적 energy-per-H는 `sum(energy_ref * ray.scale)`로 얻는다. 이 원래 owner의 inventory convention을 그대로 사용한다.

## 4. Native 미분에서 측정한 양

Probe는 이후 stress를 **birth energy U_birth**로 나눈 뒤 d에 대한 central difference를 구한다. 측정 대상은 에너지 출생분포에 대한

\[
G_Q(d)=\frac{\sum_{jk}U^{ref}_{jk}\,r_j(b+d)P_2(\mu_j(b+d))}{U_{birth}},
\]

의 `G_Q'(0)`이다. 따라서 실제 birth energy moments를 사용한

\[
G_Q'(0)=-\frac85-\frac{10}{7}M_2^{(E)}+\frac{36}{35}M_4^{(E)}
\]

와 대조하는 코드가 맞다. `ANALYSIS_NATIVE.json`의 `Gprime` 명칭도 이 측정과 일치한다. 일반적인 normalized stress `A=G/F`의 미분에는 `2(M2^(E))^2`가 더해진다. 이번 native birth의 M2가 매우 작더라도 그 두 정의를 혼동해 전 영역의 A 정확도를 승인해서는 안 된다.

20개 저장 row에서 위 Legendre 식을 검토 대상 코드를 import하지 않고 다시 계산한 결과, 저장된 analytic 값과의 차이는 0이다. Native characteristic map으로 얻은 h=`1e-5` central difference의 최대 차이는 `1.3014900268615293e-10`이다. 이는 미리 정한 `1e-8` derivative 비교 gate 이내다. 이 gate는 무차원 angular moment의 `3e-15` gate와 다른 오차 검사다.

예를 들어 `b=-0.3`, 8 rays, 96 energy bins에서는 P2-only의 실제 energy M4가 `-0.07753410240674052`이고 예측 G'는 `-1.679749362475506`, native central 값은 `-1.6797493625837951`이다. 동일한 support의 P24에서는 energy M4가 약 `1.15e-16`, 예측 G'가 약 -1.6이고 native central 값은 `-1.6000000001301484`다. Angular refinement를 16, 32 rays로 바꾸는 행과 같은 support에서 constraint를 바꾸는 행은 별개로 존재한다.

## 5. 실제 20개 사례와 보존 검사의 의미

실제 case 집합은 `n_mu={8,16,32}`, `n_energy=96`, `b={-0.3,0,0.3}`, constraint `{P2,P2P4}`의 18개와, `n_mu=8,b=0.3,n_energy=24`의 두 constraint 사례다. 정확한 20개 key와 중복 부재, 모든 source spectral panels=16, 모든 h=`1e-5`, 모든 저장 숫자의 finite 여부를 확인했다. 같은 n_mu와 b의 24/96 비교는 energy bin 수의 영향을 구분하려는 제한된 비교다.

| 실제 저장값의 독립 readback | 최대값 또는 최소값 |
|---|---:|
| 모든 row의 abs(weight P2) 최대 | `2.671257312569786e-15` |
| P24 row의 abs(weight P4) 최대 | `1.880440247958859e-15` |
| 모든 row의 abs(photon P2) 최대 | `2.692823483801247e-15` |
| P24 row의 abs(photon P4) 최대 | `1.8943460535936732e-15` |
| 모든 row의 abs(energy P2) 최대 | `2.691943454199246e-15` |
| P24 row의 abs(energy P4) 최대 | `1.8943350570508108e-15` |
| 양의 weight 최소 | `0.0005840760190016427` |
| ray rescaling factor 최대 | `3.494746553171729` |
| nonempty-stock photon transfer ledger의 상대 잔차 최대 | `8.627859456293078e-14` |
| nonempty-stock energy transfer ledger의 상대 잔차 최대 | `1.4367906288760241e-13` |
| total photon 대 source emissivity의 상대 차이 최대 | `2.220446049250313e-16` |
| total energy 대 고정 source-cell 평균의 상대 차이 최대 | `5.369926725506957e-12` |

Adapter의 `added` ledger는 새 birth의 native inventory에서 얻는다. Probe의 ledger 검사는 별도로 만든 nonempty anisotropic stock의 before/after inventory 차이를 그 ledger와 비교한다. 단순히 동일한 inventory를 자기 자신과 비교하는 검사는 아니다. 이 제한된 additive transfer 검사의 gate는 상대 `1e-11`이며 실제 잔차는 위 표와 같다.

한편 source emissivity의 photon amount와 source-cell 평균 energy 비교는 별도로 기록한다. 약 `5.37e-12`의 energy 차이는 fixed spectral owner 안의 서로 다른 적분 경로에 대한 diagnostic이다. 24/96 bins의 이 제한된 측정만으로 그 원인별 오차를 인증하거나 연속체 spectral convergence를 승인하지 않는다. Angular P2/P4 constraint 통과를 근거로 이 차이를 0으로 덮어쓰거나 허용오차를 늘리는 경로는 없다. 실제 source-cell energy 차이를 포함한 채 receipt가 `native finite-bin spectral refinement certification`을 미완료로 남긴다.

## 6. 실행 근거와 자원 범위

Receipt의 Rust compiler는 1.94.1이며 원래 owner rlib, 변경된 probe 및 변경된 native tests를 실제 컴파일한 exit 0 로그가 있다. 실행 로그는 **신규 native tests 7 passed, 0 failed**이고 이전 balance 관련 21 tests는 filter되어 재실행되지 않았다. 별도 Python runner parser/identity regression은 실제 **6 tests, OK**다. 그 synthetic parser rows는 native 측정 근거로 사용되지 않았으며 그 구분도 receipt에 명시되어 있다.

Runner는 새 output 디렉터리만 사용하고 기존 output이 있으면 거절한다. Source staging은 고정 commit의 bytes를 검증하며 owner 작업 디렉터리를 편집하지 않는다. 실제 실행은 이미 검증된 owner source를 읽었다. Source와 구현의 전후 identity 확인, timeout, child address-space 제한, 출력 file-size 제한 및 최종 disk 합계 검사가 있다. 설정은 additional workers 4, native owner pool width 1, RAM 16 GiB, disk 4 GiB, job 1800 s로 사용자 상한 안에 있다. 실제 receipt는 elapsed `14.96158348699828 s`, disk `16,409,633 bytes`, child peak RSS `339,804 KiB`를 기록한다.

## 7. 닫힌 범위와 남은 의무

이 검토는 **고정 원본 owner와 연결한 opt-in new-source adapter의 실제 컴파일·주입·transactionality·제한된 ledger 및 linear collisionless response 검증**을 지지한다. 기존 source owner의 default를 변경했다거나 production 전체의 검증이 끝났다는 의미는 아니다.

남은 의무는 다음과 같다.

- 더 높은 angular moments와 유한 d에 대한 continuum angular accuracy 및 refinement.
- Native energy bins/source panels에 대한 정량적인 spectral convergence와 source-cell energy discrepancy 분석.
- 여러 source age의 중첩, reactive/absorbing history 및 전체 source lifecycle.
- Einstein shear feedback과 결합된 진화.
- REI production 또는 full EoR를 위한 별도의 admission.

현 범위에서 수정이 필요한 blocker는 발견하지 않았다. 이번 검토에서 새로 작성한 것은 이 문서와 동반 JSON뿐이며 source, 실행 파일, 기존 owner, PR를 수정하거나 게시하지 않았다.
