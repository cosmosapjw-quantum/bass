"""Decimal70 metadata arithmetic only on saved output; no scientific integration."""
from pathlib import Path
from decimal import Decimal, localcontext
import hashlib
import json
import resource
import time
ROOT=Path(__file__).resolve().parents[1]
before=resource.getrusage(resource.RUSAGE_SELF);start=time.monotonic()
p=ROOT/'results/TUBE_RESULT.json';raw=json.loads(p.read_text())
with localcontext() as ctx:
    ctx.prec=70
    comparison={}
    for key in ['N_in_m3','U0_J_m3','proper_duration_s']:
        primary=Decimal.from_float(raw['primary'][key]);reference=Decimal(raw['independent_reference'][key])
        difference=primary-reference
        comparison[key]=dict(primary_exact_binary64_decimal=str(primary),saved_reference_decimal=str(reference),
            signed_absolute_difference=str(difference),signed_relative_difference=str(difference/reference))
    U=Decimal.from_float(raw['primary']['U0_J_m3'])
    E=Decimal.from_float(raw['representation']['E21_J'])
    N=Decimal.from_float(raw['primary']['N_in_m3'])
    direct=Decimal.from_float(raw['primary']['crossing_redshift_work_J_m3'])
    subtraction=Decimal.from_float(raw['crossing_work_subtraction_check_J_m3'])
    crossing=dict(direct_positive_W_loss_J_m3=str(direct),signed_crossing_radiation_change_J_m3=str(-direct),
        binary64_subtraction_W_loss_J_m3=str(subtraction),
        subtraction_minus_direct_J_m3=str(subtraction-direct),subtraction_minus_direct_relative_to_work=str((subtraction-direct)/direct),
        decimal_subtraction_of_represented_U_minus_EN_J_m3=str(U-E*N),
        full_shell_left_to_right_signed_change_J_m3=str(Decimal.from_float(raw['transport']['signed_propagation_energy_change_per_V0_J_m3'])),
        distinction='Crossing change compares pulled-back pre-line inventory with photons at their individual arrival faces. Full-shell change transports the entire uncollided shell from the left reference to the right reference. Neither is atomic heat or recoil.')
after=resource.getrusage(resource.RUSAGE_SELF)
out=dict(kind='saved_output_only_decimal70_metadata_arithmetic',source_output_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
    source_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    command='python code/saved_output_detail.py',working_directory=str(ROOT),decimal_precision=70,comparison=comparison,crossing_work=crossing,
    measured_arithmetic_cpu_s=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,measured_arithmetic_wall_s=time.monotonic()-start,
    metering_scope='in-process metadata arithmetic only; interpreter/import startup and output serialization excluded; outside scientific child guard',
    scientific_integrations_rerun=False,frozen_main_raw_modified=False)
(ROOT/'results/NUMERICAL_COMPARISON_DETAIL.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(json.dumps(out,indent=2))
