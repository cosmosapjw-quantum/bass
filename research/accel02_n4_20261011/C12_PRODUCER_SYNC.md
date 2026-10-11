

### C12R14_ALLOCATION_EXHAUSTED — REI producer progress synchronization

REI result `dc0f3b57cc9a56832c3e7f40e9aee6ac407873a4`의 저장된 producer 상태를 연결합니다. Active run `C2_FULL004`, checkpoint generation 96, 수용 시각 47562328985044.922 s이며 누적 attempts 102 / accepted macros 96 / accepted half boundaries 192입니다. 실제 상태는 `ALLOCATION_EXHAUSTED`, 출력 epoch는 1/129이고 전구간 목표는 40119269418002328 s (mean-volume z15.9→4)입니다. 다음 anchor는 `Q2_FULL_HISTORY_NEXT_ALLOCATION`이며 실행 가능 여부는 HANDOFF의 command_status를 따릅니다.

이 변경은 producer progress 전파입니다. BASS의 새 native receiver/solver 호출은 0이며 새 native admission은 HOLD입니다. 기존 RUN002/N4 및 C11R4 필드와 적용 범위를 보존했고 CR/RCT는 OFF_NONCOMPLETION입니다. 완료된 검산을 반복하지 않았습니다.

실제 백업 receipt: `REI_ACCEL02_C12R14_ALLOCATION_EXHAUSTED_20261011.zip` (173089128 bytes), SHA256 `dd58716cf57195150c7a9df4d92ac9849db77b5303f85168f13be97b10c9693f`; Drive `1tFrY2E_Zka2c5avIeBX6nsb_UYG7OlHU` / Dropbox `id:BSpOijBcT10AAAAAAD4JsQ`. 이 ZIP은 3개 raw byte part로 전송되며 위 Drive/Dropbox ID는 transport manifest입니다. 각 part 해시 확인 후 index 순서로 연결하고 원본 ZIP 해시를 확인해야 합니다. 원격 복원 검증 상태는 `NOT_TESTED`이며 업로드와 구별합니다. [producer STATE](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/dc0f3b57cc9a56832c3e7f40e9aee6ac407873a4/research/accel02_20261011/q1b/c12/STATE.json); 보고서·handoff·원시 증거의 게시 범위는 같은 commit과 PUBLICATION_RECEIPTS/GIT_EVIDENCE_SCOPE를 따릅니다. Keep this PR draft and unmerged.
