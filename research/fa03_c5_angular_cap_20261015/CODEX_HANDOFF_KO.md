# BASS FA03-C5 구현과 REI owner 인계

새 실제 코드: `research/fa03_c5_angular_cap_20261015/angular_sweep.py` 및 15-unit-test `test_angular_sweep.py`. 정확히 동결된 FA03 R7 source-fa02/fa03와 certificate를 `reference/`에 SHA identity로 포함해 relocation 가능. 새 16→896 angular-node sweeps, fixed n-time RK4, GL8/16 energy-resolved ε=±.1를 실제 Ubuntu PC에서 실행. Original R8 finite36 error bound는 **바뀌지 않는다**. 구적 grid 수렴은 IEEE64 rounding-level 수치 관찰이고 continuum cap/physics convergence PASS가 아니다.

## REI 읽기 전용 상태
2026-10-15 KST: REI original checkout `/home/cosmosapjw/Dropbox/bianchi/rei_bianchi`, recent HEAD `023689835f05555d3eaa2aee9cc399a4a73dd292` (이후 owner가 바꿀 수 있음). Current `STATE.json`: AX07 ZERO scoped full zbar20→4 완료, AX08 signed family 진행중, AX11 시간-refinement 및 AX12 source/IC sensitivity 미실행, scientific admission `NOT_ISSUED`. 원래 PLUS recovery observer의 이전 `LIVE_WORKERS_OR_CHILDREN_HOLD`는 별도 owner 분류가 필요하며, 당장은 owner가 변형 중인 `rust/rei_microphysics/src/lib.rs` tracked dirty를 실제 관측했다. 이번 BASS branch에서는 REI 파일/process/queue/resource/model/source 어떤 것도 변경하지 않았다.

## 실제 연구 보조
- 현재 bottleneck의 주력은 native signed histories checkpoint/continuation, source-bound five-case+refinement, 50000 K stellar emitter vs ~8K gas 분리, H/He thresholds/conservative radiation. C5 FA03 finite angular local result는 이 주력의 **광자화학 numerical gate를 통과시키지 않는다**.
- `bass_cr` PR65는 threshold-aware remapper + 35 tests 및 redshift noncommutation counterexample까지 이미 구현했다. REI rate 수정이 필요하면 해당 실제 source identity와 matched-source replay 조건을 사용자 Codex가 별도 승인·테스트하도록 한다. 이를 BASS에서 중복 수정하거나 REI live에 직접 patch하지 않는다.
- `rec_bianchi` PR85는 독립 LRS Bianchi I finite proper-clock Python reference를 구현했다. 그 결과도 REI Rust native solver와 *semantic* comparison을 거쳐야 한다.
- `BASS_HE` PR56 warm P01 cell와 현재 cold AXBI gas/stellar blackbody physics를 혼동하지 않는다.

## 권장 즉시 사용법 (BASS 분리된 작업에서만)
```bash
cd /home/cosmosapjw/worktrees/bass-fa03-c5-angular-cap-20261015
python3 -m unittest discover -s research/fa03_c5_angular_cap_20261015 -p test_angular_sweep.py -v
python3 research/fa03_c5_angular_cap_20261015/angular_sweep.py --steps 128 --out /tmp/bass_fa03_C5_new.json
```
후속 C6: 수치 구적의 분석적 derivative bound 또는 고정 subcap interval quadrature로 continuum-cap error를 **엄밀히 분리**, roundoff benchmark, source-local observer cap analytic smoothness; 따라서 R8 <4.75e-7에 누락된 angular unknown을 보수적으로 다룬다. 별도 Codex가 승인하지 않은 source replacement·full REI run·T1 start를 하지 않는다.
