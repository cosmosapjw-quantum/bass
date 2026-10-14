# BASS FA03-R9 결과: 이론 식·주장·경량 실행 계약

2026-10-14. `$physmath-research-loop`에서 명시되지 않은 전체 10단계가 아니라 **다음 선택 단계 R9**만 완료한다. R5–R8의 유효 결과를 완성된 stable equation/claim registry와 검증 가능한 evaluator로 전환한다. 후속 **R10은 READY, 미실행**이다.

- **BASS 핵심 산출물**: `manuscripts/FA03_R9_FORMAL_KO.md`, `contracts/EQUATION_CLAIM_REGISTRY.json`(역사적 ID 보존 50개 행), `contracts/EVALUATOR_CONTRACT.json`, `code/fa03_contract.py`, `evidence/FA03_POLY_SAMPLES.json`. 정확히 같은 GL3×12 36-ray와 고정 observer를 놓고 `|ε|<=0.1`에서 저장된 RK4 Taylor polynomial과 exact finite model의 trace-norm 간격 `<4.75e-7`; positivity `λ_min>0.12548`, Stokes 편광도에 대해서도 source-bound interval 출력.
- **REI 별도 이론 공급**: `manuscripts/REI_R9_INTERFACE_KO.md`, `code/rei_clock.py`, `evidence/REI_CLOCK_R9_SAMPLES.json`. prescribed LRS Bianchi I 기하학적 proper clock의 명시적인 q⁴ 나머지 부등식과 milestone 분해. Signed history가 없을 때 물리적 milestone shift 또는 과학적 수렴을 발급하지 않는다.
- **실행 증거**: `python code/test_r9.py` 13 focused checks; Wolfram 15.0.1 algebra and 실제 원격 Wolfram15.0.0/xTensor1.3.0의 8개 tensor exact zero. `evidence/xact_r9_result.json`, `evidence/xact_stdout.log` 등의 실제 원격 bytes와 source hash를 보존. R5–R8 producer, native chemistry/HPC solver와 old suite는 재실행하지 않았다.
- **재사용**: PR148 R8 head `780b27fe17574ddb1e2ace76516dbe47c81b18f3`, PR147 original+closeout `e67d6fc6c1ad8b3a219abf72104877da1f267e6d`, PR146 peer `3e612547a5e54f48aa930a16778b6b656f4671ad`; archive sha는 `contracts/EQUATION_CLAIM_REGISTRY.json`을 참조. 이 파일은 원본 III/V/I–VII 전체를 변경하지 않는 증보다.
- **병렬 REI Codex 상태**: owner가 이미 수정한 `xe` floor와 HH70/BASS_HE53의 source-bound/PL supplier를 중복 구현하지 않는다. REI의 dirty active 작업트리와 실제 실행을 유지한다. AX08 signed, AX11 refinement, AX12 sensitivity의 admission은 소유자에게 남아 있다. `CODEX_HANDOFF_KO.md` 참조.

## 실행

```bash
python code/verify_package.py
python code/test_r9.py
python code/fa03_contract.py --epsilon 1/10
python code/rei_clock.py --a 0.2 --q 0.01
```

`--out <fresh.json>`는 새 파일만 생성하고 덮어쓰지 않는다. float 대신 문자열 `'1/10'` 또는 `'0.01'`을 입력한다. `reference/`의 immutable source hash가 맞지 않으면 `ContractHold`로 중지한다. 모든 에너지/각도/시계 변수의 정의와 물리 단위 복원은 본문에 명시했다.

`originals/`는 4개 상위 source archive를 원본 SHA256 그대로 포함한다. `reference/ZERO_10_ROWS_PRIVATE.csv`는 해당 user 연구의 **private evidence**이므로 public Git으로 추출하거나 별도 공개하지 않는다. Git branch에는 compact proof, registry, API, 검증 예제만 게시한다. Archive 안의 원본이 존재한다는 이유로 public repo가 모든 원본 파일을 포함한다고 주장하지 않는다.
