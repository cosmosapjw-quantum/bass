# 전체 중앙 DAG와 BASS 현재 위치

현재 source: rei_bianchi a28ba343bb85addf1a7e9e58e75816ed3b75cd3b, DAG blob1dff0d1770815c6a9a19ccb828c02ebff29c0e8f. Exact current copy: provenance/current_refresh/CENTRAL_DAG.json. 7authorities/40nodes/17integrationedges. 중앙 파일을 변경하지 않았다.

아래 plan_status는 원본 planning 필드 그대로다. observed 상태는 원본에 별도 기록된 scoped 관측이며 parent전체 completion과 같지 않다. 표에 관측 없음은 해당필드부재를 뜻하며 실제후속작업미실행의 증명이 아니다. 최신 owner PR/대화의 추가 관측은 REPORT_KO.md 및 intake와 current_refresh에 있다. 특히 중앙의 BASS PROPOSED는 이미 수행한 B1/B2/B3a–B3e scoped owner evidence를 취소하지 않는다.

Local depth는 같은 중앙node의 명시된 local_dependencies만 따른 단계수다. 깊이0의 여러 노드는 독립 준비가 가능하다. 아래 integration edges는 해당condition을 선택할 때 추가되는 의무이며 모든 pilot에 무조건 적용되는 장벽이 아니다. 전체물리완성도=null; node수나 이번20활동을 전체가중완성도로 환산하지 않는다.

## 40개 노드의 local dependency 순서

