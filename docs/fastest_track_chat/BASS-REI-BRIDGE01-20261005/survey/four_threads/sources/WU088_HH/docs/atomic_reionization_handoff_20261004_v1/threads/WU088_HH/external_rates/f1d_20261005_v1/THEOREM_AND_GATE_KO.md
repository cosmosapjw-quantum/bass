# HH-F1D 정리와 소비자 조건

## 가정과 원소스

원 F1C raw rate와 기록된 enclosure를 계승한다. 0<T<=Tc=3000K에서 kf=1e-20cm3/s, T>Tc에서 k=A*T^p*exp(-B/T), A=1.2e-17,p=1.2,B=157800K다. floor는 물리적으로 승인된 저온율이 아니다. correctedKS에 cutoff를 넣지 않는다. 이번 source fit 재평가는0이다.

고정 비율 r=nHe/nH, nH*a^3 보존, prescribed smooth a(t)>0, H=adot/a, 단일 온도 비상대론적 단원자 이상기체 pgas=2u/3를 가정한다. tilt·비등방stress·다중온도·shock은 이 닫힌 예제 밖이다. 시간은 properseconds, energy는erg/H다. REI의eV/H와 결속할 때 정확히 한 번 변환해야 한다. 원 photon3좌표는 spectator로 유지한다.

z=(h,y1,y2,epsilon,N0,N1,N2), epsilon=u/nH>0,
Pi=1+h+r*(1+y1+2*y2), T=2epsilon/(3kB*Pi),
q=nH*(1-h)^2*k, R=nH*q,
c=(1,0,0,-chi,0,0,0)^T.

chi는 binding energy이며 kB*B가 아니다. no extra1/2. q는s^-1, R은cm^-3s^-1, c는 stoichiometric vector이며 광속표기와 무관하다. 유효 population simplex, nH>0를 요구한다.

## A. 연속 해의 유일성과 BE 다중해

H=0인 HH-only에서 x=h-h0,W=1-h0,E=u0/(chi*nH),0<d<min(W,E)를 둔다. x< E, x<=W가 양의 열에너지/인구수 조건이다. cutoff 양쪽에서 q(x)>0이고 locally bounded이며 cutoff 근처 양의 하한을 갖는다.

시간 좌표 t(x)-t0=integral_0^x dxi/q(xi)는 연속이고 엄격히 증가한다. 그 역함수는 절대연속이고 xdot=q(x)를 거의 모든 시간에서 만족한다. 역으로 임의의 절대연속 해에 이 시간좌표를 합성하면 도함수가1이므로 같은 해다. 따라서 cutoff 횡단을 포함한 양의 온도 domain의 연속 해는 유일하다. 수치 quadrature/history를 실행한 것은 아니다. BE의 두 root와 연속 ODE의 비유일성은 동치가 아니다.

hot branch에서 q 감소를 쓰면 d/q(0)<=tc-t0<=d/qa(d)=tau_a. 추가로 q(0)<qf(d)라면 tau_f<d/q(0)이다. 이 조건에서 cutoff에 도달하기 전 시간에도 cold BE root가 존재할 수 있으므로 endpoint residual만으로 branch history를 고르면 안 된다. 해당 추가조건의 새 수치 평가는 하지 않았다.

## B. raw floor 자체의 유한 열적 수명

cold branch kappa=nH*kf, x(tc)=d에서 정확한 해석식은
x(tc+s)=W-(W-d)/(1+kappa*(W-d)*s).

d<E<W이면 sE=(E-d)/(kappa*(W-d)*(W-E))에 u=0 경계에 도달한다. 금지된 u=0에서 provider를 호출하거나 물리해로 연장하지 않는다. W<=E이면 유한 시간 neutral exhaustion은 없고 W=E의 u=0 접근도 점근적이다.

처음부터 cold인 d=0에서
tflow=E/(kappa*W*(W-E)),
tBE=E/(kappa*(W-E)^2),
tBE-tflow=E^2/(kappa*W*(W-E)^2)>0.

따라서 BE endpoint의 양의 온도만으로 그 시간까지 연속 raw 모델이 양의 온도를 유지한다고 인증할 수 없다. F1C의 고정 진단값 T0=2000K,nH=1cm^-3,h0=0를 계승하면 tflow약1.93794342453093972e18s, tBE약1.97549967169776678e18s다. 실제 우주론 시간 예측/F07domain이 아니며 팽창 경우에 이 정적 식을 대입하지 않는다.

## C. 팽창 guard와 normal speed

HH+단열팽창의 udot=-5Hu-chi*nH*q, epsdot=-2H*epsilon-chi*q.
g=2epsilon-3kB*Tc*Pi,
n^T=(-3kBTc,-3kBTc*r,-6kBTc*r,2,0,0,0),
D=2chi+3kBTc>0, n.c=-D.

양쪽 normal speed는 nu_i=-4H*epsilon-D*q_i다. H>=0,epsilon>0,nH>0,h<1이면 둘 다 음수이며 hot→cold 단일 횡단의 국소 해가 유일하다. actual bracket 전체의 quantitative vmin은 별도 enclosure가 필요하다.

proper좌표 guard는 Su(t,Y)=2u-3kB*Tc*P=nH*g이므로 partial_t Su|Y=9H*kB*Tc*P를 포함해야 한다. dSu/dt=nH*gdot-3H*Su, guard에서 dSu/dt=nH*nu_i다. 명시적 시간항을 누락하면 expansion contribution을 올바른 -4Hu 대신 -10Hu로 얻는다. 빠지는 항은 +6Hu다. 현재 REI에서 관측한 버그가 아니라 새 좌표계의 수학적 경고다.

