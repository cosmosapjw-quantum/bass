# 최초 실패 보존

1. `bash RUN_GIT_REPLAY.sh`는 exit 1이었다. `prepare_git.py`는 immutable
   compressed input과 `HISTORY.csv`를 성공적으로 검증했으며 36 science tests는
   PASS했다. 종료점은 regenerated `HISTORY.csv` SHA-256 mismatch assertion이다.
   `evidence/REPLAY_NUMERICAL_COMPARISON.json`이 1170-row numerical comparison을
   보존한다. 이는 deterministic generated evidence의 `BYTE_IDENTITY_MISMATCH`다.
2. detached REI PR150 tree에서 처음 `.../rust`에서 cargo를 실행해 Cargo.toml이
   없어서 exit 101이었다. 이후 정확한 `rust/rei_microphysics` root에서 같은
   filtered build는 exit 0, selected tests 0이었다. owner source의 수정은 없다.
3. 독립 검토가 Python control에서 Simpson mean을 transport GL8 mean과 동치로
   취급한 과대 주장을 찾아냈다. GL8/intersection representation과 normal-value
   guards를 추가하고, 9 tests PASS로 회귀를 닫았다.