| Repo | Node | Local depth | Plan status | 원본 observed status | Local prerequisites |
|---|---|---:|---|---|---|
| WU088_HH | WU_CE83_OWNER_COMPLETION | 0 | PROPOSED | REUSED_COMPLETE_SCOPED | — |
| WU088_HH | WU_LI_SOURCE_UNCERTAINTY | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| WU088_HH | WU_HE_LI_CX_STATE_ENERGY | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| WU088_HH | WU_D_PI_RR_MATCHED | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| WU088_HH | WU_NUCLEAR_PARTICLE_OWNERSHIP | 0 | PROPOSED | PARTIAL_CONDITIONAL_BARE_CHILD_COMPLETE | — |
| WU088_HH | WU_SPECTRAL_GEOMETRY_COUPLING | 1 | PROPOSED | 해당 관측 필드 없음 | WU_CE83_OWNER_COMPLETION; WU_HE_LI_CX_STATE_ENERGY; WU_D_PI_RR_MATCHED; WU_NUCLEAR_PARTICLE_OWNERSHIP |
| bass_cr | CR_N4_C23B_CUTOFF_BINDING | 0 | COMPLETE_SCOPED | COMPLETE_SCOPED | — |
| bass_cr | CR_N4_STOPPING_KERNEL | 1 | PARTIAL | PARTIAL | CR_N4_C23B_CUTOFF_BINDING |
| bass_cr | CR_N5_ATOMIC_ISOTOPE_COVERAGE | 0 | PARTIAL | COMPLETE_SCOPED | — |
| bass_cr | CR_N6_CONSERVATIVE_COUPLING | 2 | PROPOSED | 해당 관측 필드 없음 | CR_N4_STOPPING_KERNEL; CR_N5_ATOMIC_ISOTOPE_COVERAGE |
| bass_cr | CR_N7_NEW_PARCEL | 3 | PROPOSED | 해당 관측 필드 없음 | CR_N6_CONSERVATIVE_COUPLING |
| bass_cr | CR_BETA_FULL_OWNER | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/rec_bianchi | REC-LINE02 | 0 | OWNER_DELIVERY_PENDING | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/rec_bianchi | REC-HISTORY | 1 | PROPOSED | 해당 관측 필드 없음 | REC-LINE02 |
| cosmosapjw-quantum/rec_bianchi | REC-C3 | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/rec_bianchi | REC-LI | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/rec_bianchi | REC-FIELD | 1 | PROPOSED | 해당 관측 필드 없음 | REC-LINE02 |
| cosmosapjw-quantum/rec_bianchi | REC-COUPLED | 2 | PROPOSED | 해당 관측 필드 없음 | REC-LI; REC-FIELD; REC-HISTORY |
| cosmosapjw-quantum/BASS_HE | HE-X1 | 0 | COMPLETE_SCOPED | COMPLETE_SCOPED | — |
| cosmosapjw-quantum/BASS_HE | HE-ANG | 1 | SOURCE_INPUT_PENDING | SOURCE_INPUT_PENDING | HE-X1 |
| cosmosapjw-quantum/BASS_HE | HE-EXCHANGE | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/BASS_HE | HE-RESERVOIR | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/BASS_HE | HE-CLOSURE | 2 | PROPOSED | 해당 관측 필드 없음 | HE-ANG; HE-EXCHANGE; HE-RESERVOIR |
| cosmosapjw-quantum/BASS_HE | HE-FEEDBACK | 3 | PROPOSED | 해당 관측 필드 없음 | HE-CLOSURE |
| cosmosapjw-quantum/bass | B1-G1B-recover | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/bass | B2-G1B-curved | 1 | PROPOSED | 해당 관측 필드 없음 | B1-G1B-recover |
| cosmosapjw-quantum/bass | B3-fourforce-owner | 2 | PROPOSED | 해당 관측 필드 없음 | B2-G1B-curved |
| cosmosapjw-quantum/bass | B4-production-restart | 3 | PROPOSED | 해당 관측 필드 없음 | B3-fourforce-owner |
| cosmosapjw-quantum/bass | B5-domain-validation | 4 | PROPOSED | 해당 관측 필드 없음 | B2-G1B-curved; B3-fourforce-owner; B4-production-restart |
| cosmosapjw-quantum/vigilode | V1-affine-native | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/vigilode | V2-session-fatal | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/vigilode | V3-affine-quotient | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/vigilode | V4-causal-polynomial | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/vigilode | V5-sphere-production | 1 | PROPOSED | 해당 관측 필드 없음 | V1-affine-native; V2-session-fatal; V4-causal-polynomial |
| cosmosapjw-quantum/rei_bianchi | REI-L0 | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/rei_bianchi | REI-L1 | 1 | PROPOSED | 해당 관측 필드 없음 | REI-L0 |
| cosmosapjw-quantum/rei_bianchi | REI-L2 | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/rei_bianchi | REI-L3 | 0 | PROPOSED | 해당 관측 필드 없음 | — |
| cosmosapjw-quantum/rei_bianchi | REI-L4 | 2 | PROPOSED | 해당 관측 필드 없음 | REI-L0; REI-L1 |
| cosmosapjw-quantum/rei_bianchi | REI-L5 | 3 | PROPOSED | 해당 관측 필드 없음 | REI-L4 |

## 17개 조건부 integration edges

