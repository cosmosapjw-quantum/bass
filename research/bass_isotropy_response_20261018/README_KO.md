# BASS isotropy / shear response — S8 게시·백업 완료, S9 소스 실행 준비

[S8 결과](S8_RESULTS_KO.md) · [S9 이론](S9_THEORY_KO.md) · [Rust package 검토](S9_THEORY_PACKAGE_REVIEW_KO.md) · [DAG](DAG.json) · [RETURN](RETURN_TO_CHATGPT.json) · [실행 HOWTO](s9_vigilode/HOWTO_KO.md) · [Codex 인계](CODEX_HANDOFF_KO.md)

## 지금 준비된 S9

관련 GitHub와 cloud backup의 새 실행결과 intake를 완료하고 실제 고정 VigilODE를 호출하는 Rust client를 작성했다. 공개 근거는 [PUBLIC_RELATED_INTAKE.json](evidence_s9/intake/PUBLIC_RELATED_INTAKE.json)이며, 확인한 관련 roots와 결과 시점의 coverage를 명시한다. VigilODE 구현은 `a21d573980f66fe02891bd216153443b5352f921`, 원 결과 게시 commit은 `ac1cd2a4738c2441c92e5fdae5f70aba35e53544`다.

두 경로는 실제 `mf_into_ls` workspace와 `SmallProblem<4>`다. 기존 S8 closed manufactured donor의 h,b,y를 적분하고, clock arm은 x를 네 번째 상태로 진화시킨다. 새 birth의 b(u)는 계산 중인 실제 상태에서 얻으며, 고정 birth마다 새 immutable bank와 driver/workspace로 재시작한다. 기존 S8 primal 153행은 비교 전용으로 재사용한다.

Rust adapter 계약검사 5개, 독립 num-dual 단위검사 9개, runner guard 10개가 통과했다. 실제 callback 190개 query vector/38개 bank-state point에서 RHS·JVP·explicit time partial을 비교했고, 최대 scaled JVP 오차는 `4.2848454134986243e-16`이었다. 과거 AD cargo exit101은 unit9 통과 후 rustdoc 실행 경로 오류였고, 원 기록을 보존한 채 별도 doctest만 exit0으로 확인했다.

`num-rational0.4.2`, `num-bigint0.4.6`, `num-integer0.1.46`로 binary64 입력의 P2/P4 admission을 정확한 유리수로 비교한다. `num-dual0.15.1`은 독립 개발 검증에 실제 적용했다. 새 moment constraint나 angular refinement는 이 S9 matrix에서 바꾸지 않는다.

**S9의 실제 history 8개는 아직 실행하지 않았다.** Source/preregistration은 고정했고 GitHub 게시와 두 cloud readback이 다음 단계다. 실제 source commit은 게시 후 영수증에 기록한다. Prereg SHA는 `7e615ea1820e95b6fb61d7a360d13bf0fb560b6f25883e17ed487e8a3505f507`다.

## 완료한 S8

S8 최종 결과·그림·handoff를 `276172ca6cac9cf6b38561fdf9ba0103e1beb9cf`에 게시했고 네 단계의 이중백업을 검증했다. 최종 확인은 [PR comment6268573867](https://github.com/cosmosapjw-quantum/bass/pull/174#issuecomment-6268573867)과 [cloud receipt](delivery/s8/S8_STAGE3_CLOUD_READBACK.json)에 있다.

전체 birth-memory tangent는 기존7개 이력 재사용과 gauge1개로 총8개 적분을 완료해 최종10/10gatePASS했다. 원 직렬화 exit1을 보존했다. Richardson joint 최대오차는 `1.0230571945157863e-10`이고 birth kernel-shift·mu_b·alpha_b 생략 대조군3개를 모두 기각했다.

Native는18개 입력 중17개를 측정했고 n2566개 target이1e-6를 만족했다. 낮은 해상도8개 목표 미달과 STRICT_INTERIOR 지지의 `b0=0.9,n64,P2P4: INNER_P2_PRECISION_LIMIT`1개를 보존했다. 원 owner57파일과 기존 n32 stock은 그대로 유지했다. S2–S7의 완료 근거, S6 rate38/344FAIL·44/238constraint악화, S7 support·exact moment 실패도 재사용·보존한다.

## 실행 및 고정 계약

NCP 준비·실행 명령과 실패 반환 계약은 [HOWTO](s9_vigilode/HOWTO_KO.md)에 있다. 현재 실제로 빌드한 binary는 Python runner만 수정한 뒤 `verified_prior_build`로 재사용했다. [준비 receipt](evidence_s9/vigilode_intake/guarded_preparation/PREPARATION_RETURN.json) SHA는 `671818a3c3761594cb21bbbb933bd9ed6e5bf764fb7ceda720b45eee7e5c44f1`다. Source 게시와 두 백업 검증이 확인된 뒤 고정8개 입력을 실행한다.

Non-tilted axisymmetric Bianchi I, signature(-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), s=dot b, Sigma=sqrt(3)|s|/H. 새 명시적 isotropic birth angular quadrature만 보정하며 기존 physical anisotropic photon stock을 초기화하지 않는다. 양의 weights, reflection parity, source frame, 고정 REI owner `0e25846433170d0f420c4cda44a0bedbf02cd177`를 유지한다.

추가worker<=16, RAM16GiB, disk4GiB, 각job1800초를 유지한다. 과학적 admission은 각 actual receipt가 소유한다. Native finite-bin/history, 실제 MD14 feedback, continuum accuracy, REI production/full EoR/merge는 별도 의무로 남는다.
