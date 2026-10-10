# PR104 유한 시간 셀 receiver

실제 BASS fixed_time_optical_depth와 integrate_visibility를 호출하는 density receiver 및 Decimal60 비교 경로를 작성했다. observer tail은 UNKNOWN이며 total/observer visibility는 null이다. 확률은 유한 segment 끝에 대한 조건부 값으로 정규화하지 않는다.

Rust 검사 14개와 Python intake 검사 2개가 통과했다. 첫 campaign은 hash 검증 이후 header preflight에서 실패했다. 계약의 t0,t1,z0,z1,ne_eff,delta_tau와 원본의 t0_s,t1_s,mean_z0,mean_z1,ne_eff_m3,delta_tau가 다르므로 Astra 판단을 요청했다. 실제 receiver 실행은 0회, science solver 실행은 0회이다. 첫 실패 stdout/stderr를 evidence/first에 보존했다.

H/He chemistry, density inversion, 물리 history 또는 observer까지의 전 광학깊이는 이 작업의 범위에 없다. 독립 review와 frozen 두 case 비교는 아직 NOT_RUN이다.

Astra의 HEADER_ERRATUM01 승인에 따라 literal header만 수정하고, 원 계약은 evidence/first/CONTRACT_ORIGINAL.json에 보존했다(SHA e9c9435bf05f8c714d706da546e0c86effc5a6f1c900b6df641c15d4656a31c1). Rust 14개/Python 3개 재검사 통과 후 flrw receiver를 1회 실행했고 exit 0이었다. 이어 producer-depth 비교가 실패하여 rp01 실행은 중단했다. 전체 attempts 2, receiver launches 1, science solver 0, repair 1/1, Cargo build 2/test 2이다.

실패하는 최초 0-based cell 1235에서 Decimal60 상대차는 2.850270609295375e-14이며 frozen 64 epsilon 한계 1.4210854715202004e-14를 넘는다. 최대 cell 1239 상대차는 1.1389401535436185e-13, 실패 cell은 832개다. tolerance와 원본 bytes는 변경하지 않았다. native backward tau/확률 acceptance는 이 실패 이후 검사되지 않았다.

## BINARY64_ORACLE_CLOSEOUT_V2

Astra의 실패 원인 검토에 따라 V1은 HOLD_ORACLE_CONTRACT로 남겨두고 별도 CONTRACT_V2.json 및 readback_v2.py를 추가했다. V1 코드·계약·first/repair 원시 evidence는 보존한다. 새 oracle은 CSV 각 입력을 native가 읽는 binary64 값으로 해석한 뒤 Decimal.from_float(float(token))으로 Decimal60에 옮긴다. c, 두 sigma, rho 계산, 64 epsilon 및 모든 backward tau/survival/P 허용오차와 물리 범위는 원 계약과 같다.

회귀검사는 실제 FLRW large-boundary cell 1235를 포함한 원 decimal-text oracle의 producer-depth 실패, binary64 입력 oracle의 통과, 의도적으로 1% 틀린 depth의 거부를 확인했다. 검사 실행 1회/exit 0이며 evidence/v2_tests.stderr.log에 결과가 있다.

두 frozen case의 producer depth를 receiver 실행 전에 검증하여 모두 통과했다. 보존된 receiver source diff 및 Cargo 입력 hash와 현재 파일을 비교했고 executable hash 532fde5b68b439ddc73503190a2889b80ee07968861d7044089c7ba85ba2a54b가 기존 FLRW 실행 receipt와 일치함을 확인했다. FLRW native stdout은 evidence/repair/flrw.stdout.log 그대로 재사용했다. rp01 receiver만 1회 실행하여 exit 0, wall 0.052443892 s, child user/system CPU 0.035388/0.005898 s를 기록했다. science solver 0, Rust rebuild 0, V2 repair 0이다. 누적 receiver 실행은 V1 FLRW 1회와 V2 rp01 1회로 총 2회이다.

동일 frozen 허용오차에서 두 case 모두 backward tau, survival, interval P 및 closure가 PASS_SCOPED다. FLRW/rp01의 최대 tau 절대오차는 각각 4.18991e-16/1.82080e-16이며 Btau 2.73090e-13/2.72900e-13 이내다. 최대 P 상대오차는 7.49082e-16/4.68505e-16, closure 오차는 4.44089e-16/2.22045e-16이다. 실행 command/exit/자원과 stdout hash, 전체 비교 수치는 evidence/binary64_v2/EXECUTION.json 및 VALIDATION.json에 있으며 rp01 stdout/stderr도 보존했다. V2 독립 Astra review는 `PASS_SCOPED`다. 검토자는 V1 raw-decimal failure 832개를 재현하면서, binary64 oracle의 두 16,384-cell 결과와 saved native stdout을 read-only로 재계산했다. review 중 빌드·receiver·solver 실행과 파일 변경은 없었다. observer tail UNKNOWN과 total/observer visibility null, global admission HOLD를 유지한다.