| From → To | 적용 조건 | Claim limit |
|---|---|---|
| HE-X1 → REI-L0 | using angular-moment injection | Necessary PSD/moment-cone gate only; does not supply angular distribution or physical cross section |
| HE-ANG → REI-L3 | selecting anisotropic baryonic scattering transport | Source-qualified angular moments needed; event frequency is not l2 transport |
| HE-EXCHANGE → REI-L3 | selecting finite-mass baryonic pressure exchange | Momentum/energy and pair symmetry from supported physical model |
| HE-CLOSURE → REI-L4 | selecting nonzero baryonic anisotropic stress | Isotropic pi_b=0 minimal pilot does not require this extension |
| CR_N4_STOPPING_KERNEL → REI-L1 | claiming thermalization of supplied fast photoelectrons | Without provider, energy remains explicitly nonthermal; no instant heat |
| CR_N6_CONSERVATIVE_COUPLING → REI-L4 | selecting CR coupled radiation/deposition pathway | Source and gas use same event measure and valid domain |
| WU_D_PI_RR_MATCHED → REI-L1 | claiming isotope-specific D PI/RR number and energy moments | Equal-electronic isotope approximation remains distinct smaller model |
| WU_NUCLEAR_PARTICLE_OWNERSHIP → REI-L2 | activating nuclear daughters/fast products | Branch normalization, charge and energy carriers explicit |
| CR_BETA_FULL_OWNER → REI-L2 | activating source-qualified beta partition and stopping | One beta owner; total Q not all heat |
| REC-LINE02 → REI-L1 | selecting native line source | Consume completed owner result only; active owner reservation remains |
| REC-LINE02 → WU_SPECTRAL_GEOMETRY_COUPLING | selecting native line in WU spectral coupling | One native line owner; no detached/native double counting |
| REC-FIELD → REI-L1 | selecting actual spectral radiation/Compton exchange | Planck and actual-monopole baths remain distinct |
| B3-fourforce-owner → REI-L4 | selecting BASS four-force geometry feedback adapter | Closed sum of sectors in matching frame/clock; signed stresses retained |
| B2-G1B-curved → REI-L5 | claiming curved Bianchi smooth-source domain | Not a prerequisite to all LRS selected flat pilots |
| V1-affine-native → REI-L4 | using native reduced30/full33 affine adaptive client | Actual full physical norm and inherited scales; other validated solvers remain available |
| V2-session-fatal → REI-L4 | using switching/restart driver | Accepted-state transactional semantics and all costs preserved |
| V5-sphere-production → REI-L5 | claiming its physical spherical transport scheme | Joint number/energy remap and source-appropriate stability; not all selected-model pilots |

## 외부·추가 조건

| Node | External dependencies | Conditional dependencies |
|---|---|---|
| REI-L0 | external:ANGTHERM01@6daf382ee698835e7a141378c232d1d97c1c5cf1; external:X1_HE38_ANGULAR_PSD_REVIEW | — |
| REI-L1 | external:BASS_CR_C23B_PHYSICAL_SOURCE; external:WU088_HH_SOURCE_MOMENTS; external:REC_SELECTED_LINE_OR_COMPTON_PROVIDER | — |
| REI-L2 | external:C3_ZERO_TINY_SOURCE; external:LOCALFLOW@9620e1fcc4bdda76e0311206f614234926600381; external:PHYSICAL_BETA_DAUGHTER_AND_STOPPING_PROVIDER | — |
| REI-L3 | external:BASS_HE_FINITE_MASS_TRANSPORT; external:X1_HE38_ANGULAR_PSD_REVIEW; external:BASS_MASSIVE_COMPONENT_MAP | — |
| REI-L4 | external:BASS_GEOMETRY_FEEDBACK; external:VIGILODE_NUMERICAL_HOOKS | {"condition":"nonzero_n_or_T","dependency":"REI-L2","external":false}; {"condition":"anisotropic_baryons","dependency":"REI-L3","external":false}; {"condition":"ANGTHERM02_accuracy_claim","dependency":"external:ANGTHERM02_OWNER_ADMISSION","external":true} |

## 이번 BASS refinement와 다음 실행 위치

기존 B1/B2 scoped receipt → B3a event/state/clock → B3b finite f_plus=0 emission 및 B3b2 INITIAL-DATA bridge → B3c bounded splitting(owner-reported, 재실행0) → B3d coarse angular error → **B3e positive angular selector PASS_SCOPED**.

다음 actual-history branch에는 birth S, R history/map, cohort amplitude, frame/clock/support와 error allocation이 필요하다. Nativefiniteabsorption branch에는 finite receiver trace/cell/face, spectral/angular/time support, finite donor 및 exclusiveatomicowner가 필요하다. 두 branch의 실제 결속과 calibratedREC/geometry 검증 뒤 B4restart/B5general-domain을 검토한다. B4/B5는NOT_RUN, BASS전체physicalcompletion=null이다.

VigilODE D4, REC135, HE100, HH146, CR104 및 REI native-HI 결과는 각각 owner-reported source observation이다. 그들의 scoped20/20 또는 remoteGET성공을 BASS과학실행이나 BASSremoteZIPrestore로 전이하지 않는다.

