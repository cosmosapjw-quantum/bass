# F04B: 실제 native 반환의 Schur 잔차 연결과 성분별 BE 범위

## 최종 판정

SCOPED_NATIVE_RETURN_SCHUR_BINDING_AND_DT_SENSITIVITY_COMPLETE.

CR_OFF_FASTEST를 유지하면서 F04A의 고정 합성 F03 input과 두 root certificate를 계승했다. 새 결과는 photon elimination 밖의 저장값에서 reduced residual로 전달되는 정확 보정항, 성분별 resolvent posterior, 같은 dt-family의 sensitivity와 좁아진 enclosing tube다. canonical REI-F04 전체, continuous ODE error, accepted two-half, 온도의존 successor 인증은 완료하지 않았다.

시작 bass_cr HEAD=64a0c276ae48c880574c0e112e3ba8b93df543ef. 작업 중 실제 native 반환 c8627ecaf015798ae90f61f4741e17ca6ccd7894를 수신했고, 게시 직전에도 그 HEAD를 확인했다. 원 owner가 이미 수행한 native 관측과 root binding을 재실행하거나 이 스레드의 최초 성과로 주장하지 않는다. 이 문서는 같은 branch의 새 경로이며 원 source/runtime_returns/CODEX_SYNC를 수정하지 않는다.

## 원 source와 native 반환 identity

source commit=c1d7f89c8abc90a6adf971390f2bce7ae7530a23, repo cosmosapjw-quantum/rei_bianchi.
- hhe_events.rs blob57a63eee1e9d8c4aa2b5ed663dbea15619359f71
- microstep.rs blob3a78b40d1823a1e1c8541538bd94481b4cab0277
- thermal.rs blobd43a09450f2b2ed17f7032d4a3aecc3ff3f5d365

Static/proper HHe, 3 photon groups, fixed synthetic alpha/beta/sigma, Case-A escape scope다. receiver c433eaee7b120a5bfb7c35e802c4b218315bf210에서 동일 blobs를 확인했다.

이후 receiver6279036f06c9ba4d47574beab90b48fc2c6f9ba7의 changed paths와 F04_successor/README_KO.md(blob2742c755e114d002bc33b3cf85aac486c9631ac6)를 읽었다. 온도의존 FT03 module/contract/tests와 lib exports가 추가됐지만 위 세 F03 파일은 변경되지 않았다. owner F04는 partial이며 uniform parent/implicit derivatives/half composition/public width는 미인증이다. 새 merged92 tests 등은 보고로 수신했고 재실행·합산하지 않았다. 이번3D/frozen-rate 결과를 successor에 자동 적용하지 않는다.

c8627ec의 research/fastest_track_20261005/f04b_native_binding에서 다음 세 파일 원문을 local에 저장하고 Git blob을 일치시켰다.
- evidence/endpoint_bits.stdout:67afa49635c7b277db0d3a9c9ea124922bab3c02, SHA25677a2c0f914ca2c5db6c27d2b0b5c7bae1d87b6775f30c1d1ec4342d215dbdea4
- export_endpoint.rs:9b89fdd9207642561fd0cfe72b41cbe79ddc994e, SHA256bddc136ae34724f8e318bbcf1ef7f8ba24a8e4607e24148092c6b321c3b4ef08
- evidence/COMMANDS.json:b7f560f94034f9a2f2290e6cee115df6f485e6d8

INPUT_LOCK.json(blob9516c6464fc5e007077cddc485ba21332f4feff2)의 세 source SHA256와 wrapper identity를 읽었고 COMMANDS의 실제 build/run exit0를 수신했다. 원 F03 Rust 전체 bytes와 native executable을 이번 ZIP에 복제하거나 재실행하지 않았다. 이 수신은 전체 cloud archive restore가 아니다.

처음9253ed4 계열 OWNER_NATIVE_RESULT에는 scalar 요약만 있어 old/endpoint bits 부재를 기록했으나 c8627ec 수신으로 그 blocker는 해소됐다. archive 안의 diagnostics/SUMMARY와 native_capture_attempt는 초기 snapshot으로 보존한다. 최종 상태는 root TASK_RETURN.json과 results/NATIVE_RETURN_SUMMARY.json이다.

## 정확 Schur 잔차 전달

x=(xH,xHeII,xHeIII), l=(1-xH,1-xHeII-xHeIII,xHeII), d=(nH,nHe,nHe), s_ag=c*sigma_ag, kappa_g=sum_a d_a*l_a*s_ag, D_g=1+h*kappa_g, Nbar_g=N_g0/D_g.

저장 native candidate를 xhat,Nhat라 두면

    r_x = xhat-x0-h*F(xhat,Nhat)
    r_N = D*Nhat-N0
    M_0g=l0*s0g
    M_1g=l1*s1g-l2*s2g
    M_2g=l2*s2g
    G_h(xhat) = r_x + h*M*D^(-1)*r_N.

