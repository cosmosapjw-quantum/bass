# PR170 Codex/NCP 선택형 후속 실행 지시문 (현재 연구에서 NCP 불필요)

사용자에게 파일 다운로드, 사전 터미널 명령, 수동 업로드를 요구하지 않는다. GitHub `cosmosapjw-quantum/bass` 최신 PR170의 `research/bass_pr170_photon_age_20261016/` 소스·DAG·원본 PR169 기준물을 직접 읽는다. 먼저 branch HEAD와 Git blob/source SHA를 검증한다. 연결된 native REI `rei_bianchi` PR159/167/170/173 및 최신 PR의 상태·owner chemistry ledgers를 읽는다.

**우선 다음을 검증:** PR170은 비틀림·틸트 없는 LRS, 생후 등방 massless collisionless 광자 `rho,DeltaP`만을 계산한다. Photon number, spectrum, Verner threshold, Thomson, gas energy/momentum 및 donor recoil은 미포함. BASS PR169의 gamma old lane은 원래 Ωr를 신생 재고로 더하는 것이 아니라 정해진 fraction을 초기 collisionless old photon으로 재해석하는 선형 실험. `S(x)` 자료는 비실제 양의 manufactured bolometric density per `d ln a`; 실제 REI `source.at_redshift` per-H/per-s를 사용하려면 photon energy spectrum와 proper n_H, H(x)와 anisotropy angular emission weighting 등 물리적 단위·방출시각을 독립 원본에서 확인하고 matched identity를 만들 것.

**NCP가 정말 필요한 경우만:** 원격 user Ubuntu에서 인가된 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`를 직접 사용한다. 먼저 `ps`, existing REI owner checkpoints/jobs, disk, source SHA, rustc/cargo versions를 점검하고 중복 작업을 금지한다. 개별 새 검증에 CPU 최대16, RAM16GiB, disk4GiB, wall1800s 자원 상한을 유지한다.

BASS 독립 브랜치와 REI owner 브랜치를 분리한다. `rho`/`DeltaP`가 고정-b passive diagnostic인지 Einstein source replacement인지 명시하고 **기존 Ωr/H² massive stress 이중계수**를 금지한다. 새 physical photon emission/recoil partner, isotope-resolved H/He reaction Q^a, positive stock and redshift/shear work, source-bound restart and same-clock convergences를 native에 별도 구현한다. Actual native source/code/test/exit/failures/ledger/residual/benchmark 확보 전에는 EoR admission HOLD. End with fresh Draft PR, Git bundle and create-only Dropbox+Google Drive SHA readback when authorized. Full status and `RETURN_TO_CHATGPT.json` posted. No auto merge.
