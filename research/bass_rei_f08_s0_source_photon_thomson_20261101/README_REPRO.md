# Exact source and science replay

Repo: cosmosapjw-quantum/bass, research branch research/bass-rei-f08-s0-source-photon-thomson-20261101. Owner REI scenario and source are in source_inputs; 12 byte hashes are checked before ANY derived calculation. No dependency beyond Python 3 stdlib for main computation or tests.

From repository root:

python3 research/bass_rei_f08_s0_source_photon_thomson_20261101/s0_source_photon_thomson.py --out /tmp/bass_rei_s0_replay --birth-panels 128 --in-mu 16 --in-phi 32 --simpson 16

python3 -m unittest discover -s research/bass_rei_f08_s0_source_photon_thomson_20261101/tests -v

python3 -O -m unittest discover -s research/bass_rei_f08_s0_source_photon_thomson_20261101/tests -v

Expected science: 4096 source-conditional instantaneous Thomson Stokes sky rows (2 geometries × 4 epochs × 512 outgoing directions) and 1032 emission cohort rows. Original F08 16k actual gas histories H+He, initial+continuous S0 13.7-eV source, original Verner H I owner. Compare results/RESULT.json and both gzipped CSVs by *numerical content* across environments; exact bytes only required/confirmed in a cold same-software-source archive replay. Original photon discretization is NOT identical to this continuum model, so photon-n mismatch is a retained scientific result, not a failed code reproducibility condition.

The source bundle includes original REI atomic_provider.rs, paired_runtime.rs, paired_history.rs as archive source snapshots only; none are compiled or modified by this Python science unit. Source file authority and historical producer binary identity are distinct.
