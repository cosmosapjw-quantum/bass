# REI: 실제 ZERO milestone과 조건부 first-passage 오차 전파

2026-10-14 Asia/Seoul. BASS 스레드 범위의 읽기 전용 supplier다. Actual REI branch/code/STATE/supervisor를 수정하지 않았고 solver를 시작하지 않았다. 기존 사용자 허가와 별도로 실행 소유자의 자원 배치·staged release를 임의로 바꾸지 않는다.

## 1. Actual current owner와 이미 끝난 준비

처음 live read 11:25:29UTC에서 HEAD d662637da4705b6546fab5d46a83bcec83dba974, clean tracked worktree였다. AX07은 실제 ZERO zbar20→4의 conditional scoped 완료, AX08 signed family는 진행 중, AX11·AX12는 pending이다. T1의4096MiB binary/config 및 variant configs는 이미 OWNER가 준비·심사했다. HH68의 source-pair semantic guard와 HE51 normalization/stitching도 별도 supplier 결과다. 이 스레드가 그것을 구현했거나 소비된 것으로 주장하지 않는다.

11:39:35UTC의 actual intake HEAD는1cff09ef35196443d3a25d484c928b1512ae22c2다. `sources/rei/STATE.json`과 SOURCE_RECEIPT가 그때의 실제 snapshot이다. 이후 owner state는 최종 delivery receipt에서만 추가하며 frozen 과거 상태를 소급 고치지 않는다.

완료 ZERO `history.csv`의165923083bytes/312238rows를 한 번 stream으로 읽고 SHA256 `4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f`를 actual completed-case descriptor와 맞췄다. 파일 size/mtime는 읽는 동안 변하지 않았다. Initial/final, 각0.1/0.5/0.9의 모든 upward bracket, Tgas extrema의 총10native rows를 원문 그대로 추출했다. 전체165MB history를 이 capsule에 넣거나 새 chemistry/ledger suite를 실행한 것은 아니다.

Actual owner reducer는 `compare_histories.py`, 당시 SHA b49fbed5f31a45e866915846357d1ddfdef8708ff7ba97ed17695ec8a5c3dc60다. Source-pair binding 의무는 HH68가 이미 다룬 것으로 분류하며 새 반복 guard를 만들지 않았다. 이 supplier의 새 목표는 아직 UNKNOWN인 **milestone 오차와 first-passage 안정성**이다.

## 2. 저장된 reference에 대한 실제 milestone

Owner는 첫 upward `x_i<c<=x_(i+1)`, theta=(c-x_i)/(x_(i+1)-x_i)를 사용하고 L=ln(a),elapsed proper time을 각각 같은 theta로 선형보간한다. Signature(-,+,+,+), t는 zbar20초기면 이후 경과 gas proper seconds이며 absolute cosmic age가 아니다. xHII는 local homogeneous ionic fraction이지 filling fraction QV가 아니다.

이번 reference calculation은 저장 binary64 t,x를 exact dyadic으로 읽고 scientific targets1/10,1/2,9/10을 exact rational로 사용한다. L knots는 owner와 같은 binary64 math.log(a)를 exact 데이터로 올린다. z=exp(-L)-1 표시는 point arithmetic이며 certified physical decimal accuracy가 아니다. Owner의 float0.1 threshold 및 float 조립과 비교한 t 차이는 각각(-1,0,0)seconds였다. 이1초 차이는 source 변경이나 물리효과가 아니라 정해진 reference arithmetic 표현 차이이며 global time error를 뜻하지 않는다.

|xHII|native indices|elapsed proper time [Myr]|reference zbar|
|---:|---|---:|---:|
|0.1|200603→200604|277.02164237474864|10.248068402397193|
|0.5|268273→268274|607.75946746982|6.816991167760682|
|0.9|287814→287815|789.4172701085173|5.8045371895307705|

1JulianMyr=31557600000000s이다. 각 target의 upward crossing은 whole saved stream에서1회였다. Native bracketing values,exact rational theta,t,local represented slope와 codecomparison은 ZERO_MILESTONES.json에 보존한다. Native samples는31만개 전체의 source digest에 결속되지만10행 밖 이력을 보간하여 재구성하지 않는다.

Evolution/refinement error와 continuous interpolation error는 여전히 null이다. 위 자릿수는 reproducible reference 값이며 physically accurate timing으로 읽지 않는다. Fraction floor1e-7나 Newton residual을 milestone 오차반경으로 대입하지 않는다.

