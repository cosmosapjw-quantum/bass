# Codex / NCP handoff — S7 완료 후 재개

## 1. 우선 확인할 상태

이 문서를 담은 commit과 PR174의 최신 HEAD/comment를 먼저 확인한다. 추가 연구 전에 Dropbox와 Google Drive의 `/BASS_BACKUPS`에서 더 새 실행결과가 있는지 대조한다. 사용자에게 과거 대화, ZIP 다운로드, 첨부, 사전 명령 실행을 요청하지 않는다.

```text
Repository: https://github.com/cosmosapjw-quantum/bass
PR: https://github.com/cosmosapjw-quantum/bass/pull/174 (draft; unmerged)
Branch: research/bass-isotropy-checkpoint-recovery-20261018
Lane: research/bass_isotropy_response_20261018/
Original implementation: 930406550ce6d4d1b2e87f016c5c18fba48c4ccd
Original closeout: a9c3e495fb460b3ec25bfa297b89c8fbd09c07fc
Parent PR173: 4e2d1fa820d6f7baae1069b615fb82a08d53403b
Fixed REI owner: cosmosapjw-quantum/rei_bianchi@0e25846433170d0f420c4cda44a0bedbf02cd177
Source ID: MD14_Z002_FESC_BB50K_13P6_100_V1
Adopted S6 science: 04a3a8515ead0328177b4ad2aa6615a6fe39ed40
Adopted S6 closeout: a9704c6f6eb09c3daa0065a66362ef7547c28e0c
S7 original scientific execution: 2865f60bf0a247eaab4997c222ad82ae22a4c8fa
S7 R2 exact-analysis source: c689dcf151a9b3a6ba830d2a7f4fe8cc6a68385a
S7 R3 source + actual one-history execution: f993bf7121af7bb6d69698244089201e28868ebc
S7 R3 source tree: c920ba0ecf008c296f815edc5d7f28a45ae06d36
Final metadata HEAD: containing commit of this document; exact post-commit proof in final PR174 closeout and final archive GIT_READBACK.json
```

이 문서의 최신 code identity는 f993이다. 그 이후 현재 metadata commit에서 R2/R3와 native scientific source는 바꾸지 않았다. Final metadata SHA를 자기 파일 안에 넣는 무한 self-hash 과정을 만들지 않는다.

## 2. 이미 완료 — 같은 입력의 캠페인을 반복하지 말 것

S2 balance.rs원본5테스트, S3 P2/P4 유도·양의 알고리즘·수치캠페인, S5 실제 native adapter, S6 finite-d/rank1/spectral/source-age는 intake에서 재사용했다. S6 rate FAIL38/344와44/238쌍 악화도 유지한다.

S7 새 실제 결과:

- 닫힌 pressureless donor와 독립 Raychaudhuri H 진화, C′=−2C, 유한 angular equilibrium spectrum 및 full tangent memory 계약 유도. 독립 Fraction28+Decimal5 PASS.
- Coupled main36입력 중28완주/8 support 실패와7benchmarks 실제 실행. Hamiltonian6.2780e−14, 작은 anisotropy nonlinear−linear 오차비3.9908/3.9953.
- Native 원 owner57파일 불변 컴파일.51입력 중42측정/9 support 실패. 여러 birth와 기존 physical anisotropic stock 보존. 흡수는 최종 한 번의 frozen-opacity BE slab이며 새 cohort에 적용했다.
- R2는 기존 raw만 재분석. Native808/808 exact constrained births PASS,42개 물리량과9support 실패 불변. 큰 b,n32,P24 angular error−9.9453e−4가1e−6목표에 FAIL인 두 row 유지.
- Coupled R2:640개 M2모두 PASS,256개 P24 M4중1개 true exactFAIL. Birth50의 M4=−3.0005964896306507e−15. R1/R2 FAIL 그대로 보존.
- R3:기존 P24API 내부 atol1e−15, 최종 exact gate3/10^15유지. b03_n32_P24_K64 **한 이력만** 실제 재실행하여64/64PASS, 최대moment9.6095162e−16. Old-stock hash동일. 다른 grid/history로의 일반화는 미검증.
- Native bin192의 단일 slab photon/energy오차 −2.071e−8/−1.105e−8(흡수 전 inventory정규화)이1e−4목표 PASS. Full reactive history 승인 아님.