고정계수 source에서 정확한 항등식이다. Native photon이 소거식에 정확히 놓이지 않으면 fraction residual만 사용한 posterior가 잘못된다. 기존 F03는 photon residual도 검사하므로 기존 safeguard 누락으로 주장하지 않는다.

fhat를 native stored RHS, f_R을 동일 input bits의 exact-real RHS로 놓으면 r_R=(Delta y-h*fhat)+h*(fhat-f_R). Native scalar residual_norm을 exact residual로 대체하지 않는다. 이 산술 차이는 관측점의 값이며 전체 floating 실행경로의 roundoff enclosure가 아니다.

H_g=sum_a d_a*l_a*s_ag*(E_g-chi_a)*ev, a_R=Rsum/np, D_u=1+h*a_R이면

    uhat-ubar=(r_u+h*H*D^(-1)*r_N)/D_u
    ehat-ebar=r_escape+h*a_R*(uhat-ubar).

exact Schur/thermal/escape 항등식을 source-bound native bits에서 검사했다. 개별 native event rates는 원 CSV에 없어 source arithmetic/event assembly의 그 rate 기반 분해는 null이다. 사건 수를 dt로 나누어 stored rate bits라고 만들지 않았다. 직접 electron+photon inventory defect는 계산했다.

## 반례와 posterior

normalized pureH, nH=1,nHe=0,c*sigmaHI=1,alpha=beta=0,h=1,x0=0,N0=1, candidate xhat=1/2,Nhat=1에서

    fraction residual=0, photon residual=1/2, reduced residual=1/6.

정확 물리 BE root=(3-sqrt5)/2, candidate distance=(sqrt5-2)/2>0이다. photon correction을 빼면 진짜 algebraic error가 숨겨진다는 부정 대조다.

기존 contraction certificate의 E_ij=sup|I-A*DG|_ij와 q=||E||inf<1을 계승한다. candidate와 root가 같은 X 안에 있고 input/dt가 일치할 때

    |xhat-x_*| <= (I-E)^(-1)*|A*G(xhat)|.

증명은 평균값 적분으로 |e|<=w+E|e|를 얻은 뒤 nonnegative Neumann resolvent를 적용하는 것이다. 모든 역행렬·proof comparison은 Fraction이다. 밖의 candidate/다른 model·initial fractions·initial photons·dt는 거절한다.

## 실제 native 결과

대상은 dt=1e8 s의 default StepControl, 반복3회의 단일 full BE 후보이며 adaptive accepted 여부를 판정한 결과가 아니다. 새 exact 결과의 성분별 root 거리 상계는

    HII   1.4758856593968439e-18
    HeII  2.866750739234021e-19
    HeIII 1.0659650356755096e-19.

이는 native float와 exact-real BE root 사이의 posterior이며 연속 ODE 오차가 아니다. 원 owner의 이미 게시된 bound와 마지막 표시 자릿수 차이를 큰 개선으로 주장하지 않는다.

실제 fraction residual은(1.4939777187765333e-18,2.841517344251837e-19,-1.0659876584363343e-19), photon correction은(-1.755406259296918e-20,2.5312406408390523e-21,2.0044610487661774e-24)다. reduced residual은 두 벡터의 정확 합이다.

actual initial u minus F04A exact initialization=-5.467016701323603e-33 erg/cm3, native uhat minus reduced ubar=-1.0073459644151924e-32 erg/cm3. 모두0으로 반올림하지 않았다. 좁힌 root 상자와 actual old.u의 thermal B 하한=2.2673539065754914e-16 erg/cm3>0. exact-real7좌표 scaled residual max=1.1705073952391452e-16, 원 native reported norm=1.1705736578619066e-16이며 후자는 escape 항도 포함하는 source-defined norm이다. 직접 사건 수지 defect=-7.149815835861457e-22 cm^-3.

위 소수들은 display only이며 proof endpoints는 ZIP의 exact rational JSON이다. c,kB,eV-to-erg를 유지하고 모든 h는 초 단위다.

## 같은 dt-family의 민감도와 더 좁은 범위

partial_h Nbar=-N0*kappa/D^2, partial_h G=-F-h*M*partial_h Nbar. 같은 X,H에서 v_i=sup|(A*partial_h G)_i|를 계산하면

    |dx_*/dh| <= (I-E)^(-1)*v.

이는 BE step-size sensitivity이며 physical dx/dt가 아니다. H=[9.9e7,1.01e8]s의 기존 family, h0=1e8s anchor와 원 input을 유지하고 parameter box를 넓히지 않았다. anchor 오차를 더한 결과:

