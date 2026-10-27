# Implementation and execution boundary

The new inverse uses only the stored fin/favg/fout triples and original coefficient inputs. Right x1s, Gamma and tau are accessed only by post-reconstruction validation. Bin273 is primary; the other five bins are retained separately and are not averaged.

`code/inverse.py` implements binary64 monotone bisection, stable series/expm1 evaluation, native background/Gamma arithmetic and population reconstruction. `code/reference.py` is a separate70-digit coth-based inverse and direct net quadrature using exact binary64 integer ratios. Its background treats the source-reproduced native z as a represented input. Native binary64 z and the exact-real affine eta clock remain separate.

The32-ulp trace/coefficient model is an explicitly assumed diagnostic uncertainty model. Its interval calculations are numerical propagation under that model, not directed-rounded end-to-end certification or a physical radius. Exact-stored-input primary/reference errors are separate fields.

The authorized C9 correction propagates incoming/outgoing intervals and the inferred tau interval through A, feq, Gamma*feq-Cp*yp, and division by Cs. It discards correlations conservatively and uses the resulting ys interval width for conditioning qualification. Local interval operations expand their binary64 endpoint results by nextafter; this does not certify the upstream32-ulp assumption or the original source solver.

The exact native convention is x1s=1-xHII. Equality xe=xHII at the known selected snapshot does not redefine that source convention. The endpoint RLya uses the original native prefactor; tau_Lya additionally uses the preserved REC LINE01 diagnostic normalization A_EFFECTIVE=(6.2649e8+2*6.2648e8)/3. That A is not a separately defined constant in original HyRec. The original outgoing Lyalpha closure remains optically thick; the diagnostic is not an inverse input or a new finite-tau evolution.

`code/net.py` computes the signed PL net trace before integrating. It reuses saved incoming totals and70-digit strings; it never replays the completed incoming consume. It copies the original B3g transport implementation into vendor and applies it only to the new outgoing/net measure. The common-volume source integral and its proper-time average have names and units distinct from the endpoint stress tensor. Native direct recoil/heat/ionization zero terms retain their source-model scope.

`code/result.py` emits all12 inverse results, validation/cross-bin diagnostics, endpoint effective-H inventories, the new net photon tensors and QSS ledger distinctions. The native algebraic complement is D; endpoint storage change is ΔNp; the finite balance would require D+ΔNp. No physical reservoir is inferred. B3i calls remain0 because the full physical non-Lyα refill energy owner is absent.

One targeted controls child, one result child and one saved-result plot child are planned, through `code/metered.py controls`, `code/metered.py result`, and `code/metered.py plot`. Guard totals are fresh30CPU seconds/180wall seconds, one thread and512MiB target. Commands are not authorized until S0 publication and both provider ACKs are confirmed by root. No general suite or native source solver is invoked.

The source member `packet_extraction_source.py` is provenance code showing the original incoming/native clock extraction. Runtime computations use only the frozen JSON packets and source constants; re-running that extractor is not a prerequisite or an authorized numerical command.

## 실제 실행 종료와 재현 범위

위의 planned/ACK 대기 문장은 S0 준비 시점의 이력이다. S0 실제 게시 및 Drive/Dropbox ACK 뒤 승인된 C9 보완을 한 번 적용하고 controls/result/saved-only plot을 각 한 번 실행했다. 세 child는 모두 exit0이며 실행 원장은 results/EXECUTION_LEDGER.jsonl이다. 누적 child CPU5.377854초, wall5.460340094초, wrapper CPU0.029728초, peak RSS66076KiB로 닫았다. 추가 과학 실행 권한은0이며 자동 replay하지 않는다.

관측 환경은 Python3.12.14, mpmath1.3.0, numpy2.3.5, matplotlib3.10.8이다. requirements.txt는 이 확인된 버전을 기록한다. 이번 전달을 위해 새 설치나 테스트를 실행하지 않았다. 이미 생성한 결과를 읽는 데 계산을 반복할 필요가 없다.

선택 단위의 재현 계산은 동결한 JSON입력, code, vendor와 위 의존성만 사용한다.35MB원 history를 다시 내려받거나 원 native solver/exporter를 실행할 필요가 없다. inputs/native_source/packet_extraction_source.py는 입력이 추출된 방법을 보존한 provenance이며 현재 재현 실행의 선행조건이 아니다. 원 입력 전체 identity는 packet의 source metadata로 보존한다.
