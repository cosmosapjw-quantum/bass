## S11 후속 물리 결과 게시 — 양의 P246, S8 pointwise 수리, 유한-d 반례

완료된 S9/S10과 2026-10-20 원9ZIP 배송을 재사용한 뒤, **새 등방 birth의 고정 support P246 알고리즘**만 별도 연구 단위로 수행했습니다. S9/S10 campaign·기존 native history·ODE·benchmark·NCP 재실행과 새 자동 최적화 cycle은 모두 0회입니다.

### 게시된 단계

| 역할 | Commit / tree |
|---|---|
| C1 계약·현재 Git/cloud/PR175 read-only intake | `e9f8eccc8d86764ebebe9bb98cc68ecb9aad09d8` / `a73917718005524ee32617b58732c65581d7378b` |
| C2–C5 실행 전 source/input | `7fb9b83cba01d37ce4cabbc4772527710601cd96` / `963a43f26df1f9c6f462b9df9a2c34cf99f525c9` |
| C6–C9 원시 결과·그림·독립 readback | `85d5833b4486d14855b84a9d967f5819788d05e5` / `fd3e994212059228501e26f7bf3d3b96462ba1d5` |

실행 source를 먼저 게시했고 18개 source/input의 bytes·SHA256·Git blob을 연결한 뒤 main run을 수행했습니다. 결과 게시 후 전체 tree 3,056항목, 선택한 payload120개, 변경77개, 예상 밖 변경/삭제0, 현재 ref=PR HEAD, Draft/open/unmerged를 확인했습니다.

### 과학 판정

- Main **101/101**: 14개 입력·차수 쌍, 12개 양의 결과, 2개 예상 P6 support infeasibility. 원 exact normalization/P2/P4 gate `3/10^15`를 유지하고 P6도 같은 gate를 사용했습니다.
- Rust 저장 weights의 최대 exact residual `1.0280045769226785e-16`; Python/Rust weight 최대차 `6.938893903907228e-17`. 기존 photons·physical anisotropic stock·birth weights·source frame·reflection·original REI owner를 변경하지 않았습니다.
- 저장된 S8 b9/n64 birth11의 **새 pointwise P24**는 통과했습니다. 과거 `INNER_P2_PRECISION_LIMIT` failed native history와 receipt는 그대로입니다. 같은 support의 P246은 `z_max≈0.619510<5/7`이고 exact facet이 음수여서 거부했습니다.
- S3의 P8 cubic을 재사용하고 P8/P10 quartic을 유도했습니다. 작은 d의 차수는 P24 약2, P246 약3, cubic 제거 뒤 약4입니다.
- **유한-d 개선은 일반화하지 않습니다.** 고정 dyadic7ray의 등록49점에서 최대 angular bias는 P24 `0.02204259946`, P246 `0.03414707019`: **1.54913989382294배 악화**입니다. 구간 supremum이나 full spectral-history 수렴 검증이 아닙니다.
- 별도 새 수학 단위25/25, 독립 수학·응답 readback235/235, provenance/readback152/152를 각각 보존했습니다. 152 감사자는 Rust 작성자이므로 그 독립 범위를 root runner/provenance로 제한했고, 다른 검토자가 frozen Rust core를 별도로 읽었습니다. 원 S10 C9 155/155와 합산하지 않습니다.

[전체 S11 결과](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s11_p246/RESULTS_KO.md) · [기계 판독 ledger](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s11_p246/RESULT_LEDGER.json) · [그림](https://github.com/cosmosapjw-quantum/bass/blob/85d5833b4486d14855b84a9d967f5819788d05e5/research/bass_isotropy_response_20261018/s11_p246/evidence/figure/S11_P246_RESPONSE.png)

### 신규 배송 상태 — 진행 중

C1 ZIP40,857bytes/6payload, C2–C5 ZIP157,012bytes/44payload는 Dropbox 전체 원격 bytes/SHA256/provider hash/CRC/manifest/Git identity를 통과했습니다. 객체는 각각 `id:BSpOijBcT10AAAAAAD_aBg`, `id:BSpOijBcT10AAAAAAD_aBw`입니다. 새 Drive upload 두 시도는 provider 응답 없이 중단되어 성공으로 세지 않았고, 다른 지원 endpoint를 확인 중입니다. 결과 ZIP과 최종 metadata/readback은 후속 배송 댓글이 확정합니다. **기존 S10 원9ZIP·최종JSON 이중 배송은 완료 상태 그대로입니다.**

실제 MD14 donor 정규화/native Einstein·shear shared-Q 결합, evolving reactive full finite-bin spectral history, 더 넓은 angular/finite-d 고차 모멘트, 새 Rust client full birth-memory tangent는 계속 미완료입니다. `5.369926725506957e-12`는 기존 제한된 source-deposition 설명으로 유지합니다. MF2.973/4.115의 workload 한정 결과, closed-small 불확실성과 changing n16/cohort2 `0.9498173837599284` 회귀를 보존합니다. REI production/full EoR/merge로 확대하지 않습니다.

