# CE1-O S1: fixed MPFR NaN interval admission and independently checked x86_64 LP64 ABI

Parent PR254 HEAD `8a56d15947435fe7dd83cc1b11347c145136321c`, original MPFR source Git blob `e3a5b83183bfad45bbf38c3c3de89de72fe3adce`. Child PR256 Draft and isolated; upper DAG **9/15**, CE-1 PARTIAL.

**Implemented:** `mpfr_number_p` C ABI typed ctypes call; `Interval.decimal` rejects native MPFR NaN/±Inf even though `mpfr_set_str` reports syntactic success; `contains`/`is_nonnegative` reject nonfinite internal MPFR endpoint (including overflow/poison). Source Git blob after fix `122d4a87ccd95d462db7eb58ef925f2b18c4ec33`. No source/geometry/EFE/RK4/Hermite/precision/target modification.

**Actual current-turn RED/GREEN:** RED 8 FAIL + 5 PASS, exit1 (direct false `NaN.contains(0)==True`); corrected 39 focused PASS, scoped 13 CE1 modules 127 PASS/30.00s exit0. Five allowed finite-decimal fixtures unchanged. `PYTHON_PASS`, `CPP_PASS`, MPFR 4.2.2.

**Independent standalone C execution:** actual x86_64 LP64 C program compiled `cc -std=c11 -Wall -Wextra -Werror -O2 ... -Wl,-l:libmpfr.so.6`, returned 32-byte MPFR struct and offsets 0,8,16,24 matching Python `ctypes.Structure`; precision 192. C vs ctypes **260** binary and **250** transcendental directed interval endpoints exact float identity. Also **260** exact rational inclusions, **250** independent mpmath 120-digit inclusions and seven nonfinite rejection checks. Output `PASS_CROSS_LANGUAGE_CONDITIONAL`. Both call libmpfr.so.6, which remains a shared trust root: this is not formal verification of MPFR, CPython, C compiler, parallel sources or all possible inputs.

**S1 backup:** `BASS_CE1O_S1_20261029.zip`, 25,887 bytes, 11 members; SHA-256 `65d57d9bef45d81e2b51c7f503da84fab0dcd965cabd7204e12da1089c1bc959`, ZIP CRC and 10/10 payload SHA manifest PASS. ZIP contains S0 original checkpoint, implementation, test, C oracle, driver, primary logs and report. S1 Git/Drive/Dropbox receipt to be verified, then S2 final.
