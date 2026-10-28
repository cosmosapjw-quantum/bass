# BASS 비섭동 연구의 패키지 통합 전환

전환일: 2026-10-28. 별도 브랜치: `integration/bass-nonperturbative-research-20261028`.
기준 scientific tail: `937acea2875f199eebabaa1abcafd531a64035c3` (BF3-C/PR219).

이 전환은 새 과학 노드를 실행하지 않는다. 기존 main/owner/연구 브랜치는 변경하지 않고, 통합 브랜치에 원문 보고서와 실행 가능한 package API를 추가한다. 과학 DAG는 8/15, BF-3 PARTIAL, BF3-D 미실행, production_ready=false를 유지한다. 통합 테스트의 통과를 이전 모든 과학 결과의 재실행이나 native/Einstein solver의 완성으로 해석하지 않는다.

## 원본 보고서와 단계별 출처

20개 보고서는 각각 원본 ZIP의 REPORT_KO.md를 연구 순서대로 게시했다. 당시의 실행 실패, 미게시 상태, 제한된 판정과 다음 단계가 그대로 남아 있다. 보고서의 상대 경로는 해당 원본 패키지 기준이다. 이 문서와 CI_VERIFICATION.json은 이번 전환의 상태를 기록하며 원문을 소급 수정하지 않는다.

1. [DL-1 공통 연산자 계약](reports/01_DL1.md)
2. [DL-2 편광 source dictionary](reports/02_DL2.md)
3. [KM-1 source-memory 유도](reports/03_KM1.md)
4. [KM-3 독립 Volterra](reports/04_KM3.md)
5. [DV1-A full-polarized harmonic RHS](reports/05_DV1A.md)
6. [DV1-B Bianchi-I 유한시간 삼각 비교](reports/06_DV1B.md)
7. [DV2-A Bianchi-II 곡률 generator](reports/07_DV2A.md)
8. [DV2-B frozen Bianchi-II](reports/08_DV2B.md)
9. [DV2-C expanding Bianchi-II](reports/09_DV2C.md)
10. [DV2-D Bianchi-V class-B generator](reports/10_DV2D.md)
11. [DV2-E frozen Bianchi-V](reports/11_DV2E.md)
12. [DV2-F expanding Bianchi-V](reports/12_DV2F.md)
13. [KM-2A tilted normal-time generator](reports/13_KM2A.md)
14. [KM-2B tilted collision history](reports/14_KM2B.md)
15. [KM-2C Bianchi-I tilted memory](reports/15_KM2C.md)
16. [BF-1 spatial projector](reports/16_BF1.md)
17. [BF-2 collision correlations](reports/17_BF2.md)
18. [BF3-A periodic spatial PDE](reports/18_BF3A.md)
19. [BF3-B retarded spatial source-memory](reports/19_BF3B.md)
20. [BF3-C periodic-lapse characteristics](reports/20_BF3C.md)

`ARCHIVE_SOURCES.json`에는 선택한 20개 원본 ZIP의 SHA-256/크기가 있고, `CODEGEN.json`에는 원본 report Git blob, 28개 module의 source blob과 package output SHA-256, 19개 원본 regression test의 source/output identity가 있다. 원격 stack의 parallel variant와 첨부 원본을 동일시하지 않았다. 필요한 원본 여섯 파일은 `original_overrides/`에 바이트 그대로 보존한다. 전체 원시 캠페인 ZIP을 이 디렉터리에 중복 커밋한 것은 아니다.

## 실제 코드에 적용한 것

`bianchi.nonperturbative`는 설치 가능한 패키지에 포함된다. `research/` 디렉터리나 sys.path 주입 없이 26개 공개 선택 kernel을 제공한다. `_core`에는 보조 모듈을 포함한 28개 파일이 있고, pinned source에서 import/bootstrap만 기계적으로 변경했다. 물리식, 수치 tolerance, 원래 validity support는 변경하지 않았다. P8 호출은 실제 `bianchi.q.polarization`을 사용한다. 원본 연구 파일은 계속 남아 있으며 직접 수정하지 않는다.

공개 진입점은 명시적으로 `backend='python_oracle'`을 요구한다. Native default나 기존 backend policy를 약화하지 않는다. 모든 kernel이 같은 signature/물리 범위를 갖는 단일 production solver라는 뜻은 아니다. 아래처럼 선택한다.

```python
from bianchi.nonperturbative import catalog, load_kernel
print(catalog())
projection = load_kernel('spatial_projection', backend='python_oracle')
```

