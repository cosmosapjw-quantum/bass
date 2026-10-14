# Reproduction and preserved execution

Python with NumPy and mpmath1.3.0 is the observed environment. No network, native chemistry, atomic runtime or production code is required for local checks.

Read-only stored-payload verification:

    python code/verify_package.py

Focused tests and immutable-input replay (write new result/log files only in a copied capsule):

    python -m unittest discover -s code -p 'test_*.py'
    python code/check_certificate.py
    python code/replay_zero_milestones.py

Exact stored-ray assembly without regenerating any reference:

    python code/assemble_certificate.py

For an intentional scientific reproduction, use an isolated copy. Keep the original reference NPZ; it is the fixed approximation under certification. The generator refuses to overwrite it. To reproduce residual generation for that exact fixed approximation:

    python code/certify_moments.py --start 0 --end 36
    python code/assemble_certificate.py
    python code/check_certificate.py

The interval producer uses50decimaldigits and writes one durable ray JSON after each ray. Its complete recorded run covered36rays×64cells. Do not count a repeated producer as independent science review. A separately regenerated RK4 NPZ can differ in ZIP metadata and binary64 arithmetic; it is a new reference requiring a new certificate, not the immutable old bytes.

`evidence/xact_r7.wl` is the exact submitted local Wolfram code. Its Export path was the recorded research-host path; rerunning on another machine requires explicitly changing that output destination and recording the changed script identity. The existing logs are exact downloaded bytes with hash-checked SOURCE_RECEIPT. Cloud CAS is a normalized transcription of actual tool output, not raw transport bytes.

The source-intake archive was restored to this session by the Files connector and exactSHA checked. The new final archive's remote restore status belongs to the detached delivery receipt, not inferred from this earlier source restoration.
