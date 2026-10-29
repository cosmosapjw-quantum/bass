# BASS CE1-N | 패널 내부 연속 source 감소의 독립 이론·코드 구현

2026-10-29 · 물리/소스/경계조건·RK4·허용오차 frozen · 원본 DAG 9/15 (CE-1 PARTIAL)

## 1. 핵심 연구 성과

기존 CE1-M은 원본 물리 여섯 셀과 저장된 양의 ray/mass에 대해, 네 RK4 패널마다 고정된 source discrepancy 상계 eta_j를 사용했다. 이번 CE1-N은 exact Einstein-Vlasov 해와 저장된 exact-binary Hermite 3차 다항식 모두에 대해 방향별 도함수 하한 kappa_j>0를 추가 인증하여, 해당 패널 내부 시간 tau에 대해 eta_j exp(-4 kappa_j tau)를 엄밀한 시변 source forcing 상계로 사용한다.

비교계의 양의 행렬 반군을 유지하며 n개의 substeps에서 source forcing만 감소하는 계단형 MPFR192 upper로 전파한다. 기존 angular continuum integral, source MPFR box 계산, initial Hamiltonian mismatch, whole-panel time residual, Hermite knot jump 등은 재계산·수정하지 않는다. 정리 및 가정과 세부 증명은 THEORY_KO.md 참조.

## 2. 현재 실제 계산 결과

원본 384-ray refinement8, 4 RK4 panels, u=0..0.08, exact stored binary input, target max|Δh|<1e-5:

| 비교 패널당 substeps | CE1-N h upper | 판정 |
|---:|---:|---|
| 1 (=CE1-M) | 9.411551484445186e-6 | MET |
| 2 | 9.343783643876962e-6 | MET |
| 4 | 9.310028683903997e-6 | MET |
| 8 | 9.293183459849245e-6 | MET |
| 16 | 9.284768913839171e-6 | MET |
| 32 | 9.28056365759593e-6 | MET |

이는 n=1보다 1.3917771906762% 더 작은 certified bound. n=32의 staircase exponential source surrogate 대비 multiplicative envelope overestimation factor는 MPFR192 계산상 약 1.001033435 이하. 이는 exact surrogate forcing의 전파 결과에 대한 수학적 factor이지 실제 물리오차에 대한 사후 상대오차가 아니다.

Refinement1, 6 rays: fresh MPFR192 source+whole-panel residual n1=5.256210833627636e-4, n32=5.176219938811385e-4, target NOT_MET. Refinement8 source+time 전체를 이번 런에서 fresh 실행했으며 original source.n/mass 및 RK4/Hermite/time SHA를 기록했다.

Refinement16, 1536 rays: immutable CE1-M 기존 MPFR192 source-only panel upper와 PR246/251 SHA-matched source/path를 현재 실행에서 다시 만들어 확인한 뒤, 수십 단계의 가벼운 MPFR 비교 전파만 새로 실행했다. CE1-M n1=2.9617469790966602e-6, CE1-N n32=2.9290467948909914e-6, 약 1.1040843271373% certified bound 감소, target MET. Ref16의 새로운 angular-source 적분 및 full-panel time residual 재실행은 **NOT_RUN**. 기존 MPFR residue 등은 SHA 검증된 재사용 자료이며 수치실험 독립성·provenance를 구분한다.

## 3. 적대 및 독립 수치 검증

- 테스트 초안의 mpmath Fraction 변환 실수를 실제 FAIL 로그로 발견·수정했다. 추가로 물리 초기 shear와 certified path의 불일치를 public fast API가 허용할 가능성을 발견해 exact `path.states[0]==source.initial_state(shear)` 검증을 추가했다. 잘못된 shear 입력은 현재 ValueError를 일으킨다.
- CE1-N 신규 14 tests PASS: exact rational Bernstein differential control; n=1 exact CE1-M; 1,2,4,8,16,32 monotone staircase refinement; 65-digit mpmath direct time-dependent 2x2 variation-of-constants below MPFR upper; altered Hermite derivative; mutated numerical source SHA; mutated continuum physical cell; changed initial shear; invalid substeps; missing backend.
- 전체 현재 복원 환경 13개 focused inherited/test modules, **121 passed in 24.61s**, exit 0; `compileall` PASS. Local restore is exact baseline source blob matching PR253/251; GitHub CI will be checked independently.
- 120 deterministic positive parameter samples: independent mpmath95 exact matrix exponential+constant-force results vs MPFR192 `propagate_interval`, **120/120 enclosure checks**, no observed undercoverage. This is sampled falsification, NOT full formal program verification.
- Wolfram exact single-ray scaling ratio=1, derivative row sum residual=0; cubic derivative Bernstein identity=0, nonautonomous exp-forcing 2×2 closed-form integral identity=0.

## 4. 실제 실행 비용

한 컴퓨터·동일 Python 환경에서 refinement8 canonical full MPFR source/time proof 16.7563 seconds. Reuse of its fixed certificate and fresh MPFR intrapanel source comparison, 7 runs per n, median:

| n | added reprop median (s) | final h upper |
|---:|---:|---:|
| 1 | 0.01126 | 9.411551e-6 |
| 2 | 0.01564 | 9.343784e-6 |
| 4 | 0.02412 | 9.310029e-6 |
| 8 | 0.04059 | 9.293183e-6 |
| 16 | 0.07359 | 9.284769e-6 |
| 32 | 0.14029 | 9.280564e-6 |

This measures additional a posteriori certification cost only, excludes machine/native Rust production and original official RF-BENCH acceptance. No claim of 4× wall-clock or generic solver acceleration. The useful structural property is avoiding repeated costly angular-box MPFR runs when integrating a time-decaying source-error envelope. More substeps trade extra ~0.13 seconds of comparison for ~1.39% enclosure reduction.

## 5. Literature, evidence and boundaries

- **Mathematical method context:** A. Neumaier, *Global, rigorous and realistic bounds for the solution of dissipative differential equations. Part I: Theory*, Computing 52 (1994), DOI 10.1007/BF02276880; logarithmic norms and a posteriori differential inequalities.
- **Bianchi-I context:** J.M. Heinzle and C. Uggla, *Dynamics of the spatially homogeneous Bianchi type I Einstein-Vlasov equations*, CQG 23 (2006), DOI 10.1088/0264-9381/23/10/016.
- These papers do not establish the specific CE1-N numerical enclosure; the source-local and Bernstein/Metzler synthesis is derived here under explicit conditional assumptions and checked with actual code and Wolfram/mpt reference.
- Scope excludes time-varying source weights, collisions, polarization, tilt, spatial modes, measured sky, general Bianchi or unconstrained code paths. Python/ctypes/MPFR formal program proof NOT_RUN, independent distinct human author review R6/C9 NOT_RUN. Native subagent NOT_EXPOSED (tool inventory), no children simulated.
- Original top-level DAG 9/15 and 21 edges; CE-1 PARTIAL; 18/20 scoped stage outputs with R6/C9 explicitly held; `production_ready=false`, `merge_ready=false`, `auto_next=false`.

## 6. Publish and handoff

Parent reference is `cosmosapjw-quantum/bass` PR #253 HEAD `e4a0feba0e8709d5e996ed8ef4c9c9bf1da4c4d0`; PR #252 is separately complete Draft, DO NOT merge unrelated sibling branch. New opt-in module and focused test only, plus research evidence/plots and stage status. A new isolated PR should be Draft, no parent/main modifications. Check exact new GitHub HEAD CI before scoped release; RF-00/RF-BENCH and native production independent. Stop after the CE1-N bounded unit rather than automatically executing the next node.