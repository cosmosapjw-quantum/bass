# BASS→REI IGM S0 original spectral-support physical science

## 실제 물리 결과
원본 REI-F08의 13.7 eV 단색 광자원, Bianchi I/FLRW 원본 H_i, 16,000개 실제 proper-time 구간, 128개 원본 q 방향, 17개 원본 energy nodes 및 원본 Verner96 H I 원자단면적을 사용했다. 원본 두 V1 최종 photon checkpoints의 총 4,352개 에너지-각도 photon weights 및 256개 guard weights도 직접 읽었다. 원본 원시 자료는 변경하지 않았다.

**첫 간격의 구성적 물리 반례:** 정확한 13.7 eV source null propagation의 첫 시각 물리 에너지 하한은 13.699913519 eV인데 원본 hat interpolation은 13.675 eV 노드에 초기 광자수 0.00017124946478640907/H를 재배분한다. 이 연산은 광자수와 평균 에너지를 보존하지만 물리적 frequency support는 즉시 보존하지 않는다.

**원본 최종 checkpoint:** S0_BI total N=0.050070816545420574/H, U=0.6419113223206975 eV/H. 정확한 물리 하한 12.383882550536338 eV 아래 이산 에너지 노드+guard 가중치는 0.011730393740032726/H (23.427606%). 10eV 아래 guard=0.0010016543797005874/H (2.000475%). S0_FLRW의 below-support fraction=23.427273%, 문제를 이방 전단 한정으로 돌릴 수 없다.

**16,000-step original hat replay with original H/He medium:**
| BI final t=1e13 proper s | Original native F08 V1 | Same fixed-grid original hat, frozen original H I | Passive original hat, no absorption |
|---|---:|---:|---:|
| Photon count /H | 0.050070816545420574 | 0.05008021641368748 | 0.09999999999999508 |
| Fraction below exact physical min | 0.23427606237241555 | 0.23429788178772085 | 0.2708481094845208 |
| <10eV guard /H | 0.0010016543797005874 | 0.0010017367237961723 | 0.0023737558440779377 |
| Photon energy eV/H | 0.6419113223206975 | 0.6420289023940952 | 1.2716798038496924 |

가스와 원래 MPRK/SDIRK thermal root는 frozen original F08 H/He trajectory로 제한되어 original full source-owner replay가 아니다. 따라서 원본 총 광자수 근접 재현(+0.018773%)은 원래 spectral support 오류의 생성 메커니즘을 강하게 뒷받침하지만 기존 6.13% photon-count 차이 전체의 유일한 원인이라고 단정하지 않는다.

## 실제 생성 데이터 및 검증
- 60개 원본 proper-time/mode/geometry history records, SHA256 8ea84799078c4276701e3033ffdd372102e268436fb48c7be5968b0ef86966b9.
- 108개 original/frozen/passive discrete spectral energy records, SHA256 a50a27a95b6af89c6de301565c5ea3491dd11fc160ffd88266d61473c86c6401.
- 768개 original/frozen/passive actual q direction resolved support records, SHA256 6aaaf330ea4a28e9d106266c109e0716eb0eca02ca04897d560d40efbf81b8c7.
- Full original source origin: four V1 checkpoint/header raw SHA256 plus parent PR317 original S0 H/He and atomic source 12/12 SHA256; different byte-identity and physics-equivalence claims are kept separate.
- 18/18 normal and 18/18 optimized physical tests PASS: original checkpoint/charge/proper-clock SHA, generic original hat equality, first-step energy-support counterexample, photon number/energy moment and passive conservation, original Verner cutoff, frozen source-vs-original support comparison, all 936 output rows.
- Independent pure-stdlib adversarial code separately parsed original photon bit patterns and checked first-step fake-support and the 23.43% final support violation. Original math.sqrt vs NumPy first-step summation differs by 4.28e-16 photons/H, so independent calculation acceptance uses a justified absolute 1e-15 bound, not physical error tolerance relaxation.
- Passive model photon number final=0.1/H and cumulative 16k-step number ledger errors ≤8.27e-14 photons/H, per-remap mean energy error ≤6.66e-16 eV/H.

## Drift watchdog and claim ceiling
이 작업은 기존 PR319의 관측 sky 확장이 아니라 **원본 F08 photon transport의 source-equivalence 문제를 원본 checkpoint와 실제 remapping 연산자 수준에서 특정한 물리 연구**다. 원래 photon source/observer geometry/atomic owner는 잠겨 있고, 원본 REI H/He/thermal solver 및 acceptance worker는 변경되지 않았다. 사용자 중앙 DAG: 28/88 canonical reported +0, 33/88 Working non-additive, 4/7 Physical Fast; BASS upper 9/15 scoped/source mapped, fully completed +0. F05 원본 tick160→161 아직 미수용; F09 atomic provider source-domain blocker; F08 scientific admission HOLD. Same-author self-hostile audit only, distinct-author blind referee NOT_RUN. No production merge, no tolerance relaxation, no new unrelated sky atlas.

다음 중앙 물리 작업은 BASS가 도출한 source-support-preserving characteristic energy representation을 실제 REI source owner가 채택/거부할 수 있게 정확한 물리 계약을 제공하는 것 또는 F05/F09 실제 blocker 해소다. 승인 없이 original F08 photon owner의 discrete state를 교체하면 안 된다.

## Source preservation and draft
Single BASS Draft PR #321 stacked on immutable PR317 HEAD 18e6273f28ea67e472c919de86594f70fd1c81c9. Source-inclusive 35-member archive /home/cosmosapjw/archives/BASS_REI_F08_S0_ORIGINAL_HAT_SUPPORT_20261101.zip has 6480646 bytes and SHA256 530370df21fd40e57165bd0882c17c25f684d571788c5c2db70f2c3105a48cfb. Independent extracted run verified ZIP CRC, original checkpoint SHA4/4, parent S0 source SHA12/12, 18/18 standard and optimized, independent stdlib audit and byte-exact recompute of 60+108+768 physical records. Final-head GitHub CI remains pending until live readback. Original production and REI source owner are unmodified.