주요 machine receipts:

```text
evidence_s7_coupled/run01/RETURN_S7_COUPLED.json
evidence_s7_coupled/revalidate_r2/RETURN_S7_COUPLED_REANALYSIS.json
evidence_s7_coupled/strict_margin_r3/RETURN_S7_STRICT_MARGIN_R3.json
evidence_s7_coupled/EXACT_MOMENT_FAILURES_R2.json
evidence_s7_coupled/FINAL_COUPLED_SUMMARY.json
evidence_s7_native/run01/RETURN_NATIVE_COHORTS.json
evidence_s7_native/revalidate_r2/RETURN_NATIVE_COHORTS_R2.json
evidence_s7_native/revalidate_r2/REUSE_IDENTITY.json
```

## 3. 이번에 준비된 코드와 NCP 역할

현재 S7 범위의 Python/Rust source, 사전등록, source확보/hash검증, 컴파일, 실제 실행, exact 분석과 결과 수집 코드는 모두 준비해 push했고 샌드박스에서 실행했다. **현재 S7 실행을 완료하기 위해 NCP가 필요한 것은 아니다.** NCP의 독립 재현이 필요할 때에는 아래 준비된 runner를 사용할 수 있다. 사용자에게 이 명령을 사전 실행하도록 요구하지 않는다.

이미 존재하는 owner checkout이나 작업 디렉터리를 전환·정리하지 않는다. 새 출력 경로를 사용하며 기존 결과를 덮어쓰지 않는다. Source/code가 바뀌면 기존 prereg hash검증이 실패하는 것이 정상이다. 새 계약과 commit/readback을 먼저 만든 뒤 변경 범위만 실행한다.

아래 명령의 cwd는 BASS 저장소 루트이며, **독립 재현이 필요한 경우에만** 사용한다.

### R3 한 이력 선택적 재현

```bash
python3 research/bass_isotropy_response_20261018/run_s7_strict_margin.py \
  --prereg research/bass_isotropy_response_20261018/evidence_s7_coupled/PREREGISTRATION_R3_STRICT_MARGIN.json \
  --prereg-commit f993bf7121af7bb6d69698244089201e28868ebc \
  --git-root . \
  --out /tmp/bass_s7_strict_margin_ncp_reproduce
```

Python dependencies는 `requirements_s7.txt`의 NumPy2.3.5/SciPy1.17.0이며 원 실행 Python3.12.14였다. Runner는 원래 R1/GL128/R2 failure입력의 SHA도 검증한다.

### Native 선택적 컴파일·재현

```bash
python3 research/bass_isotropy_response_20261018/run_native_cohorts.py \
  --prereg research/bass_isotropy_response_20261018/evidence_s7_native/PREREGISTRATION_R2.json \
  --out /tmp/bass_s7_native_ncp_reproduce \
  --workers 4 \
  --timeout 1800
```

현재 runner의 계약은 **R2 PREREGISTRATION_R2.json**이다. 옛 PREREGISTRATION.json으로 바꿔 넣지 않는다. 정상 Git checkout에서는 runner가 committed source/prereg를 확인한다. 원 owner를 출력 폴더에 자동 확보해 manifest의 size/SHA256/Gitblob을 검사한다. 기존 owner가 있으면 `--rei-repo /existing/path/rei_bianchi`는 pinned commit의 gitshow만 읽고 기존 checkout을 바꾸지 않는다. `--owner-root /existing/path/rei_0e258464`로 검증 가능한 원파일 폴더를 지정할 수도 있다.

원 실행 compiler는 rustc1.94.1이며 `--rustc /existing/path/rustc`로 선택할 수 있다. cargo 없이 rlib/probe를 직접 컴파일한다. Worker4는 owner staging용이며 native/BLAS는1thread다. Output 디렉터리가 존재하면 중단한다.