|fraction|sensitivity upper [s^-1]|new enclosing radius|old radius/new radius|
|---|---:|---:|---:|
|HII|3.6063303280724806e-12|3.6063303280727673e-6|2.77290|
|HeII|4.1661191668061087e-13|4.166119166808976e-7|24.0032|
|HeIII|1.7170598988956624e-16|1.7170599017624132e-10|58239.1|

원 cube 반경은 모두1e-5였다. 이는 같은 algebraic family enclosure의 개선이지 우주론적 예측 정확도가58239배 좋아졌다는 뜻이 아니다. 새 root solve/certify 호출과 owner parameter-box 확장은0이다.

고정 rate에서는 partial x_*/partial u0=0, partial u1/partial u0=1/D_u, partial escaped1/partial u0=1-1/D_u다. 이 독립성은 온도의존 FT03에 적용하지 않는다.

## 구현·검증 경계

새 focused tests42 PASS; Python syntax PASS. 첫 Schur2개와 owner CSV parser1개에 assertion RED→GREEN을 기록했고 나머지39개는 tests-after다. 실제 native CSV parser, Schur/thermal/escape, nonnegative resolvent, independent SymPy partial_h differentiation, binary64 decoding과 domain/mismatch 거절, 동일 family tube를 검사했다. 독립 human/agent/proof-assistant review는 없다.

이 채팅의 native runs0, atomic integrations0, old science suites0, new root solves0, cosmological histories0. 원 native producer의 실행/10tests는 재실행하거나42에 합산하지 않았다. 초기 작성한 runtime/export_bits.rs는 rustc 부재로 DRAFT_NOT_COMPILED이며 실제 owner 반환 도착 후 같은 점의 실행은 불필요하다. Runtime env blocker와 프로젝트의 데이터 확보 상태를 분리한다.

## 정본 artifact와 실제 이중백업

파일=BASS_CR_CHAT_F04B_20261005_v1.zip
bytes=1290643
SHA256=1c7a81e061412530ba84ee14ec151aba77d9af69e94751159a5a5a69913672a1
ZIP74 members,73 payload SHA256/CRC local검증.

Drive: success ACK, id1CRkaH1DHrpL7sP6GRgQ9HdxAQUKjWAAC, parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ. Metadata readback에서 이름/size1290643/parent 확인.
Dropbox: completed, id:BSpOijBcT10AAAAAADyQZw, size1290643, modified2026-10-04T16:05:35Z.
Dropbox path=/BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/BASS_CR_CHAT_F04B_20261005_v1.zip

같은 immutable local archive를 두 provider에 create-only 저장했다. R1 UPLOAD_VERIFIED(ID/name/size/path 또는 parent). Remote checksum은 응답에 노출되지 않았고 full restore/독립 remote byte-hash는 하지 않았다. UPLOAD_VERIFIED!=RESTORE_VERIFIED. 이 Git 문서는 summary/sync이며 코드·전체 증명·시험·정확 JSON의 정본은 위 ZIP이다.

읽기 순서: TASK_RETURN.json, INTAKE_ACK.json, SOURCE_BINDING.json, REPORT_KO.md, results/NATIVE_RETURN_SUMMARY.json, 필요시 exact JSON. diagnostics/SUMMARY의 초기 missing-bits 상태를 최종으로 읽지 않는다. local native attempt의 실패 기록은 보존하되 resolved native data blocker로 오독하지 않는다.

## 다음 노드와 유지 상태

BASS-CR-CHAT-F04C_TEMPERATURE_COUPLED_RESIDUAL_SCOPE_AND_OWNER_BOX_INTAKE.

다음에는 실제 ft03_controlled.rs/ft03_rates.rs/ft03_successor_binding.json과 REI-F04 원 parent 범위를 읽고 thermal coupling을 남긴 residual 및 photon elimination 조건을 유도한다. 새 source를 읽기 전3D 인증을 붙이지 않는다. owner가 선택한 box가 없으면 형식 유도·항등식·부호 검산을 진행하되 uniform proof를 주장하지 않는다. accepted half1→half2 initial-box 전달과 사건 binding도 별도다. 같은 native probe·42tests·기존 cube 인증·과거 suite를 반복하지 않는다.

CR_OFF_FASTEST; precision atomic PARKED. G02=UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN,b_grid=NO_GO. 기존 S-only window bounds5.599633283869504e-17 및7.49726779045559e-17 ta^-1 상속. CR-F0=WAIT_FOR_ACTUAL_CR_OFF_DISPATCH_BINDING, source/loader/callback관측=null. CR-on/full-K/R4AQ/318patch/소비된 승인 재사용 없음. 본 보조 결과를 canonical REI-F04 종료나 새 mandatory gate로 만들지 않는다.
