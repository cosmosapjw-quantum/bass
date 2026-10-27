"""Read admitted saved data only; no previous scientific program imported."""
import hashlib
import json
from mp_b import ROOT,m,exact

SOURCE_A_SHA='179784a094091324dd85ba727fddca1a592178099e9067ff254d6c44c60dd7bd'
PRIOR_FINITE_SHA='a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac'
PACKET_SHA='c335e0273677a55a910b4ff67a1aa47a64834a19bf460b286bfe78404e9cf710'
def read(name,expected=None):
    raw=(ROOT/'inputs/reused'/name).read_bytes()
    if expected and hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('saved input byte identity mismatch '+name)
    return json.loads(raw)
def load():
    a=read('SOURCE_OPERANDS.json',SOURCE_A_SHA);prior=read('FINITE_CHANNEL_RESULT.json',PRIOR_FINITE_SHA);packet=exact(read('NATIVE_QSS_STORED_INPUT_5126_5127.json',PACKET_SHA));tube=read('TUBE_RESULT.json');incoming=read('FINITE_TUBE_INPUT_SLICE.json')
    ops=exact(a['endpoints']);c=exact(a['source_constants']);c.update(energies=packet['energy_eV'],eV_J=m(incoming['native_cosmology']['EV_J']),LYA_FACT=m(incoming['native_cosmology']['LYA_FACT_cm3_inv']),fHe=m(a['source_steady_temperature'][0]['fHe']))
    c['G']=3*m(10**6)*c['LYA_FACT'];c['E21_J']=c['E21']*c['eV_J']
    return dict(source_operands=a,ops=ops,source_packet=packet,incoming_packet=incoming,tube=tube,prior=prior,constants=c,
      initial_prepared_owner=prior['finite_owners'],initial_spectral_owner_reused=prior['finite_owners']['spectral_owner'],
      original_source_hashes=dict(SOURCE_OPERANDS=SOURCE_A_SHA,prior_finite=PRIOR_FINITE_SHA,stored_packet=PACKET_SHA),
      old_scientific_programs_called=0,old_spectral_preparation_calls=0)
