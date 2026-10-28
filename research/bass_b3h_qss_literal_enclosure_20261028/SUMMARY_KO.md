# 새 B3h QSS 구간 결과

원 PR212 검토 대기와 별개로, 실제 저장 cut의2x2 정지상태에 대한 새 source-literal 구간을 구성했다. 새 work18/20, 독립 작성자R6/C9미수행, 원 중앙28/88,증가분0. 새로운 nativeODE/B3i/oldcampaign/oldquadrature는0이다.

## 실제 결과
새 dyadic 대표값 q≈(6.56840948242368576490e-15,1.97467235481912766796e-14).

|bits|새 산술 E_QSS 상한|별도 residual 상한|
|---|---|---|
|256|8.72253024064538907165e-76|9.16217826899945739126e-76|
|384|2.56332125568880571551e-114|2.59844859034972245716e-114|
|512|7.53292413851220881073e-153|7.71811888035933963287e-153|

표는 위쪽 표시 반올림이다. 원 exactinteger/rational경계가 우선한다. reset거리≈7.44273725068990090841e-29이며, 조건부 미래Lyalpha count상한은1.25435955941624615156e-22/V0다. 같은모형이라는 추가가정 아래 상속cut오차의 알려진별도기여는2.44144826449726281586e-42/V0. 새대표값 산술반경의 count기여는1.26955918034380560872e-146/V0다. 산술반경이 작아도 실제representedreset차이는 사라지지 않는다.

Wien삭제/JSONfloat의십진수재해석/theta초기화는 nominalq와 각각 약1.31021796264e-19/2.65751148020e-35/1.29146255481e-20의L1차이를 만든다. 이는 source/clock 모형변경 효과이지 물리오차반경이나새trajectorycorrection이아니다.

## 검증과 실패 보존
8개동일시험RED8FAIL→GREEN8PASS; 추가tests-after6/6PASS; primary12/12; 생산모듈을import하지않는Decimal180소거법/정확Fraction227/227,192corners. 별도작성자의독립검토는아니다. 실제정수구간산술은expTaylor양의tail과integer sqrt를사용한다.

새primary CPU0.129553s/reference0.051038s. 알려진child/plotlauncher CPU합4.569435s, wall실측+plot45s보수상한합45.427586483s. 첫실패launcher·준비·원격·모델·delivery비용은unknown이므로end-to-endcap증명은아니다. 새allocation닫힘,옛budget이월0.

첫실패는없는이전Python경로로child가시작되지않은것이다. 현재실행은Python3.13.5였다. 새그림은생성됐지만wrapper가ledgerappend권한오류로exit1; 원파일/로그를확인하고CPUreceipt를복구했으며plot재실행0. 비치명적startupwarning보존,all_runtime_attempts_pass=false.

## 조사 범위와 종료
7repo에서이름에202610을포함하는713branch반환의terminal을확인하고관련새PR원문과부모백업을대조했다. 단일snapshot/모든branch본문/모든대화전문/모든백업원문전수조사는아니다. REC PR142의313x313QSS와 BASS BF1은다른scope로보존했다. SourceZIP과이Git runnableprojection은같은파일집합이라는주장을하지않는다.

E_QSS_old와physical eS/en/eE/geometry/temporal/total/global은null,globalphysicalcompletionnull,L4=false. 원PR212의18/20과합산하지않는다. 중앙/foreign/main변경0,merge0. 다음은고정saved-evidence에대한distinct-author R6/C9 한묶음이며AUTO_NEXT_NODE=false.
