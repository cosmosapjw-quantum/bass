# CE1-O S0: exact MPFR NaN proof-premise counterexample

**Source:** PR254 pinned HEAD `8a56d15947435fe7dd83cc1b11347c145136321c`, original `einstein_interval.py` Git blob `e3a5b83183bfad45bbf38c3c3de89de72fe3adce`. Parent and main untouched, CE1 PARTIAL, upper DAG **9/15**, 21 edges.

**Reproduced P1 direct certification defect:** `Interval.decimal("nan")` is accepted, `Interval([nan,nan]).contains(0)==True`, `Interval([nan,nan]).is_nonnegative()==True` due to raw MPFR unordered compare returning an integer 0. `Interval.decimal("Inf")` and `Interval.decimal("-Inf")` are also accepted despite the finite interval contract. Original new tests: **8 FAIL + 5 PASS, exit1**. Production physical six-cell ref8 is unchanged and not disproved; this is lower-level malformed interval input.

**Current-turn verified runtime:** Python 3.13.5 `PYTHON_PASS`, g++14.2 `CPP_PASS`, libmpfr.so.6 present; C header `mpfr.h` missing, so the next bounded C ABI oracle will use an explicit x86_64 LP64 struct layout and `-l:libmpfr.so.6` with layout assertions. Native subagent tool absent `NOT_RUN`. No distinct human-author reviewer or formal program proof.

**Minimal next step:** use `mpfr_number_p` on both endpoints, fail closed on NaN/Inf in the decimal constructor; independent standalone C oracle versus Python ctypes exact 192-bit directed operations, rational/mpmath checks, same source and time/physical/tolerance contracts.

**S0 immutable ZIP:** `BASS_CE1O_S0_20261029.zip`, **2,964 bytes**, **3 members**, CRC PASS, SHA256 `c2c1b457b80899fed8de70f27a7e5fe872ed08d1ce6d097baf6b961a5d6199b6`. No merge/production. S0 Git, Drive and Dropbox receipts follow separately.
