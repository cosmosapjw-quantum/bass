# 최신 백업·대화 조사

관측 시각: 2026-10-21 15:15:47 UTC. 상세 파일·범위·해시는 `INTAKE_SUMMARY.json`에 있다.

## 바로 재사용할 결과

- **rec_bianchi HHeLi Stage B**: `/bianchi/rec_bianchi/20261016/REC_REI_HHLI_STAGE_B_20261021.zip`, 205,429 bytes, `id:BSpOijBcT10AAAAAAD_hlQ`, 15:11:37 UTC. Stage A는112,861 bytes,15:02:23 UTC. Git intake가 동일 소스를 회수하므로 여기서는 metadata ACK까지만 확인했다.
- **C21N offgrid4 실제 새 실행**:443KB closeout archive를 단일GET으로 회수하고 크기·Dropbox content hash를 검증했다. 고정 source5ecb8a6c…/REI3b85dedc…; z20→4의 신규4개 collisionless40-state DOP853 trajectory,각101표본,모두COMPLETE. 기존125좌표와합쳐129좌표. H/He/Li 반응망 실행의 근거로 대체하지 않는다.
- **REI D9**:4.58MB delta archive를 실제회수·크기/hash검증했다. 기존175개 history,153epochs,35exactreference를 재사용한 성분별 shear 적분예산이며 새로운IVP/ODE/moment는0이다. 최대scaledresidual1.473444875767401e-6,고정기준2e-5를 통과했다. D8의4개 bracket도 해석이 닫혔다. 다음노드는D10 zero-initial-matter-stress-generation이다.
- **HE32 최적화**:2,024,454-byte P1백업이14:57UTC에 게시됨을 확인했다. 내용판정은 Git intake와연결한다.

## 재사용 가능한 Li 입력

`text/lithium_coefficients.json`에는 Li6/Li7에 공통으로 적용하는 elemental VoronovCI/BadnellRR·DR 행이 있다. isotope-specific 데이터가 아니므로 `ElementalElectronicEquality` 가정을 명시한다. Li전하상태는q0..3,Li6/7각4개다. RR의 하한은q1/2/3에대해10/40/90K,CI의 하한은q0/1/2에대해1/4/5eV다. `FUTURE_LI_COLD_CLOSURE.md`는 coldCI값을 임의외삽하거나0으로두지말고 필요한생성기오차/소스근거를 특정한다. 이 문서의 옛HOLD는 새rec_bianchi구현을 확인한뒤 갱신할 사항이다.

`text/isotope_state.rs`는n,H,D,T,He3,He4의13개전하상태 bookkeeping이며 자체물리율이나IC를 선택하지않는다. 문서의21fixturestates와21-speciesinventory는 서로다르다. 전체21-species결합완료주장은 실제신규solver에 근거해야한다.

본문은 Dropbox extracted text다. 정확한immutable코드bytes로채택할때 Git원본identity를사용한다. 실제ZIP/tarGET두건은별도DOWNLOAD.json에hash가있다.

## 조사 범위

`/BASS_BACKUPS`105개,`/BASS_DERIVATION_DOSSIERS_20260912/bass_cr`46개,`/bianchi/research_backups/rei_bianchi`55개,`/BASS_DERIVATION_DOSSIERS_20260912`3281개(6pages),rec백업폴더49개,rate폴더35개,Dropboxroot454개를직접children기준끝까지열거했다. 이는 모든하위폴더전체파일의recursive전수검사와구별된다. 관련9개검색어결과도보존했다.

PersonalContext는이번에도`Personal context is unavailable for this conversation.`을반환했다. DriveHHELI/REI_D9/C21N_OFFGRID4검색0건,lithium검색5건은10월11–15일문서였으며전역자료부재판정으로쓰지않는다. 다른사용자대화의원문을읽었다고주장할수없다.

## 파일위치

- `selected/BASS_CR_C21N_OFFGRID4_NCP_RETURN_AND_DOCUMENT_CLOSEOUT_20261021T140731Z/…/RESULTS_KO.md`,rawcaseRESULT,analysisSUMMARY.
- `selected/REI_D9_FINAL_DELTA_20261021T141112Z/…/D9_COMPONENT_SHEAR_BUDGET/results/RESULT.json`,THEORY_RESULTS_KO.md,EXECUTION_CONTRACT.md,CONTINUATION_STATUS.md.
- `text/`9개입력/설명; `*_DOWNLOAD.json`2개실제GET검증.
- 원시전체listing은관련없는다른연구파일을포함하므로게시패키지에는`INTAKE_SUMMARY.json`과선택된연구근거만추가한다.