기존 `PolQState`에는 실제 메서드 `collide_normal_time`를 추가했다. 기존 `collide`, `strang_step`, Q geometry의 native requirement, model runner와 기본 backend는 그대로다.

```python
# ps: 정상적인 BASS PolQState. 기존 native 생성 절차는 이 전환에서 대체하지 않는다.
ps.collide_normal_time(
    dt_s=0.01,
    rest_rate_s=1.3,  # n_e_star * sigma_T * c, D를 포함하지 않는 proper opacity
    beta=[0.3, -0.2, 0.1],
    panels=32,
    backend='python_oracle',
)
```

시간은 normal proper seconds이며 Hubble-normalized 시간이나 전자 rest time이 아니다. Geometry와 beta는 이 collision substep 동안 고정된다. 정확히 한 번의 relative-flux D는 내부 generator가 처리한다. 자동 Strang 호출 교체, geometry-feedback, 전자 반대 four-force, Rust ABI 연결은 하지 않는다.

상태 없이 동일한 경로를 시험하는 공개 함수도 있다.

```python
from bianchi.nonperturbative import normal_time_collision_step
J_next = normal_time_collision_step(
    n, raw_weights, J,
    dt_s=dt_s, rest_rate_s=n_e_star * sigma_T * c,
    beta=beta, panels=32, backend='python_oracle',
)
```

이 공개 collision adapter는 real P8 carrier, finite unit directions, 양의 raw weight, transverse/positive physical coherency를 검사한다. 복소 배열을 실수로 조용히 절단하지 않는다. 실패한 update는 원래 state를 변경하지 않는다. Input/output positivity는 검사하지만 임의 timestep의 positivity 정리를 주장하지 않는다. Common log scale은 보존하고, 지원하는 scaled float64 동적 범위를 넘으면 clipping 대신 거절한다. Signed basis 연구는 각 `_core`의 기존 경로에서 수행하며 이 physical-state adapter와 구별한다.

## 검증과 재현

이번 로컬 통합 검증은 새 경계/실제 caller 테스트 21개와 import를 바꾼 원본 scoped regression 219개, 합계 240개를 실행했다. 과거의 대규모 science verifier는 재실행하지 않았다. DL1의 archive helper 기반 감사는 원문 증거로 보존하며 패키지 전체 인증으로 승격하지 않는다.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/assemble_nonperturbative.py --check
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/validate_research_integration.py
```

재생성은 Python3.13에서 `python scripts/assemble_nonperturbative.py`로 수행한다. 원본/결과 hash가 다르면 중단한다. `CODEGEN.json`이 실행 authority이며 두 script는 실제 source와 원본 PolQState의 나머지 bytes도 확인한다. 원문 report20의 게시 중 추가된 단일 공백은 원본 hash로만 복원하도록 제한했다.

로컬에서 기존 backend-policy test는 optional equinox 부재로 1개 실패했고, 18개 통과/1개 native skip였다. 이 환경 실패는 지우지 않는다. CI는 원래 pyproject의 Python-oracle dependencies를 설치하고 해당 기존 test도 다시 실행한다. 실제 최종 CI 결과는 `CI_VERIFICATION.json`과 Actions artifact의 JUnit/log를 따른다. Workflow가 성공하기 전에는 원격 통과를 주장하지 않는다.

패키지 단독 복사와 wheel 설치에서 `research/` 없이 모든 catalog kernel을 import하고 실제 PolQState 메서드를 확인한다. Native Rust 실행과 native QState constructor는 NOT_RUN이다. 테스트에서는 실제 QState/PolQState class의 storage를 명시적 oracle fixture로 구성했다. 이를 native 생성 성공으로 표현하지 않는다.

## 다음 연구로의 전환

새 연구는 원본 디렉터리에 또 다른 vendor 복사본을 누적하기보다, 위 package API를 기준으로 작은 additive 변경과 대응 테스트를 작성한다. 과학 기준선은 BF3-C 그대로이고 다음 후보는 BF3-D의 inverse phase-space local source mapping이다. 아직 구현하지 않은 BF3-D, Einstein feedback, generic tilt/thermal-recoil, observer sky, 전체 production readiness는 이번 통합으로 닫히지 않는다.

중앙 scientific DAG와 기존 native-first 권한/정책을 그대로 보존했다. 통합 결과는 별도의 `TRANSITION_CONTRACT.json`으로 관리한다. 이 브랜치를 main에 merge하거나 기존 연구 PR들을 자동 merge하지 않는다.
