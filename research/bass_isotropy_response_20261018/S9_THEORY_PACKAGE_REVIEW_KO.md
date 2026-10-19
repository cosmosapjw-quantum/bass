# S9 독립 검토: frozen-bank JVP, 명시적 시간 미분, birth cache, Rust AD

## 1. 결과와 적용 범위

S9의 세 상태 \((h,b,y)\)에 대한 해석적 JVP와 명시적 \(x\) 미분을 직접 유도했다. 실제 `coupled_cohorts.py`의 donor 정의와 `s8_tangent.py`의 birth memory를 읽고, VigilODE 세 crate의 operator, GMRES, `OdeProblem`, matrix-free cache 구현에 대조했다. 공식 `num-dual 0.15.1`의 원본 소스를 고정해 독립 방향 자동미분 검산에 적용했으며, 신규 단위 검산 **9/9개가 통과**했다. 이 검토에서 ODE history는 실행하지 않았다.

실제 adapter callback 대조도 완료했다. 다섯 개 고정 bank의 190개 query vector가 모두 같은 사전 기준을 통과했고, 누락된 시간 미분과 stale birth cache를 표현한 대조 네 개는 모두 reject됐다. 결과는 `evidence_s9/theory_review/actual_callbacks/RESULT.json`, 실제 source/binary 결합 증빙은 `ACTUAL_CALLBACK_SOURCE_BINDING.json`에 기록했다.

물리 범위는 non-tilted axisymmetric Bianchi I이며 부호와 정규화는 다음과 같다.

\[
(-,+,+,+),\qquad a_\perp=ae^{-b},\quad a_\parallel=ae^{2b},\quad
s=\dot b,\quad x=\ln(a/a_{\rm ref}),\quad h=H/H_*,\quad y=s/H_*,\quad
\Sigma=\sqrt3|y|/h.
\]

이번 수학적 대상은 S7/S8의 manufactured closed donor와 frozen collisionless cohort이다. 실제 spectral owner는 `0e25846433170d0f420c4cda44a0bedbf02cd177`로 유지한다. 기존 photon stock, 물리적으로 anisotropic한 source, 이전 birth cohort의 방향과 weights를 바꾸는 연산은 포함하지 않는다. 백업과 관련 GitHub의 새 실행결과 확인은 `evidence_s9/intake/FRESH_RELATED_INTAKE.json`에서 완료한 범위를 재사용했다.

## 2. 고정 bank에서 커널을 직접 미분

cohort \(k\)의 저장된 값 \((u_k,b_k,w_k,\mu_{ki},\alpha_{ki})\)를 모두 고정한다. \(w_k\ge0\), \(\alpha_{ki}>0\), reflection pair는 정확히 같은 weight를 가진다. 관측 시점의 \(d=b-b_k\)에 대해

\[
A=e^{2d}(1-\mu^2),\quad B=e^{-4d}\mu^2,\quad
R=\sqrt{A+B},\quad N=B-A/2,\quad D=N/R.
\]

\(A_d=2A\), \(B_d=-4B\), \(N_d=-4B-A\)이므로

\[
R_d=\frac{2A-4B}{2R}=-2D,
\qquad
D_d=\frac{-4B-A}{R}+\frac{2N^2}{R^3}.
\]

따라서 저장된 source frame을 고정한 radiation moment는

\[
\mathcal E=\sum_{ki}w_k\alpha_{ki}e^{-4(x-u_k)}R(b-b_k,\mu_{ki}),
\quad
\Pi=\sum_{ki}w_k\alpha_{ki}e^{-4(x-u_k)}D(b-b_k,\mu_{ki}),
\]

\[
\mathcal E_b=-2\Pi,\qquad Q:=\Pi_b=\sum_{ki}w_k\alpha_{ki}e^{-4(x-u_k)}D_d,
\qquad \mathcal E_x=-4\mathcal E,\quad \Pi_x=-4\Pi.
\]

