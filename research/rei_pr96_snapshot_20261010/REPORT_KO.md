# N4: REI PR96 → BASS 고정 snapshot 수신

17개 source-pinned warm-history epoch를 BASS의 실제 `ElectronState::new`,
`rei::electron_state_from_rei`, `scattering_rate_per_normal_second`로 읽었다.
고정 source dataset과 JSON의 상태·시간을 맞추고 proper cm⁻³를 m⁻³로 한 번
변환한다. HeIII의 전하 가중치는 2다. 물질속도는 0이므로 주어진 proper
elapsed time과 normal time이 같고 두 직교 방향의 Thomson rate가 같다.

`evidence/first/`의 첫 substantive 실행은 17개 전부 PASS_SCOPED였다.
전자밀도·보관된 전자밀도·두 방향 산란율의 Decimal60 비교 최대 상대차는
각각 `2.220446049250313e-16`, 동결 허용치는 `1.4210854715202004e-14`다.
물리/수치 실패는 없었다. 이후 새 Rust 예제의 rustfmt 줄바꿈 검사만 실패했고
원 diff를 `evidence/first/format.stdout.log`에 보존했다. rustfmt 적용 후 한 번의
최종 closeout 실행을 `evidence/final/`에 별도로 남겼다. 첫 결과는 덮어쓰지 않았다.

시작/끝 전자밀도는 `64.1804549337503`, `64.18002849673917 m^-3`,
산란율은 약 `1.279987360571146e-18`, `1.2799788558949967e-18 s^-1`이다.
명령·exit·toolchain·binary hash는 각 `EXECUTION.json`, epoch별 readback과
독립 산술 참조는 `VALIDATION.json`에 있다. Rust 새 예제 2개, 기존 receiver
2개, Python rejection 3개 테스트를 사용한다. 독립 Astra 리뷰는 `PASS_SCOPED`이며,
이는 warm snapshot receiver의 unit/frame/charge readback만 승인한다.

기존 legacy adapter가 받는 photon/group 보조 필드는 API fixture다. 이
수신 함수가 사용하는 값은 proper nuclear densities와 ionic fractions뿐이며,
2904개 source photon node를 4개 그룹으로 변환했다는 뜻이 아니다. BASS의
기존 legacy REI dependency pin도 유지한다.

실행 재현(새 output 디렉터리 지정):

```sh
python3 research/rei_pr96_snapshot_20261010/readback.py \
  --rei-source /path/to/pinned/rei/research/physical_provider_20261010 \
  --output /path/to/new/readback-output \
  --target-dir /path/to/cargo-target
cargo test --offline --locked --manifest-path _rustcore/Cargo.toml \
  --example rei_pr96_snapshot_readback --test rei_axisym_receiver_contract
python3 -m unittest discover -s research/rei_pr96_snapshot_20261010 -p test_readback.py -v
```

이 결과는 조건부 warm-history snapshot의 수신·단위·전하·프레임 검증이다.
화학/background solver 호출, CR 주입, 보간, optical-depth/visibility/observer-tail
적분은 수행하지 않았다. Cold REC IC, 전체 history convergence, CMB 및 global
physical admission은 HOLD다. 다음 작업은 이 diff의 독립 리뷰와, 검토된 scope의
백업·게시다. 이후 N4 전체 history/observer 계약은 해당 DAG 입력이 갖추어질 때
진행한다.
