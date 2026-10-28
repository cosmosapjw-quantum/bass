# 동시 CE1-F 구현 PR238/239 대조

작업선은 PR239/research/bass-ce1f-tabulated-angular-certificate-20261029다. 마감 중 발견한 PR238/research/bass-ce1f-tabulated-meanray-implementation-20261029는 우리 C4(a3ddc5ed49d245e87fe393ec17e889dbc77f540d)에서 분기했다. 상대 HEAD0286dd0a97f512a2dc6f431e462e64bd65267047, source SHA2568191ad0035b8683570200f6258351f444e105e3e26cd5d8c4829d26ebc23c53f. 두 PR은 같은 물리적 centered-cell 구성을 공유하며 API와 데이터 의미가 다르다. 자동 merge나 다른 branch 수정은 하지 않았다.

동일 물리 입력의 exact binary fractions를 상대의 rational-string API에 전달했다. f1/2/4/8,각16개 상태에서 압력 차이 최대1.1102230246e-16이고 각 압력·기하 상계가 가까웠다. 이는 수치적 일치 검사이며 보편 인증 증명을 대체하지 않는다. 상대 nominal E=4/5와 이번 E≈.9 입력의 f8 목표 판정을 서로 비교하지 않는다.

추가 독립 리뷰의 확인된 구현/증명 전제 문제: 상대 geometry의 Emax는max(Econt.upper,float energy0)다. 한 셀 exact decimal0.9와 exact binary0.9 사례에서 정확 저장광선 norm²>1 때문에 E_Q(0)-Emax가 MPFR192로[1.2092281458331372e-16,1.2092281458331375e-16]에 놓였다. 따라서 E_Q<=Emax라는 해당 증명 전제는 이 입력에서 성립하지 않는다. 최소 교정은 정확 이산 초기 에너지의 외향 상한도 Emax에 넣는 것이다. 우리 모듈은 이미 이를 수행한다. 이 지적은 상대 최종geometry상계의실제위반이나새물리배제정리가 아니다. 해당 입력의 직접 압력 인증은 별도로 통과했다.

실제 source,재현가능compare.py,원자료,SIBLING_238_REVIEW.md를 provenance/sibling238에 보존했다. 상대 maxcomp nearest-conversion의 별도 증명 세부사항은 관측된 underbound로 승격하지 않았다. 우리의 source/test hash와 기존 C9 판정은 유지했다. 상위노드 완료 추가0,원래9/15; 이론/코딩20단계는 STAGES.md에 있다.
