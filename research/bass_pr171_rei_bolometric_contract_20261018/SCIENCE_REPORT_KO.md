# BASS PR171: REI native bolometric source 경계 대조

## 판정

- `DERIVED`: REI의 comoving photon rate, proper `n_H`, transport-represented
  mean energy를 같은 midpoint clock에서 쓰면 BASS convention은
  `S=j_proper/H`이다.
- `IMPLEMENTATION_VERIFIED`: PR150 source/transport/driver 세 파일을 exact
  commit에서 추출해 hash로 고정했고, Python control은 Simpson fraction과
  GL8/intersection transport moment를 분리해 구현했다.
- `NUMERICALLY_CHECKED`: z=4,6,10,20의 declared-H controls에서 체적 energy
  conversion residual은 각각 `1.90e-16`, `0`, `1.36e-16`, `1.61e-16`
  (무차원, denominator `max(|S|,|n_H E_REI|)`)였다. 이는 Python mapping
  control의 binary64 algebra 잔차이다.
- `HOLD`: 실제 Rust `SourceLedger` parity, finite proper-time step, BASS
  source identity/checkpoint/restart, H/He absorption and heating, gas/emitter
  `Q^a`, recoil, polarization 및 full EoR admission.

## 금지한 혼동

`U,M`은 PR170의 bolometric first-order stress memory이며 photon number 또는
photoionization rate를 복원하지 않는다. 기존 `Omega_r` collisionless stock과
새 source emission도 별도 항목으로 유지한다. BASS가 이미 계산한 `b,H,s`에
이 passive-tracer stress를 다시 더하지 않는다.

## PR170 재실행

격리 venv에서 36개 과학 test는 PASS했고 세 recovery test도 PASS했다.
그러나 `RUN_GIT_REPLAY.sh`는 current numerical stack에서 generated CSV의
byte hash가 달라 exit 1이었다. 입력 gzip과 restored immutable CSV hash는
원본과 일치한다. 1170 rows 중 최대 field 차이는 dimensionless ratio의
`1.4408801408960503e-11`; `b` 최대 차이는 `6.09013e-14`, `s/H`는
`1.29824e-13`, photon rho는 `2.77556e-17`, photon Delta는 `1.95541e-14`다.
따라서 이것은 `BYTE_IDENTITY_MISMATCH`이며 과학적 integrity failure로
승격하지 않는다.