**Exit0은 모든 scientific target PASS를 뜻하지 않는다.** Native receipt의 `integrity_gates_pass`, `accuracy_targets_pass`, retained failures를 읽어야 한다. 현재 완료된 정상 재현 대상은 integritytrue/accuracyfalse/COMPLETED_WITH_RETAINED_GATE_FAILURES다.

### Native 기존 증거만 선택적 재분석

```bash
python3 research/bass_isotropy_response_20261018/run_native_cohorts.py \
  --prereg research/bass_isotropy_response_20261018/evidence_s7_native/PREREGISTRATION_R2.json \
  --revalidate-existing research/bass_isotropy_response_20261018/evidence_s7_native/run01 \
  --out /tmp/bass_s7_native_ncp_reanalysis_r2 \
  --timeout 1800
```

Git의 lossless gzip을 직접 읽으며, 별도 압축 해제·owner확보·Rust컴파일·native재실행이 없다. Raw SHA256은 `4b544414a434abfb56edbf38c89807aa221b3083185bcfc2499e9f53f6db8122`다.

## 4. 다음 유한 연구 단위의 후보와 실제 미완료

1. Native의 큰 b에서 n_mu>32 또는 다른 양의 support를 위한 angular refinement. 현 owner는 n_mu≤32이므로 단순 CLI 값 변경으로 해결됐다고 가정하지 않는다. 먼저 energy-bin/owner frame 계약을 보존하는 새 제한된 코드 설계가 필요하다.
2. Full coupled tangent: δb(x),birthδb(u),μ/α미분을 포함하는 기억항. 측정한 δΠ의 Duhamel identity를 tangent PASS로 사용하지 않는다.
3. Native MD14에 에너지 공급 성분을 포함하는 Einstein feedback. 현 manufactured donor결과를 원 owner의 astrophysical coupling으로 바꾸어 부르지 않는다.
4. Evolving full reactive absorption/chemistry와 spectral/cohort reconstruction accuracy. 현재 단일 frozen-opacity slab을 전체 history로 확대하지 않는다.
5. R3 stricter internal margin을 다른 입력에 적용하려면 새 범위/계약과 필요한 입력 검증을 남긴다. 원 R1/R2FAIL은 보존한다.

이 후속 항목들은 **아직 구현된 옵션이 아니다**. 현재 S7 재현 pipeline과 구별해서 다음 승인된 연구 단위를 선택한다. 매 단계 백업·게시·DAG를 갱신한다.

## 5. 바꿀 수 없는 계약

```text
non-tilted axisymmetric Bianchi I; signature(-,+,+,+)
a_perp=a exp(-b), a_parallel=a exp(2b)
s=dot b, Sigma=sqrt(3)|s|/H
새 명시적 locally isotropic birth angular quadrature만 보정
기존 photon/physically anisotropic stock 재초기화·재보정 금지
positive weights, reflection parity, source frame, fixed spectral owner 유지
support infeasibility는 witness로 남길 것; 음의 weights/tolerance완화 우회 금지
P2/P4, 국소 spectrum, 작은 ledger를 continuum/full native history승인으로 사용 금지
기존 owner 작업 보존; 추가workers<=16, RAM16GiB, disk4GiB, 각job1800초
REI production/full EoR/merge 자동 확대 없음
```

## 6. Cloud와 종료 증거

[Cloud readback](CLOUD_READBACK_KO.md), [DAG](DAG.json), [RETURN](RETURN_TO_CHATGPT.json), [closeout](PUBLICATION_CLOSEOUT.json)을 읽는다. S7의1~3단계는 Drive의 전체 rawZIP/SHA/CRC/manifest와 Dropbox의 fresh full-object providerhash/size를 검증했다. 이번 Dropbox rawZIP다운로드는 성공하지 않았으며 이전의 rawreadback과 섞어 보고하지 않는다.

Final metadata archive는 앞의 세 S7 source/evidence archive에 이어지는 incremental supplement다. 그 post-upload readback은 자신의 archive 안에 자기 hash를 넣지 않고 최종 PR174 comment에 보관한다. Git HEAD와 단계별 sourcecommit을 구별한다.
