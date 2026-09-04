# SciSpace literature lock — R6C

## Question

What scientific-software and reproducible-build practices distinguish source-tree modifications from deterministic build artifacts in parent–candidate differential testing?

## Relevant results

- Lamb and Zacchiroli, *Reproducible Builds: Increasing the Integrity of Software Supply Chains*, IEEE Software, DOI `10.1109/MS.2021.3073045`.
- Dhruv, Dubey, Barba, and Gesing, *Managing Software Provenance to Enhance Reproducibility in Computational Research*, Computing in Science & Engineering, DOI `10.1109/MCSE.2023.3314288`.
- Heroux, *BSSW 4: Improving Reproducibility Through Better Software Practices*, DOI `10.6084/m9.figshare.5593339.v2`.

## Methodological conclusion

The relevant separation is:

```text
immutable source identity
!= build workspace
!= generated artifact
!= installed executable environment
```

A parent–candidate differential is strongest when both source trees remain unchanged and packaging/build products are generated in isolated staging locations with explicit provenance. Merely ignoring an artifact weakens observability; building outside the source worktree preserves both traceability and the cleanliness invariant.

## Project application

R6C therefore exports each pinned Git commit into a non-Git staging directory for PEP-517 installation while retaining the detached worktrees solely for source identity and test execution. The same native wheel, dependency lock, environment variables, and test cone are preserved.

## Authority boundary

The literature supports the execution design only. It does not provide BASS equations, signs, units, hashes, tolerances, source coefficients, or admission decisions.

```text
authority_effect = NONE
```