실제 추가 source를 b라 하고 beta=n.b로 쓰면 nu_a=beta-Dqa,nu_f=beta-Dqf. qf>qa에서 beta<Dqa는 두 음수, beta>Dqf는 두 양수, Dqa<beta<Dqf는 hot양수/cold음수인 repelling 경계다. 이 jump순서에서 attractive sliding 조합은 없다. 등호는 grazing/퇴화다. 실제 광가열·재결합의 beta를 단열값으로 치환하여 transversality를 승인하지 않는다.

## D. 횡단 민감도의 saltation

단일 transverse event, 동일event순서, 교차guard 없음, 충분히 smooth인 branch/guard, identity state reset을 가정한다. nominal time에 맞춰 delta_tc=-n.delta_z_minus/nu_a를 사용하면

S=I+c*(qf-qa)*n^T/nu_a,
delta_z_plus=S*delta_z_minus+O(norm(delta_z)^2).

2차 remainder는 C2 국소조건이며 C1에서는 o(norm(delta_z))로 읽는다. 상태·실제 eventcounter에는 impulse를 추가하지 않는다. 전이시간 변화를 무시한 reset Jacobian I만으로는 민감도가 맞지 않는다. 일반 saltation 식은 Kong etal, arXiv2306.06862v3, DOI10.1109/JPROC.2024.3440211의Eq9/Eq11/Eqs27–29와 일치하며 위 HH대입은 직접 유도다.

S*c=lambda*c, detS=lambda=nu_f/nu_a.
n.v=0인 tangent는 불변이며 ell^T=(chi,0,0,1,0,0,0)에 대해 ell^T*S=ell^T다. 이는 전이 민감도의 회계 관계이며 팽창 중 epsilon+chi*h가 상수라는 뜻은 아니다. 그 smooth도함수는 -2H*epsilon이다.

같은 시간 coordinate Jacobian J=diag(1,1,1,nH,1,1,1)에서 Su_matrix=J*S*J^-1. prescribed density의 partial_t guard를 포함해야 한다. 독립적인 dynamical density/geometry좌표에 이7차원식만 적용하지 않는다. lambda는 특수방향 고유값/행렬식이지 일반 norm/전체history오차 gain이 아니다. 소비자가 고른 positive scale W_s에 대해 norm(S)<=1+abs((qf-qa)/nu_a)*norm(W_s^-1*c)_inf*norm(n^T*W_s)_1이라는 별도 upper bound를 쓸 수 있다.

## E. 조건부 팽창 gain과 event-time budget

HH+단열팽창에서 rho=qf/qa>1, theta=4H*epsilon_c/(D*qf)>=0이면
lambda=(1+theta)/(theta+1/rho), 1<=lambda<=rho.
theta가 증가하면 lambda는 감소한다. 저장 F1C rho enclosure를 exact rational로 운반한 theta=0,0.01,1,10,100의 값은 각각 약3.909876110233189e15,101,2,1.1,1.01이다. 무차원 수학적 조사점이지 소비자 물리domain이 아니다.
1<K<rho이면 lambda<=K iff theta>=(1-K/rho)/(K-1). K를 actual tolerance로 지정하지 않았다. 다른 source의 cancellation/grazing에서는 이 단열 해석이 깨진다.

J_HHdot=q,L_HHdot=-chi*q로 per-H event와열기여를 정의하면 extended jump vector는(c,1,-chi), normal은(n,0,0)이다. h-J_HH와L_HH+chi*J_HH의 covector가 saltation을 통과해 보존된다. 전이를 delta_tc>0만큼 늦춘 source배정의 국소1차 사건오차는 deltaJ=-(qf-qa)*delta_tc, deltaL=+chi*(qf-qa)*delta_tc다. 에너지 상쇄만으로 event위치오차가 작다고 결론낼 수 없다.

전체 단일crossing bracket에서 gdot<=-vmin<0이고 참guard 오차<=epsg가 인증되면 abs(delta_tc)<=epsg/vmin. 동일초기값·공통compacttube·하나의 전이시각차·공통scaled norm의 branch Lipschitz L과 source차 bound M이 확보되면 timing에 의한 state오차<=M*exp(L*duration)*epsg/vmin. 실제 box/tube/source의 인증 없이 수치대입한 것은 certificate가 아니다. full/half1/half2 각각의 사건시각과 same-stage R/nH를 쓰며 accepted two-half는 half1.events+half2.events다.

## 검산과 결론의 상한

proof-only script1회, 기호항등식27개와exactassertion49개 PASS, exit0, stderr0byte. 49개에는16개 constant-field event-alignment 사례의 위치/시간 검사,5개normal부호사례,5개inheritedgain bounds와 관련 exact 부등식 등이 포함된다. constant-field oracle은 실제 HH trajectory가 아니다. 모든 해석적 가정/부등식이 CAS에 의해 자동 증명됐다고 하지 않는다.

신규productiontests/TDD/HHfit/rootfinder/timestepper/consumer/history/NCP/primitive/oldscience replay는0. 제3자 독립과학검토도 없다. 원source는 그대로다. REI raw mirror는container DNS실패로 만들지 못했지만 원문은connector로 읽고 exactcommit/blob와semanticprojection을 남겼다.

HH-F1 WAITING_ON_REI_DOMAIN, HH-F2 NOT_INTEGRATED, physical/production admission=false 유지. 최신REI6279036f의F04 controllednative successor는partial이며certificate_completed=false다. 이번F1D가 그native code를 검증한 것은 아니다. HH-off baseline을 막지 않는다. 실제F07/소비자cutoff정책이 도착하기 전 추가generichelper나toy campaign을 멈추고 이 단위를 닫는다. 전체 증명·원수치·실패기록·후속DAG는START의sealedZIP에 있다.