여기서 아래첨자 \(x\)는 \(b\)와 bank를 고정한 편미분이다. 실제 궤적의 전미분은 \(\mathcal E'=-4\mathcal E-2(y/h)\Pi\)이다. 이 둘을 섞으면 명시적 시간 미분과 Jacobian에 같은 항을 두 번 넣게 된다.

이미 완료된 P4 연구와 연결되는 국소 항도 이 미분으로 확인된다.

\[
D(0,\mu)=P_2(\mu),\qquad
D_d(0,\mu)=-\frac85-\frac{10}{7}P_2(\mu)+\frac{36}{35}P_4(\mu).
\]

이 식은 birth 때 \(P_2\)가 0이라는 사실과 이후 strain response의 정확성이 다른 조건임을 보여준다. 이번 검토는 기존 S3의 angular campaign을 다시 실행하지 않았다. \(P_2/P_4\) 일치가 finite-strain continuum angular accuracy를 보증한다는 결론도 추가하지 않는다.

## 3. 실제 세 상태의 Jacobian과 명시적 시간 미분

실제 Python 구현은 donor를 네 번째 ODE 상태로 진화시키지 않는다. 한 birth interval 안에서 exposure \(\xi\)는 상수이며

\[
\mathcal E_d(x)=d_0e^{-3x-\lambda\xi},\qquad
\partial_x\mathcal E_d=-3\mathcal E_d.
\]

따라서 이 구간 안의 donor 미분에 추가 \(-\lambda\mathcal E_d\) 항은 없다. transfer는 고정된 birth event에서 따로 적용된다. \(L\)을 cosmological constant의 고정 무차원 값이라 하면

\[
F_h=\frac{-h^2-2y^2-\mathcal E_d/2-\mathcal E+L}{h},\qquad
F_b=\frac yh,\qquad
F_y=-3y+\frac\Pi h.
\]

상태 순서 \((h,b,y)\)에서 직접 얻는 행렬은

\[
J=\begin{pmatrix}
-2-F_h/h & 2\Pi/h & -4y/h\\
-y/h^2 & 0 & 1/h\\
-\Pi/h^2 & Q/h & -3
\end{pmatrix},
\qquad
F_x=\begin{pmatrix}
(3\mathcal E_d/2+4\mathcal E)/h\\0\\-4\Pi/h
\end{pmatrix}.
\]

VigilODE의 독립적인 source/API 담당자가 실제 source를 읽고 제시한 식과 세 행 모두 일치했다. S9 adapter의 `FrozenBank::eval`은 이 행렬과 \(F_x\)를 계산하고, `jvp`는 \(Jv\)를 반환한다. `OdeProblem`은 `autonomous=false`와 명시적 `partial_t` callback을 받는다.

정적 작은 상태 API를 위해 \(\chi'=1\)을 추가하면

\[
\widetilde F(h,b,y,\chi)=(F(\chi,h,b,y),1),\qquad
\widetilde J=\begin{pmatrix}J&F_x\\0&0\end{pmatrix},\qquad
\widetilde J(v,v_\chi)=(Jv+F_xv_\chi,0).
\]

외부 solver clock에 대한 편미분은 이 4상태 표현에서 0이다. \(F_x\)는 네 번째 Jacobian 열에 들어간다. 해당 항을 없애는 구현과 시간 상태를 추가하는 구현은 서로 다른 수치 문제를 만든다.

추가로 \(C=h^2-y^2-\mathcal E_d-\mathcal E-L\)을 직접 미분하면

\[
C'=2hF_h-2yF_y+3\mathcal E_d+4\mathcal E+2(y/h)\Pi=-2C.
\]

이 항등식은 constraint 밖의 임의 상태에서도 성립한다. AD 검산에서 constraint를 0으로 강제하거나 \(h\)를 다시 덮어쓰지 않고 확인했다.

## 4. Birth 직후의 실제 jump와 cache 유효성

고정된 event \(x=u\)에서 donor energy \(w>0\)를 꺼내 새 cohort에 넣고 \((h,b,y)\)는 연속으로 둔다. 새 cohort는 실제 계산된 \(b(u)\)를 저장한다. 실제 입력 weights에 대해 정규화하지 않은 합을 정의한다.

\[
S=\sum_i\alpha_i,\qquad M_2=\sum_i\alpha_iP_2(\mu_i),\qquad
M_4=\sum_i\alpha_iP_4(\mu_i),\qquad
K_D=-\frac85S-\frac{10}{7}M_2+\frac{36}{35}M_4.
\]

같은 state/time의 왼쪽과 오른쪽 bank를 비교하면

\[
\Delta\mathcal E=wS,\quad\Delta\Pi=wM_2,\quad\Delta Q=wK_D,
\quad\Delta C=w(1-S),
\]

\[
\Delta F=\left(\frac{w(1/2-S)}h,0,\frac{wM_2}h\right),\qquad
\Delta F_x=\left(\frac{w(4S-3/2)}h,0,-\frac{4wM_2}h\right),
\]

\[
\Delta J=\begin{pmatrix}
w(S-1/2)/h^2&2wM_2/h&0\\
0&0&0\\
-wM_2/h^2&wK_D/h&0
\end{pmatrix}.
\]

이상적인 \(S=1,M_2=M_4=0\)일 때도

\[
\boxed{\Delta F_h=-w/(2h),\quad\Delta(F_x)_h=5w/(2h),
\quad\Delta J_{yb}=-8w/(5h)}.
\]

즉 새 isotropic cohort의 \(\Delta\Pi=0\)과 상태 연속성은 기존 derivative cache의 유효성을 보장하지 않는다. 정규화 오차도 별도로 \(\Delta C=w(1-S)\)에 남기므로, 정규화된 moment를 대신 검사하여 defect를 숨기지 않는다.

실제 VigilODE `rodas5p_matrix_free_fast.rs`의 cache 조건은 time bits, state bits, model epoch, callback allocation identity의 일치이다. refresh 전에 기존 JVP와 callback cache를 무효화하고 RHS와 \(F_x\), JVP linearization을 다시 만든다. 같은 base point에서 step size만 변할 때 J의 재사용은 가능하지만 shifted operator는 \(h_{\rm step}\gamma\) 값까지 별도의 정확한 identity에 포함한다.

`OdeProblem::with_model_epoch`의 계약은 callback이 읽는 데이터가 바뀔 때 client가 epoch를 바꾸는 것이다. callback 포인터만 유지한 채 내부 데이터를 바꾸면 이 계약을 지킬 수 없다. 이번 S9 구현은 **각 birth 이후 새 immutable bank, 새 `OdeProblem`, 새 driver/workspace**를 구성하도록 했다. 이 구조에서 source event를 가로질러 왼쪽 bank의 frozen derivative를 운반하지 않는다.

또한 실제 `eval_partial_t`는 `autonomous=true`이면 0을 반환하고, 명시적 callback이 없으면 중심 유한차분으로 fallback한다. 따라서 3상태 문제는 명시적 \(F_x\) callback을 제공해야 한다. 이 검토와 AD 코드는 유한차분을 사용하지 않는다.

## 5. S8 전체 tangent와 solver 내부 JVP의 구분

위의 \(Jv\)는 현재 solver step의 local state perturbation이다. 저장된 birth 좌표, source-frame 방향, KL weights, energy를 미분하지 않는다. S8의 전체 history sensitivity는 이미 다른 문제를 풀었다. \(\theta=y_0\)인 경우 새 cohort는 \(\delta b_u\)와 그에 따른 \(\mu_\theta,\alpha_\theta\)를 저장한다. 예를 들어

\[
\delta\mathcal E=\sum_{ki}w_ke^{-4(x-u_k)}\left[
\alpha_{ki,\theta}R+
\alpha_{ki}\{R_d(\delta b-\delta b_k)+R_\mu\mu_{ki,\theta}\}\right].
\]

\(\Pi\)에도 같은 구조로 \(D\)의 미분이 들어간다. 고정 birth 시간과 고정 donor parameter에서 \(\theta=y_0\)에 대한 \(\delta w\)는 0이다. 다른 parameter나 움직이는 event time을 미분할 때는 이 가정을 다시 유도해야 한다. 현재 고정 event grid에서 state의 event map은 항등이므로 state tangent는 연속이고, 새 bank에 birth memory가 붙는다.

이번 oracle은 callback 내부의 세 상태 JVP와 명시적 시간 편미분을 검산한다. 이미 완료된 S8의 8개 tangent history를 재실행하지 않았으며, local JVP의 일치만으로 전체 birth-memory sensitivity를 승인하지 않는다.

## 6. 실제 적용한 Rust 패키지

Exa에서 두 검색을 각각 5개 결과로 요청하고 공식 문서와 maintainer source를 읽었다. 검색 색인에는 서로 다른 문서 버전 표기가 섞여 있었으므로, 아래 고정 버전 manifest와 Git tag를 최종 근거로 삼았다. 검색 원문과 공식 문서 응답은 `evidence_s9/theory_review/RUST_PACKAGE_PRIMARY_SOURCES.json`에 보존했다.

| 항목 | 확인 및 적용 |
|---|---|
| `num-dual` | `0.15.1`, `default-features=false`, Rust MSRV `1.89`, edition `2024` |
| 공식 tag | `v0.15.1` → `c5f544267ffebf5c50fbd0f016533f75ca84dd0e` |
| 실제 API | `Dual64::new(real, seed)`, 공개 필드 `re/eps`, trait `DualNum`의 `exp/sqrt` |
| 실제 lock | `num-dual 0.15.1` → `num-traits 0.2.19` → build dependency `autocfg 1.5.1` |
| 기본 feature 제어 | nalgebra feature를 끄고 scalar directional AD만 사용 |
| 라이선스 | `MIT OR Apache-2.0`; upstream 양쪽 license 파일 포함 |
| 원본 source | `src/**`, manifest, README, license, manifest가 명시한 bench 파일 총 31개, 278,470 bytes; 모든 Git blob hash 검증 |
| 보존한 패키지 | VigilODE의 기존 `faer 0.24.4`; 새로운 matrix backend 교체 없음 |

`num-dual`의 목적은 수작업 Jacobian을 독립 chain rule로 대조하는 것이다. 코드의 dual primal은 \(A,B,R,D\)와 RHS를 직접 평가하며 BASS/VigilODE의 해석적 derivative helper를 호출하지 않는다. production callback은 계속 해석적 행렬과 명시적 \(F_x\)를 사용한다.

`faer 0.24.4`의 실제 `Mat::from_fn`, `partial_piv_lu`, `faer::linalg::solvers::Solve` API는 VigilODE core의 `DenseMatrix/LuFactorization`에서 이미 사용된다. 이번 세 상태 검산을 위해 별도의 nalgebra/simba를 추가할 필요는 없었다. faer의 공식 안내도 저차원 vector/matrix와 큰 dense matrix의 목적을 구분한다. 작은 문제에서 어느 driver가 빠른지는 실제 S9 run과 계측으로 판단하며, package 소개만으로 성능 향상을 주장하지 않는다.

공식 출처:

- <https://docs.rs/crate/num-dual/0.15.1/source/Cargo.toml>
- <https://docs.rs/num-dual/0.15.1/num_dual/struct.Dual.html>
- <https://github.com/itt-ustutt/num-dual/tree/c5f544267ffebf5c50fbd0f016533f75ca84dd0e>
- <https://docs.rs/faer/0.24.4/faer/>
- <https://github.com/cosmosapjw-quantum/vigilode/tree/a21d573980f66fe02891bd216153443b5352f921>

Cargo 구성의 세부사항도 실제 실행으로 확인했다. upstream source를 checker workspace 안의 path dependency로 두자 자동 workspace member가 되어 사용하지 않는 dev/optional package까지 해석하려 했다. checker manifest를 `ad_check/checker/Cargo.toml`로 옮겨 원본 dependency를 workspace 밖에 두었고, 정확히 세 dependency package만 잠그는 offline build가 성공했다. upstream source나 manifest를 고쳐 dependency를 숨기지 않았다.

## 7. 실제 AD 검산과 실패 분류

비교 기준은 실행 전에 `CALLBACK_SCALED_GATE=5e-13`으로 고정했다.

\[
\max_i\frac{|\mathrm{actual}_i-\mathrm{reference}_i|}{1+|\mathrm{reference}_i|}\le5\times10^{-13}.
\]

이는 독립 callback 수식의 binary64 비교 기준이다. 기존 \(3\times10^{-15}\) angular moment/normalization 기준을 변경하지 않는다.

| 실제 검산 | 수 | 최대 scaled error 또는 결과 |
|---|---:|---:|
| frozen-bank JVP | 180 vectors, 540 components | `3.9103208355425865e-16` |
| 명시적 시간 미분 | 36 vectors, 108 components | `7.670248546944298e-17` |
| 시간 상태를 추가한 JVP | 108 vectors, 324 components | `1.9514946088073507e-16` |
| 독립 primal 수식 | 36 vectors | `9.457812836833237e-17` |
| constraint 밖에서 \(C'=-2C\) | 36 points | `2.0618799893071615e-16` |
| 정규화된 P24 birth의 jump | 4 events의 국소 평가 | `3.7913415170303094e-16` |
| 고의적 moment/normalization defect | 8 events의 국소 평가 | `1.030588134516469e-15` |
| \(F_x=0\) 누락 음성 대조 | 3 cases | 모두 reject; 최소 mismatch `0.10739005895585806` |
| 입력 domain·reflection·기존 bank 보존 | 5 reject + 5 frozen checks | 모두 예상 결과 |

단위 검산 9개는 0.01초에 통과했고 첫 compile은 2.79초였다. 이 표의 event는 같은 시점의 두 bank를 평가한 횟수이며 history 수가 아니다. 수학적 양의 해가 없는 support를 이 AD 검산으로 해결했다고 간주하지 않는다. `balance_p24.rs`의 rank/convex-hull failure, near-boundary unresolved, positive-support loss, reflection 및 tolerance 거부 분기를 그대로 읽고 보존했다.

설정·실행 실패도 수치 실패와 분리해 보존했다.

- 직접 crates.io read는 sandbox `PermissionError`로 막혔다. 사용 가능한 공개 GitHub connector로 공식 tag와 text source를 읽었다.
- 최초 exact-source 수화 과정에서 CRLF 두 파일의 hash 불일치를 발견했다. 원래 CRLF와 manifest의 마지막 newline 유무를 복구한 뒤 31개 원본 Git blob이 모두 일치했다. `.gitattributes`는 이 두 파일의 bytes를 보존한다.
- 최초 Cargo manifest parse는 명시된 bench 파일 누락으로 실패했다. 원본 bench 파일을 추가했다. 다음 offline resolution의 `approx` 부재는 위의 workspace 배치를 수정하여 해결했다.
- 최초 `cargo test`는 9개 단위 테스트 통과 뒤 `rustdoc` 경로 부재로 doc-test launch가 실패했다. 동일 source에서 `RUSTDOC` 경로를 지정해 **doc-test 단계만** 다시 실행했고 exit 0, doc-test 0개를 확인했다. 단위 검산을 새 history처럼 다시 집계하지 않았다.

원시 수치 관측은 `AD_UNIT_OBSERVATIONS.json`, 후속 build/doc command·로그·RSS는 `AD_BUILD_AND_DOC_RECEIPT.json`과 대응 `.log`, 원본 package hash는 `NUM_DUAL_SOURCE_PROVENANCE.json`에 있다. 실제 ordinary f64 AD의 일치는 interval/continuum certificate가 아니다.

## 8. 실제 callback 대조의 갱신 및 남은 의무

**최종 갱신 상태: actual callback 비교 PASS.** `s9_vigilode/ad_check/compare_callbacks.py`는 다섯 개 고정 bank, 190개 query vector, 서로 다른 38개 bank/state point를 사전 정의한 후 actual Rust adapter의 RHS/JVP/explicit \(F_x\)를 독립 num-dual oracle과 대조했다. 전체 helper wall time은 0.098초였고 ODE history는 0개였다.

| 실제 production 대조 | 최대 scaled error |
|---|---:|
| RHS | `1.408730312680672e-16` |
| JVP | `4.2848454134986243e-16` |
| explicit \(F_x\) | `8.522562581924881e-17` |
| \(Jv+F_xv_x\) 조합 | `4.2848454134986243e-16` |

고의적으로 \(F_x=0\)을 사용한 세 대조의 mismatch는 `0.39324`, `0.48992`, `0.51081`이었다. birth 뒤에 앞 구간의 \(F_x\)를 재사용한 대조의 mismatch는 `0.004344607753021381`로, 모두 같은 `5e-13` 기준에서 reject됐다. 별도의 `SmallProblem::jacobian` callback을 직접 호출하는 검산이나 실제 upstream cache를 고의로 오용해 적분하는 history는 이 비교의 범위에 포함하지 않는다.

대조에 사용한 actual adapter binary SHA256은 `69d884d67d0eb61bd6d4f52b5cfd079c07aa82c35a27272de608b93f16fb4823`이다. 컴파일된 runtime `lib.rs`와 repository의 대응 파일은 모두 SHA256 `204d3fa9dd4a5ed8400410ff1035c4771e11d6ff50d5267a3756a740cf9b731b`였으며, binary/source와 oracle을 대조 전후 다시 읽어 변경되지 않았음을 확인했다. 이후 source가 바뀌면 이 receipt는 이 source에 대한 결과로 보존하고 변경 위험에 맞는 검증을 새로 연결해야 한다.

이 독립 검토의 통과는 다음 의무를 대신하지 않는다. 실제 native source의 finite-bin photon/energy 보존, 기존 owner 보존, 실행 실패를 포함한 S8/S9 native campaign, finite-strain angular refinement, event spacing과 time integration의 분리 검증은 해당 DAG와 raw evidence에 따라 따로 판정한다. full EoR/REI production 확대 근거는 추가하지 않았다. root 작업자가 이번 code/evidence를 stage별 Git 게시·두 클라우드 backup·독립 readback·DAG에 연결한다.

## 9. Source와 재현 경로

VigilODE publication은 `ac1cd2a4738c2441c92e5fdae5f70aba35e53544`이며 실제 읽고 사용하는 source commit은 `a21d573980f66fe02891bd216153443b5352f921`, tree는 `3eb56734d3dbde83298f6c96e33663b0ad0177b6`이다. source와 publication의 선택한 crate files가 모두 같은 Git blob임은 별도의 `SOURCE_MANIFEST.json`으로 확인했다.

재현 명령과 공개 oracle API는 `s9_vigilode/ad_check/README_KO.md`에 있다. 새 실행에는 새로운 output directory를 사용하여 기존 evidence를 덮어쓰지 않는다. 이 helper의 개별 process timeout은 1800초이고 subprocess는 순차 실행한다. 연구 전체의 worker 16, RAM 16GiB, disk 4GiB 기본 상한은 유지한다.
