# Reproduce source-exact HI photoionization and heat

Data/authority: BASS PR321 immutable parent plus original REI-F08 S0 photon checkpoint, original material histories and Verner HI atomic provider. Code is additive on isolated BASS Draft PR323.

Commands from repo root:
python3 research/bass_rei_f08_s0_characteristic_photoheating_20261101/source_exact_photoheat.py --out /tmp/bass_s0_cold --births 512 --simpson 48
python3 -m unittest discover -s research/bass_rei_f08_s0_characteristic_photoheating_20261101/tests -v
python3 -O -m unittest discover -s research/bass_rei_f08_s0_characteristic_photoheating_20261101/tests -v
python3 research/bass_rei_f08_s0_characteristic_photoheating_20261101/audit_source_physics.py

The audit reads the checked-in physical outputs under results/. It writes one derived source energy-response file. The cold output is not accepted unless original-source hashes, 3900 source-conditional data records, physical number/energy/cross-section invariants and numerical comparison PASS. No original H/He IVP rerun; no observable CMB or actual x_HII prediction.
