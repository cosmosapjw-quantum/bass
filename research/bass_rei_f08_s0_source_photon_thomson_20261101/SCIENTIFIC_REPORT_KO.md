# BASS→REI S0 first-scatter 과학 결과 | 2026-11-01

원본 S0의 13.7 eV 단색 초기·지속 방출, F08의 H/He 원본 이온화·전자·중성수소 이력, 원본 Verner H I 단면적 및 정확한 Bianchi I photon null-characteristic에 대해 국소적인 first Thomson-scattered Stokes gain을 계산했다. **실제 새 모델 데이터: 4,096개 물리 sky gain 레코드 + 1,032개 photon birth-cohort 레코드**. 이들은 8개 원본 배경·시간 조합의 계산 격자 샘플이며 독립 천문 관측이 아니다.

| Original proper t [s] | Bianchi mean P/I | Bianchi max P/I | FLRW max P/I |
|---:|---:|---:|---:|
| 2.5e12 | 8.216618678863649e-4 | 1.30246859211689e-3 | 2.5990553834347108e-15 |
| 5.0e12 | 6.895339834433336e-4 | 1.0931060136242974e-3 | 1.6280478170734356e-14 |
| 7.5e12 | 5.526808812959268e-4 | 8.762317262486202e-4 | 1.3659351558440181e-14 |
| 1.0e13 | 4.217193847278587e-4 | 6.68677000592525e-4 | 6.20474414871541e-15 |

- 최종 원본 F08 photon_n=0.05007081654542054/H, 독립 정확한 characteristic+HI birth 이력 모델 photon_n=0.047001270459869876/H, 차이 -6.1304094826698075%. 원본 photon_n에는 이미 guard가 포함돼 있어 추가 guard 합산 금지. 원본 HI gamma와 새 모델 차이 +3.535666311697683%.
- 최종 원본 H I 자유 전자 이력은 별도 저장된 16,001행과 H/He 전하수지 전체 표본에서 상대 오차 최대 3.34e-16 일치. 핵심 입력/모델 소스 12파일 SHA256 고정.
- 원본 아래 10eV guard_num=0.0010016543797005872/H (원본 photon_n의 2.0004754242263265%); 진짜 원본 S0 null characteristic 지원 하한은 12.383882550536338eV. 반면 새 characteristic 계산의 10eV 이하 광자는 0. 원본 이산 photon-state와 정확한 원래 S0 방출 characteristic의 source-support 불일치로 판정한다. 원래 remapping의 누적 확산이 가능한 원인이지만 구체적 단일 원인은 아직 독립적으로 입증하지 않았다. 이를 전체 원본 IVP를 무효화하는 일반 no-go로 확대하지 않는다.
- 실제 상태: 15/15 일반 테스트와 15/15 python -O 테스트 PASS; H/He source identity, SHA falsification, Verner threshold, cutoff split, GL isotropy, FLRW 영편광, Bianchi nonzero polarization, 4096개 CSV row 전수감사, 수송행렬 trace, Stokes positivity 포함. Same-author hostile audit; 외부 독립 referee NOT_RUN.
- Bianchi 최종 대표 outgoing n에서 P/I=2.5131667330466673e-4 (128 birth/16×32 입사각), 256 birth=2.513169027976254e-4, 256 birth+Simpson32=2.513163667393072e-4. 입사각 24×48, 128 birth=2.5131663539071874e-4. 이 차이는 quadrature sample stability이지 model-error certificate가 아니다.

**Science admission:** 기존 REI-F08 H/He source trajectory는 HOLD, 원래 F05 46,080셀 [160,161] 승인 BLOCKED, F09 atomic provider-domain BLOCKED. 따라서 본 BASS 연구는 **실제 S0 source-prescription + original H/He matter history + independent transport + local Thomson source**, 완전한 source-owner equal F08 photon-state replay나 관측자까지의 polarized radiation transfer가 아니다.

**DAG:** REI CENTRAL 28/88 REPORTED, 신규+0; Working 33/88 REPORTED(비가산), Physical Fast 4/7; BASS 9/15 SCOPED/SOURCE_MAPPED (FULL count 미확정), 신규 full+0. 원본 생산, main, 기존 다른 PR, 물리 허용오차를 변경하지 않았다. 재귀 메타감사·새로운 source-only atlas는 중단. 다음은 원본 F05 수용과 F09 공급자 도메인, 혹은 동일 광자 source owner의 원래 이산 광자 수송과 observer LoS polarized collision을 실질적으로 결합하는 작업.

## 재개 후 추가 적대적 검산 및 claim ceiling

- 2026-11-01 복원된 4,096행의 국소 gain을 별도 `audit_science.py`에서 전체 읽어 산란 Stokes positivity 및 `P=√(Q²+U²)/I`를 재확인했다. 모든 8개 실제 REI branch/epoch 스냅샷에서 방출 입사 광자 에너지와 산란 gain의 전방향 적분을 비교했으며 최대 상대 잔차 **3.2555256268551602e-9**였다 (16×32 midpoint outgoing grid). FLRW control의 최대 편광률 **1.6280478170734356e-14**.
- 위 잔차는 국소 Thomson gain 정규화 검증만을 의미하며, 원래 REI-F08 이산 광자 상태의 동등성이나 모델오차 인증이 아니다. 원본 대비 photon number −6.1304094826698075%, HI 광이온화율 +3.535666311697683%라는 차이를 보존한다.
- `lower_guard_n`의 10 eV 이하 광자는 원래 정확한 source 특성선의 하한 12.383882550536338 eV와 정합되지 않는다. 모델의 이산 재배치가 발생 원인일 가능성은 있지만 유일한 원인으로 단정하지 않는다. 원래 F08 scientist admission HOLD를 유지한다.
- 후속 추가 수송 실험이나 독립 sky atlas는 이 branch에서 승인하지 않는다. 다음 물리 진전은 원래 F05의 source-safe first tick 수용/거절 판정, F09 소스 유효 도메인 해소, 동일 photon owner 기반 post-scatter line-of-sight 관측 편광 수송이 필요하다.
