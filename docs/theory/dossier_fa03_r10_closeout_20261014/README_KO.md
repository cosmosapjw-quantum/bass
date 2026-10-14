# FA03-R10 종료·재개 및 REI source-threshold 공급 (2026-10-14)

BASS FA03의 **선택된 R10 단계만 종료**한다. 새로운 R1/10단계 사이클은 시작하지 않는다. 부모 PR149 commit `ee0f8a2e86ec70b3ff295c08c083125d774990c8`의 50개 stable equation/claim ID, 본문·Python evaluator와 원 R9 source archive를 보존한다.

## 유지되는 물리 주장
정확한 Kasner (2/3,2/3,-1/3), metric (-,+,+,+), x=t/t_o∈[1/2,1], source·absorber normal rest, zero incoming coherency, observer χ=1/125, ψ=1/100, aperture δ=1/50, positive **GL3×12 36-ray finite detector**, continuous exact band e∈[.98,1.02], real |ε|≤1/10에 한하여

\[
\|\mathcal J_{36}(\epsilon)-\widehat S_0-\epsilon\widehat V_0-\epsilon^2\widehat W_0/2\|_1<4.75\cdot10^{-7},\quad \lambda_{\min}(\mathcal J_{36})>0.12548.
\]

강한 상계는 PR146 interval enclosure와 PR147 original reference의 exact-rational equivalence witness에 의존한다. PR147 단독 numerical radius (<4.84e-7)과 다르다. 연속 각도 cap, χ/ψ 수치 미분의 certificate, finite ε의 완전 six-moment closure, 실제 원자 opacity, cosmological shear/reionization signal은 **HOLD**. 물리 intensity 복원 인자 c*t_o*E_*²*j_*(eplus-eminus)를 한 번만 곱한다. 원 I–VII / 21 nodes / D9.1 / SOURCE_CLOCKS / ABUNDANCE_MODEL 불변.

## 이 루프의 과학적 추가 진단
`code/threshold_support.py`는 pure exact rational count+energy preserving deposit이 이온화 문턱 아래 support를 보존하지 않을 수 있음을 검사한다. Mono23eV<HeI24.59eV에서 20eV/30eV에 (7/10,3/10)을 배분하면 count 1, mean23eV 정확 보존이지만 **문턱 위 노드 가중치 3/10**. Real spectrum이 threshold를 가로지를 때는 `MIXED_SOURCE_SUPPORT_UNRESOLVED`를 반환한다. **이 값 30%는 실제 REI ion fraction/source-rate error가 아니다.**

최근 `bass_cr` PR63의 actual source-weighted sigma discrepancies HI +0.119254%, HeI +10.408540%, HeII +38.594120%는 별도 source-specific numerical evidence다. Chemistry accuracy나 abundance error로 전이하지 않는다. Related C²-Ray Mellema et al. (2006), DOI 10.1016/j.newast.2005.09.004; Friedrich et al. (2012), DOI 10.1111/j.1365-2966.2012.20449.x는 helium edge split/photons method background다.

## 상태, 검증, 원본
새 14 Python tests PASS. R9 nested archive 2,542,568bytes SHA256 `87c923b7bf6689b1791a88f700788570b734deed77ca500bec670ef49b333d43` exact match, original R9 38 payload verifier/13 tests PASS. R10 18 payload verifier PASS, altered-copy rejection PASS. Wolfram15.0.1 exact source counterexample PASS. R10 new xAct invocation failed a script syntax mistake and was NOT promoted. Inherited R9 actual Wolfram15.0.0/xTensor1.3.0 eight zero groups remain pinned and valid. External independent reviewer / native subagent NOT_RUN.

Full 19-member/18-payload immutable archive `BASS_FA03_R10_CLOSEOUT_20261014__71016d559e66.zip`, 2,560,802 bytes, SHA256 `71016d559e6663f18c0977373b233a20b0d1f1d0c66a34f59b83e8b048238024`. Google Drive object 18NOycRFqGMLcZh31QiHNi9bnEa8hr4Vr, Dropbox id:BSpOijBcT10AAAAAAD7J2w, both ACK; actual Drive restoration was SHA verified, Dropbox restoration not independently performed. Original R9 ZIP and private native source stays **only** inside full archive, not public Git.

**R10=COMPLETE_SCOPED, NEXT_FA03_STAGE=NONE**, no new science cycle without explicit task. This PR is draft, no main merge and no active REI mutation.
