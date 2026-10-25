"""Native scalar convention and typed finite-donor readiness, no transaction."""
from dataclasses import dataclass,asdict
import math


@dataclass(frozen=True)
class DonorBinding:
    source_query_owner: str | None = None
    source_identity: str | None = None
    species_state_isotope_mapping: str | None = None
    frame: str | None = None
    proper_clock: str | None = None
    spectral_support: str | None = None
    angular_support: str | None = None
    time_support: str | None = None
    donor_inventory: str | None = None
    donor_measure: str | None = None
    donor_cells_to_incoming_face: str | None = None
    volume_convention: str | None = None
    atomic_energy_recoil_owner: str | None = None
    physical_error_radii: dict | None = None
    evidence_class: str = 'ACTUAL_SOURCE_ONLY'


RADIUS_FIELDS=('source','donor_inventory','angular','spectral','geometry','energy_recoil')


def finite_donor_readiness(binding: DonorBinding):
    if not isinstance(binding,DonorBinding): raise TypeError('DonorBinding metadata required')
    record=asdict(binding)
    fields=[k for k in record if k not in ('physical_error_radii','evidence_class')]
    for key in fields:
        if record[key] is not None and (not isinstance(record[key],str) or not record[key].strip()):
            raise ValueError('nonempty owned metadata required: '+key)
    missing=[k for k in fields if record[k] is None]
    radii=binding.physical_error_radii
    if radii is not None:
        if not isinstance(radii,dict): raise ValueError('physical radii must be a mapping')
        for key,value in radii.items():
            if value is not None and (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0):
                raise ValueError('nonnegative finite radius or null required: '+key)
    missing_radii=[k for k in RADIUS_FIELDS if radii is None or radii.get(k) is None]
    structural=not missing
    return dict(metadata=record,missing_structural_fields=missing,missing_physical_radius_fields=missing_radii,
        missing_structural_reasons={k:(
            'Finite donor frame must be explicitly bound to the known native local non-tilted tetrad' if k=='frame' else
            'Finite donor proper clock must be explicitly bound to known native proper seconds' if k=='proper_clock' else
            'Selected finite donor/source binding does not supply '+k) for k in missing},
        structural_model_readiness='READY_CONDITIONAL_ON_DECLARED_MODEL' if structural else 'INPUT_DEPENDENT',
        uncertainty_certification='COMPLETE_SUPPLIED_RADII' if not missing_radii else 'INPUT_ERROR_UNSPECIFIED',
        input_candidate_ready=structural and binding.evidence_class=='ACTUAL_BOUND_FINITE_DONOR',
        physical_finite_absorption=False,
        transaction_executed=False,synthetic_metadata=binding.evidence_class.startswith('SYNTHETIC'))


def native_source_binding(state,facts,history):
    meta=state['meta']; TR=float(meta['TR_eV_rescaled'])
    # Native hydrogen.h E21 and unmodified eV-temperature convention.
    E21=10.198714553953742
    departure=float(meta['Dfplus_Lya']); ratio=E21/TR
    source_identity=state['head']+':'+state['source_git_blob_sha1']
    readiness=finite_donor_readiness(DonorBinding(
        source_query_owner='REC_LINE02_NATIVE_DIRECT_Trr[1,1]+=r_sr[1]+=r*b',
        source_identity=source_identity,
        species_state_isotope_mapping='effective hydrogen collapsed 2p/1s; no isotope-resolved inference',
        physical_error_radii=None))
    records=history['records']
    if len(records)!=313: raise ValueError('expected exactly 313 reused REC owner query rows')
    return dict(schema='B3H_NATIVE_SCALAR_BINDING_V1',native_departure_Dfplus_Lya=departure,
        source_reference_frame='LOCAL_NON_TILTED_MATTER_TETRAD',source_reference_clock='PROPER_SECONDS',
        native_departure_original_decimal=meta['Dfplus_Lya'],native_source_identity=source_identity,
        native_reference=dict(law='WIEN',occupation=math.exp(-ratio),E21_eV=E21,TR_eV=TR,
            units='native eV temperature; no extra k_B'),
        native_total_occupation_Wien=math.exp(-ratio)+departure,
        standalone_LINE01_total_occupation_Planck=1/math.expm1(ratio)+departure,
        conventions_interchangeable=False,selected_fplus_equals_cell_average=False,
        native_constants=facts['constants'],modern_constant_delta_interpretation='SOURCE_MODEL_CHANGE_NOT_ROUNDOFF',
        direct_owner_scope=['Trr[1,1]+=r','sr[1]+=r*b'],
        existing_instantaneous_ledger=facts['native_line_components_decimal70'],
        native_partition_source_head=facts['source_head'],
        history_owner_reuse=dict(status=history['status'],query_count=len(records),
            physical_epsilon=history['physical_epsilon'],normalized_max_error=history['normalized_max_error'],
            query_rows=records,payload=history['payload'],recomputed_queries=0),
        finite_donor_readiness=readiness,source_energy_physical_radius=None,
        new_native_source_transactions=0,new_native_runs=0)