## 3. 단조성·최소 기울기 없이 가능한 conditional interval

연속 참해 X(t), 연속 piecewise-linear reference Xhat(t), nonnegative continuous envelope d(t)가 실제로 주어져

    |X(t)-Xhat(t)|<=d(t)  for EVERY t in[t0,t1]                (MS.1)

를 만족한다고 하자. U=Xhat+d,L=Xhat-d를 두고 first hitting time T(Y)=inf{t>=t0:Y(t)>=c}, 빈 집합은 infinity로 정의한다. 그러면

    T(U) <= T(X) <= T(L).                                    (MS.2)

왼쪽: U가 아직 c 미만이면 X도 c 미만이므로 더 일찍 도달할 수 없다. 오른쪽: L이 c 이상인 첫 시각에는 X도 c 이상이므로 그때까지 반드시 hit했다. Initial overlap/initial above는 t0의 hitting과 prehistory UNKNOWN을 구분한다. Global monotonicity나 dX/dt의 positive lower bound는 쓰지 않았다.

이 간단한 enclosure는 여러 crossing, reheating과 재중성화, flat crossing에도 유효하다. T(U)가 없으면 envelope 아래의 모든 X는 represented interval에서 미도달이다. T(U)만 있고 T(L)이 없으면 finite upper endpoint가 없으며 `POSSIBLE_HIT_NO_FINITE_UPPER_BOUND`로 남긴다. True event가 반드시 존재한다고 말하지 않는다. 미래 t1이후 또는 t0이전의 crossing을 만들지 않는다.

`code/milestones.py:first_passage_band`는 PL Xhat,d에 대해 이를 exact Fraction으로 계산한다. Scalar radius는 uniform envelope다. **Node-only error는 MS.1이 아니다.** `CONTINUOUS_ERROR_ENVELOPE`와 nonempty `bound_authority`가 없으면 numeric interval 생성을 거절하며, radius=None이면 reference result만 반환한다. bound_authority는 caller의 증거 참조이고 helper가 그 proof를 검증했다는 뜻이 아니다.

Node errors ei와 cell curvature bound M2가 있는 경우에만

    |X(t)-Xhat(t)| <= (1-theta)e_i+theta e_(i+1)
             +M2 h² theta(1-theta)/2                         (MS.3)

를 활용할 수 있다. 이 이차식 전체를 input PL envelope로 그대로 부르면 안 된다. 안전한 한 가지 adapter는 각 cell의 M2 h²/8을 양 끝 error에 추가하여 전체cell을 위에서 덮는 것이다. 공유node는 양옆curvature addend의 최대를 써야 한다. 이 curvature adapter는 이번 production 구현 범위 밖이다. Curvature가 없으면 d를 null로 유지한다.

같은 조건에서 candidate/reference first-hit brackets [aC,bC],[aR,bR]가 닫혔을 때만

    DeltaT in[aC-bR,bC-aR]                                  (MS.4)

로 이동량을 얻는다. 미완료 signed case, unknown envelope, onset identity mismatch가 있으면 interval도 unknown이다. 한 case의 bound를 다른 shear sign에 전용하지 않는다.

## 4. 실제 코드·검증과 연결

새 milestone helper21 unit tests와 Jet1 test가 통과했다. 첫 linear envelope case는 실제 RED→GREEN이다. Nonmonotonic first event,flat crossing,initial overlap,never-hit,possible-only,negative radius,NaN,node-only rejection,huge coordinate origin exact arithmetic을 검사했다. 실제ZERO10rows에 대한18조건도 통과했으며 bound는 모두null로 남는다. Actual owner reducer를 patch하거나 raw history를 다시 적분하지 않았다.

새 `REI_AX11_MILESTONE_ENVELOPE_INTERFACE`와 `REI_ZERO_NATIVE_MILESTONE_READOUT`는 supplier ready-for-owner-import다. Canonical AX11은 실제baseline+2refinement 및 signed family·controller release가 남아있다. Prepared T1을 다시설계하거나반복빌드할필요없다. This supplier does not insert an optical-tail gate into abundance goal.

원자lane상태: CR/RCT/HH OFF 유지; stellar50000K와gasT분리; cold helium inventory와warm3/38분리. HE51의 memory 조건은방법상보존하고foreign source numericalradius를이곳에적용하지않았다. 전체program science admission은owner가관리한다.
