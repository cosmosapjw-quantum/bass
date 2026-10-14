# FA-02: 고정 cap의 observer rapidity·pointing 응답

2026-10-14. FA-01의 exact Kasner test sector를 재사용한 후속 연구다. 원래 21개 단위와 D9.1, FA-01 normal-cap, F-N-STIM 및 F-ADT-FRAME-01은 유지한다. 새 결과는 derived / symbolically checked / numerically checked / owner-reviewed이며 외부 독립 심사는 미실행이다.

## 명제와 물리적 관측

Observer는 고정 e1축의 표준 boost rapidity chi를 갖고, cap pointing은 observer tetrad의 R3(eta)R2(-zeta)로 정한다. |chi|+|eta|+|zeta|<=.02, cap radius<=.02 rad, x=t/t_o in [.5,1], p=(2/3,2/3,-1/3), energy band [.98,1.02]E_star를 유지한다. 모든 pixel에서 observer e2를 screen에 투영한 analyzer를 사용한다. Pointing으로 analyzer reference axis를 임의로 재정의하지 않는다.

고정 cap label m에서 b=R3(eta)R2(-zeta)m, g=cosh chi, s=sinh chi라 두면

`A=g+s*b1=E_normal_o/E_observer`,
`n=(s+g*b1,b2,b3)/A`,
`dOmega_normal=A^-2 dOmega_m`.

원래 FA.25의 D^-2=A^2와 Jacobian이 정확히 상쇄된다. 고정 label 적분에 Doppler area를 다시 곱하지 않는다. 이것은 경계를 무시한 것이 아니라 moving aperture의 정확한 pullback이다.

Projected-e2 analyzer의 회전은 M=[[c,-sM],[sM,c]],
`c=(A-g*b2^2)/(sqrt(1-b2^2)*sqrt(A^2-b2^2))`,
`sM=s*b2*b3/(sqrt(1-b2^2)*sqrt(A^2-b2^2))`.

Same screen/medium에서 `F'=B-GF-FG^T`, `B=(m3+.1*m4*A*q)*P_s`를 사용하며 cap mean은 `<M F(1) M^T>`다. First/second variation은 이 식을 같은 label에서 미분한 선형 IVP다. B의 A,q,screen 변화와 endpoint의 양쪽 M derivative를 모두 포함한다. 곡선 parameter에서는 J_ij*lambda_i'*lambda_j'뿐 아니라 J_i*lambda_i''도 유지한다.

## Uniform remainder

실제 on-plateau polynomial을 complex |chi|<=.2, |eta|+|zeta|<=.2에 연장한다. 실제 coefficient majorant에서

`||T-I||<.2`, `||G-G0||<.081`, `||M||<1.008`, `|band weight|<1.205`.

Core와 perturbation의 합 growth는 -.238보다 작다. Length .5의 Duhamel 식으로

`sup ||J||_1 <= .5*1.205*1.2^2*1.008^2 = 8608761/9765625 < .9`.

원점에서 sigma=l1(lambda)<=.02이면

`||J-J0-J_i lambda_i||_1 <= .9*(sigma/.2)^2/(1-sigma/.2)`,
`||J-J0-J_i lambda_i-.5 J_ij lambda_i lambda_j||_1 <= .9*(sigma/.2)^3/(1-sigma/.2)`.

일반 real base l1<=.02에서 third directional derivative bound는 `25000/27`. 위 상계는 sampled maximum이 아니라 finite analytic domain의 증명이다. Unknown physical provider error와 finite-precision integration error는 포함하지 않는다.

## 계산 결과

cap=.02에서 (I,Q,U,V)의 rapidity gradient는
`(.054205532991873,.025235188944244,.006907233748759,-.005296959336698)`.
중앙 pointing gradient는 대칭으로0이다. I의 실제 Hessian 독립성분은
`chi chi=.0539683662963`, `eta eta=-.7130311491533`, `eta zeta=-.0727335368061`, `zeta zeta=-.1734589095592`.

lambda=t(.5,.3,-.2)의 직접 cap 비교:

| t | I | first remainder | second remainder | uniform second bound |
|---|---:|---:|---:|---:|
| .005 | .495582881389 | 6.07565e-7 | 3.83461e-9 | 1.44231e-5 |
| .010 | .495716586757 | 2.41603e-6 | 3.06125e-8 | 1.18421e-4 |
| .020 | .495980479438 | 9.55101e-6 | 2.43872e-7 | .001 |

Nonzero base(.005,.003,-.002)의 I gradient는
`(.05448150268826,-.00197567568445,.00012824002379)`다. 두 정밀도 jet 차이는 약2.3e-14 이하였지만 continuum-certified roundoff bound로 부르지 않는다.

새 local checks36개, Wolfram exact algebra7묶음과 inequality5개, xAct null-gauge variation8개를 실행했다. 최초 xAct의 dummy/free index capture 실패를 명시적 scalar contraction rule로 고쳤고 실패·수정 반환을 보존했다. Area 중복, energy/aberration 동결, endpoint/passive analyzer derivative 누락의 negative controls도 포함한다.

## 재현·전체 판본

Python+NumPy로 `python docs/theory/dossier_fa02_20261014/runtime/fa02.py`를 실행한다. 전체 검사에는 SciPy/SymPy가 추가로 필요하며 full archive에 있다. Code는 Taylor monomial 계수를 전달하고 pure quadratic은 Hessian의 절반이다.

전체 PDF/LaTeX/machine package: `BASS_ALL_BIANCHI_FA02_20261014.zip`
- 98,637,515 bytes, 1,249 files
- SHA256 `72569f6e1f72731903e2de85b2e9ec2681dc130ceeb61deb7e1e72d37ceb62fd`
- 현재 합본412쪽, VII권26쪽, canonical equations801개.

Same archive는 계정의 Dropbox와 Google Drive BASS_DERIVATION_DOSSIERS_20260912 폴더에 백업된다. 실제 업로드 결과는 별도 publication receipt에 기록한다. Restore와 과학 검증은 별개다. 이 브랜치는 새 연구 기록과 replay만 추가하며 main/solver를 변경하지 않는다.

SOURCE_CLOCKS hash: 3a1ac8baa12b612eec855fe78a986aca6db577d5625deab952836e2ccd421d8a
ABUNDANCE_MODEL hash: 592c2243a6032b75111fb205ea3e103b229f48194d984e3216b2eb5c74ac9098
같은 event R,Q와 ABF full kappa derivative, DC*r, admissible Bianchi/VI_-1/9 및 H=0 interface를 보존한다. 숫자는 지정된 Kasner family이며 empirical errors는 null이다.

다음 FA-03은 같은 cap/band의 에너지 의존 수동 opacity와 observer–opacity-slope mixed response이며 아직 실행하지 않았다.
