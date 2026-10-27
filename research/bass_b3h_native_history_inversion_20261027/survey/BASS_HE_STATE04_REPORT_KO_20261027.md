# HE-EXP-STATE-04 연구·전달 보고서 — 2026-10-27

**범위 내 판정:** 실제 HD–H⁺ 한 상태 edge의 native 하향 계수와 명시적 열적 reciprocity 상향 계수, population-derived 내부 에너지 witness, Bennett 2008 source correction을 독립 이론·코드 검토 후 승인했다. 이는 전체 물리 반응망이나 모든 종의 미분 충돌 공급자 승인으로 확장되지 않는다. Source archive와 delivery tail 모두 Dropbox·Drive 업로드 ACK 및 독립 metadata의 ID/size를 확인했다. 두 원격 사본을 전체 재다운로드해 SHA256을 확인하지는 않았다.

## Source inventory와 구현한 하나의 edge

[EMAA HD Rovibration dataset](https://doi.osug.fr/public/EMAA/EMAA_HD_Rovibration_805a7aa5.html), DOI `10.17178/EMAA_HD_Rovibration_805a7aa5`, 원문은 CC BY 4.0으로 보존했으며 71,451 bytes, SHA256 `feda215f1d75ee85de399903c77e18f62c8e323fe709015215634d6ccc7720b6`이다. 원문은 52개 local levels, 368 radiative transitions, H⁺ collider 1종, 171 collisional rows, 25 native temperatures, 4,275 rate cells를 담는다. [HITRAN spectroscopy](https://doi.org/10.1016/j.jqsrt.2021.107949)와 [González-Lezana 등의 충돌 원전](https://doi.org/10.1063/5.0128598) 및 EMAA를 함께 인용한다. Inventory 전체를 구현한 것이 아니다. 이번 scalar adapter는 HD local level ID 2↔1, 곧 v=0,j=1↔v=0,j=0 한 edge만 다룬다. 52 level ID는 기존 WU aggregate ID에 자동 결속하지 않으며 기존 104 IDs/138 variants/155 event references는 유지된다.

Native 1005 K에서 2→1 하향 계수는 `2.48e-10 cm³/s` = `2.48e-16 m³/s`다. 두 level의 원문 파수 차 `89.227900 cm⁻¹`와 정확한 SI 상수로 얻은 에너지 차는 `Δ=1.772463922970989e-21 J`다. 상대 충돌 에너지 분포가 무상대드리프트 Maxwellian이고 microscopic reciprocity와 source weight 관례가 유효하다는 조건을 호출자가 명시하면, 유도된 상향 계수는 `6.547809139557261e-16 m³/s`, 평형 상부/하부 population 비는 `2.6402456207892184`다. 상향값은 독립 측정값이 아니다. 24개 허용 native 점을 사용하며 원문 마지막 3005 K는 논문의 3000 K support와의 결속 전까지 보존·표시만 하고 실행하지 않는다. 보간·외삽 및 thermal rate에서 DCS 역산은 하지 않았다.

## 수 보존과 에너지 소유권

명시적 collider density를 \(n_p\), 두 population을 \(n_l,n_u\), 상향·하향 계수를 \(k_{lu},k_{ul}\)이라 하면

\[
 j_+=n_p n_l k_{lu},\qquad j_-=n_p n_u k_{ul},\qquad J=j_+-j_-.
\]

출력은 \(\Gamma_u=J\), \(\Gamma_l=-J\), \(\Gamma_{H^+}=0\)이며 HD 총 수와 charge가 보존된다. Population-derived 내부 에너지 witness는 \(\dot U_{\rm int}=\Delta J\), 물질 총 kinetic compensation은 \(\dot K_{\rm material}=-\Delta J\)다. 이 내부 에너지를 독립 RHS로 다시 더하지 않고 explicit state population을 equilibrium heat capacity에도 중복 계산하지 않는다. 총 보상량은 종별 분할을 결정하지 않는다. 종별 heat, momentum, stress 및 독립 internal RHS는 `null`, birth pool은 `UNASSIGNED`다. A21은 별도 radiative metadata이고 충돌마다 광자를 방출하는 규칙이 아니다. 실제 population, relative distribution, species partition 및 deposition은 여전히 호출자와 후속 소비자의 책임이다.

## LiH correction과 동위원소 문제

[Bennett 2008 정오표](https://doi.org/10.1111/j.1365-2966.2008.12586.x)의 27개 native rows는 높은 J quasi-bound dipole matrix-element 코드 오류를 교정한 것이다. 동일 물리 소유자의 [Bennett 2003](https://doi.org/10.1046/j.1365-8711.2003.06422.x) 원표를 현재 선택에서 supersede하며 둘을 더하지 않는다. 원문 단위 `10⁻²⁰ cm³/s`에서 1000 K는 17.7→3.19, 3000 K는 51.2→1.80이다. 교정 fit을 평가하지 않았고 인쇄된 <7% fit residual을 물리 covariance로 취급하지 않았다. 기존 77 native cells와 실행 원장은 그대로다.

[NIST Stwalley–Zemke 표](https://doi.org/10.1063/1.555936)는 ⁷LiH의 D0를 `19589.8 ± 0.3 cm⁻¹`, ⁷LiD를 `19768.8 ± 0.3 cm⁻¹`로 구분한다. Bennett 2003의 권고 LiH 값은 후자의 수치와 일치하는 source 간 isotope 불일치로 보존했다. 원모델 Q를 고쳐 쓰거나 현대 atomic mass를 event mass, RA 최종 state 및 photon branch에 자동 적용하지 않았다.

## 실제 검증과 제한

새 테스트는 19 methods, 1 process, PASS, exit 0; CPU `0.115736379 s`, wall `0.11492365499725565 s`, cap 4 CPU s/15 wall s/256 MiB/1 thread, repair 0이다. 독립 Decimal80 기준, 24 native 점의 reciprocity, population·에너지 보존 및 잘못된 입력을 포함한다. Source preparation·network·model·IO 총 비용은 `UNKNOWN_NOT_ZERO`이며 측정된 test envelope를 end-to-end cap으로 주장하지 않는다.

저장 결과만 읽은 별도 plot은 1 process PASS, CPU `3.35712228 s`, wall `3.3577162440051325 s`, cap 4 CPU s/15 wall s/512 MiB/1 thread, 과학 함수 호출 0이다. Root가 PNG의 축·단위·범례와 3005 K HOLD를 직접 판독했다. 선은 시각적 연결이지 interpolation 승인이나 fit이 아니다. 독립 이론 `PASS_SCOPED_STATE_THEORY`, 독립 코드·저장결과 `PASS_BOUNDED_SOURCE_BOUND_STATE_ADAPTER`, root `ACCEPT_SCOPED_SOURCE_BOUND_REFERENCE`이며 범위 밖 물리 정확도나 covariance를 인증하지 않는다.

## DAG와 게시 상태

Local DAG의 8개 노드는 source, thermal pair, population energy, LiH correction, validated reference의 범위 내 5개 산출물과 정확한 global state/mass binding, differential branch input, named deposition의 열린 3개 의존성이다. 이 5/8은 작업 그래프의 국소 상태로서 전체 물리 완료율이 아니다. Central은 88개 노드이며 로컬 후보는 HE-EXCHANGE, HE-EXP-PAIR, HE-CLOSURE, HE-EXP-CLOSURE의 observation만 바꾼다. 다른 84개 및 새 B3h 관찰을 보존하고 independent review는 metadata-only PASS다. Central과 HE source는 아직 게시되지 않았다.

GitHub `create_tree` 승인 결과는 네 차례 `user rejected MCP tool call`이었다. 네 번째도 기존 DRIFT02 75파일 후보에 관한 것이고 STATE04 직접 쓰기 시도는 0이다. 추가 사유는 제공되지 않았으며 대체 경로를 사용하지 않았다. R10/C10은 partial이다. HE101 C8 `PARTIAL_EXPORT`, 전달 19/20, reserve 0과 기존 PASS/FAIL/FAIL 및 모든 과거 원장·실패·비용을 보존했고 이전 suite START, 재실행, 예산 이전은 0이다.

## 실제 source·delivery identity와 복구

- Source S04 `2addfab8c8975febd69d2c88eecc09afea508fbe`, tree `af0f52ee8885e1a5f31aa933ed5efb730d7dc3bf`. Source ZIP은 15,715,054 bytes, 348 members, SHA256 `d341f4711f652b447e95f51368821d22ba13a2b5d9567c3e9b19b03cfbb83d0c`. Dropbox와 Drive는 upload ACK 및 별도 metadata ID/size를 확인했다. 전체 사본을 내려받아 SHA256을 확인하지는 않았다.
- Delivery D04 `30924d902187777fbff02687639c91d65cf53191`, tree `7529db3500c2f12875da20b3827ad071439ca7d9`, parent S04. Tail ZIP은 2,134,905 bytes, 31 members, SHA256 `489dd9b67aca244d5f7910a1264233da7e288ff1ddc52514c78118e072e8b407`. Dropbox `id:BSpOijBcT10AAAAAAEDHSA`와 Drive `1RyapuOieTIYs__-aYObfPjci9fpjKRuy`는 업로드 ACK와 별도 metadata의 ID/name/size를 확인했으며, Drive parent와 MIME도 일치한다. 전체 원격 재다운로드 SHA256은 확인하지 않았다.
- Git 복구는 `ac6042a6b0610b09d0576538767ee0299389a5eb`을 가진 저장소에서 source ZIP의 실제 bundle을 fetch해 S04에 도달한 뒤, S04를 prerequisite로 하는 tail bundle을 fetch해 D04를 복구한다. 대안은 source ZIP을 펼친 뒤 tail manifest의 28개 변경 경로를 적용하고 미기재 파일을 보존하는 것이다. S04 당시 source backup=false와 D04 당시 tail 미생성·미백업 기록은 각각 과거 시점이며 이 외부 closeout에 실제 ACK를 기록한다.

다음 물리 입력은 exact isotope/state/global identity와 일관된 질량·에너지 관례, energy-resolved differential/branch data, 종별 kinetic partition 및 named deposition/thermalization consumer다. 원격 게시를 다시 진행할 수 있다면 그때 현재 HEAD를 재조회하고 expected SHA 기반 non-force 경로만 사용한다.

중앙 후보의 기계 조립은 기록상 초기 1회, 재적용 1회, 검증 1회다. 그 뒤 중복 `reapplied` 디렉터리가 다시 나타나 보존을 위해 repository 밖으로 옮겼으나 재출현 원인은 확인되지 않았다. 추가 실행이나 과학 오류를 추정하지 않는다.

마지막으로 관측한 Git 작업 트리에서 tracked files는 clean이었고 `delivery/central/reapplied/`는 untracked로 남아 있었다. 추가 정리나 원인 추정은 하지 않았다. 독립 검토자와 root는 assembler·verifier·재적용을 실행하지 않았다고 확인했다.

실제 Drive 다운로드: [STATE04 source ZIP](https://drive.google.com/file/d/1EE-7Xwzp_QOfxX446Mklf-LRLqdjYwVE/view?usp=drivesdk) · [STATE04 delivery tail ZIP](https://drive.google.com/file/d/1RyapuOieTIYs__-aYObfPjci9fpjKRuy/view?usp=drivesdk).