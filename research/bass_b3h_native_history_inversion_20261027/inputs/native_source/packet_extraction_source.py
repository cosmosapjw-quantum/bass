"""Read saved bytes and extract two-knot native virtual-bin traces. No inverse/solver."""
from pathlib import Path
import csv
import hashlib
import json
import math
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
HISTORY = ROOT / 'intake_rec/source_history.npz'
SNAPSHOT = ROOT / 'intake_rec/research/rec_history_characteristic_resume_20261024/inputs/target_native_snapshot.csv'
ARCHIVE = ROOT / 'intake_rec/HyRec_Oct2012.zip'
SOURCE = 'd6dbe39a4923439547c01695d9020ba39367ea90'
BINS = [273, 272, 267, 268, 269, 309]

def value(x):
    x = float(x)
    return {'decimal': x, 'binary64_hex': x.hex()}

def identity(path):
    b = path.read_bytes()
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
            'git_blob': hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()}

def main():
    hi = identity(HISTORY)
    assert hi['sha256'] == 'd4f82542e13fed4ff0bb60b17865d8b9de5e090a2366108169c3da7a21fcb4b1'
    assert identity(ARCHIVE)['sha256'] == '48cd597519606cdafd0ee6405b781d28467cd323278d16596055a8d0577a1d27'
    hist = np.load(HISTORY, allow_pickle=False)
    rows = list(csv.reader(SNAPSHOT.read_text().splitlines()))
    meta = {r[1]: float(r[2]) for r in rows if r[0] == 'META'}
    virt = {int(r[1]): r for r in rows if r[0] == 'VIRTUAL'}
    with zipfile.ZipFile(ARCHIVE) as z:
        raw_table = z.read('HyRec/two_photon_tables.dat')
        table_lines = raw_table.decode().splitlines()
        member_identities = {n: {'bytes': len(z.read(n)), 'sha256': hashlib.sha256(z.read(n)).hexdigest()}
                             for n in ['HyRec/hydrogen.c', 'HyRec/hydrogen.h', 'HyRec/history.c',
                                       'HyRec/hyrec_params.h', 'HyRec/two_photon_tables.dat', 'HyRec/input.dat']}
    h = float(hist['dlna'])
    zstart = float(hist['z_start'])
    eta0 = -math.log(1.0 + zstart)
    # Source clock only: history.c rec_set_derived_params and rec_build_history.
    izH0 = math.floor(1 + math.log(8.617343e-5 * 2.728 * (1.0 + 8000.0) / 0.4) / h)
    traces = []
    for k in [5126, 5127]:
        native_z = (1.0 + 8000.0) * math.exp(-h * (izH0 + k)) - 1.0
        if k == 5127:
            assert native_z == meta['z'], 'native source clock differs from stored snapshot'
        for b in BINS:
            assert not 100 <= b < 180
            r = virt[b]
            assert float(r[11]) == float(r[12]) == 0.0
            E = float(hist['energy_eV'][b])
            # None of the selected bins is a line-adjacent routing exception.
            source_bin = b + 1
            source_E = float(hist['energy_eV'][source_bin])
            ainv = (1.0 + native_z) * source_E / E
            query = -math.log(ainv)
            position = (query - eta0) / h
            left = math.floor(position)
            alpha = position - left
            assert query < eta0 + h * (k - 1)
            assert 0 <= left < left + 1 < k
            y0 = float(hist['outgoing_virtual'][source_bin, left])
            y1 = float(hist['outgoing_virtual'][source_bin, left + 1])
            incoming = (1.0 - alpha) * y0 + alpha * y1
            avg = float(hist['average_virtual'][b, k])
            outgoing = float(hist['outgoing_virtual'][b, k])
            trace = {'index': k, 'bin': b, 'native_global_index': izH0 + k,
                     'native_z': value(native_z), 'stored_eta': value(hist['eta'][k]),
                     'native_eta_from_z': value(-math.log(1.0 + native_z)),
                     'energy_eV': value(E), 'incoming_derived_from_saved_prefix': value(incoming),
                     'average_stored': value(avg), 'outgoing_stored': value(outgoing),
                     'incoming_witness': {'source_bin': source_bin, 'source_energy_eV': value(source_E),
                         'query_eta': value(query), 'position': value(position), 'indices': [left, left + 1],
                         'fraction': value(alpha), 'stored_values': [value(y0), value(y1)]}}
            if k == 5127:
                trace['right_snapshot_validation_only'] = {
                    'incoming': value(r[3]), 'average': value(r[4]), 'outgoing': value(r[5]),
                    'Dfeq': value(r[6]), 'Dtau': value(r[7]), 'Gamma': value(r[13]),
                    'one_minus_P': value(r[14]), 'incoming_binary64_matches': incoming == float(r[3]),
                    'average_binary64_matches': avg == float(r[4]), 'outgoing_binary64_matches': outgoing == float(r[5])}
            traces.append(trace)
    columns = ['Eb_eV', 'A1s', 'A2s', 'A3s3d', 'A4s4d']
    selected_rows = [{'bin': b, 'literal_row': table_lines[b],
                      'fields': {name: value(v) for name, v in zip(columns, table_lines[b].split())}}
                     for b in BINS]
    p = {'schema': 'BASS_NATIVE_VIRTUAL_TRIPLE_TRACE_INPUT_V1',
         'source_repository': 'cosmosapjw-quantum/rec_bianchi', 'source_commit': SOURCE,
         'source_history_path': 'data/pr05b2_source_history_v060.npz', 'source_history': hi,
         'right_snapshot': {**identity(SNAPSHOT), 'path': 'research/rec_history_characteristic_resume_20261024/inputs/target_native_snapshot.csv'},
         'original_archive': identity(ARCHIVE), 'original_members': member_identities,
         'operation': 'saved-byte extraction and native clock/interpolation arithmetic only; no inverse, native solve, tests, consume or plot',
         'selection': {'primary_bin': 273, 'cross_check_bins': [272, 267, 268, 269, 309],
                       'reason': 'saved right-snapshot moderate positive Dtau, resolved finite jump, all outside diffusion [100,180)',
                       'right_snapshot_role': 'candidate conditioning selection and later validation only; x1s is not an inversion input'},
         'clock': {'izH0': izH0, 'z_start': value(zstart), 'eta0': value(eta0), 'dlna': value(h),
                   'native_z_expression': '(1+ZSTART)*exp(-DLNA*(izH0+index))-1',
                   'interpolation_expression': 'ainv=(1+native_z)*E[b+1]/E[b]; eta_query=-log(ainv); position=(eta_query-eta0)/DLNA; j=floor(position); alpha=position-j; fin=(1-alpha)*out[b+1,j]+alpha*out[b+1,j+1]',
                   'strict_past': 'eta_query < eta0+DLNA*(index-1)',
                   'native_z_and_affine_eta': 'retain both binary64 clocks; do not substitute exp(-stored_eta)-1 for native original operation order'},
         'constants': {'hPc_eV_cm': value(1.239841874331e-4), 'kBoltz_eV_per_K': value(8.617343e-5),
                       'E21_eV': value(10.198714553953742), 'E31_eV': value(12.087365397278509),
                       'E41_eV': value(12.748393192442178), 'E32_eV': value(1.8886508433247664),
                       'E42_eV': value(2.5496786384884356), 'T0_K': value(2.728), 'obh2': value(.021976),
                       'omh2': value(.13), 'okh2': value(0), 'odeh2': value(.343), 'w0': value(-1),
                       'wa': value(0), 'Y': value(.24), 'Nnueff': value(3.04), 'fsR': value(1), 'meR': value(1),
                       'nH0_coefficient': value(11.223846333047), 'photon_density_coefficient': value(4.48162687719e-7),
                       'neutrino_coefficient': value(0.227107317660239), 'Hubble_coefficient_s_inv': value(3.2407792896393e-18)},
         'table_rows': selected_rows,
         'Gamma_source_formula': 'r2g=(fsR*fsR*fsR*fsR)^2*meR; db=exp((Eb-E21)/TR); Tvr_s=-r2g*A2s/abs(exp((Eb-E21)/TR)-1); Trv_s=Tvr_s*db; Tvr_p=-exp(-E32/TR)/3*r2g*A3s3d/abs(exp((Eb-E31)/TR)-1)-exp(-E42/TR)/3*r2g*A4s4d/abs(exp((Eb-E41)/TR)-1); Trv_p=Tvr_p*3*db; Gamma=-(Trv_s+Trv_p)',
         'Gamma_input_scope': 'selected b>=140: source read_twog_params normalizes A2s only below140; effects A-D=1, diffusion rates at selected bins are zero; no matter-temperature or effective recombination rate input required',
         'optical_depth_source_formula': 'Dtau=Gamma*x1s*cube(hPc/Eb/fsR/fsR/meR)*nH_cm3/8/pi/H_s_inv',
         'background_source_formula': 'TR=kBoltz*T0*(1+native_z)/(fsR*fsR*meR); nH_cm3=1e-6*(11.223846333047*obh2*(1-Y))*(1+native_z)^3; H from original history.c rec_HubbleConstant sum of five density contributions in original order',
         'native_piecewise': {'tau_gt_1e_minus6': 'A=1-exp(-tau); one_minus_P=1-(1-exp(-tau))/tau',
                              'tau_le_1e_minus6': 'A=tau-tau^2/2; one_minus_P=tau/2-tau^2/6',
                              'ideal_F_applicability': 'all selected saved right-snapshot tau exceed1e-6; verify inferred left tau remains same branch before adopting ideal F',
                              'ideal_F': '(favg-fin)/(fout-fin)=1/(1-exp(-tau))-1/tau'},
         'validation_only_right_state': {k: value(meta[k]) for k in ['iz_local', 'z', 'x1s', 'xe', 'xHII', 'nH_cm3', 'H_sInv', 'TM_eV_rescaled', 'TR_eV_rescaled']},
         'traces': traces,
         'status': 'extracted input; inversion and scientific admission not performed',
         'physical_radii': {'eS': None, 'en': None, 'eE': None, 'geometry': None, 'total': None}}
    dest = OUT / 'NATIVE_VIRTUAL_TRIPLE_TRACE_5126_5127.json'
    dest.write_text(json.dumps(p, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'path': str(dest), 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
                      'traces': len(traces), 'right_all_binary64_matches': all(all(t['right_snapshot_validation_only'][k] for k in ['incoming_binary64_matches','average_binary64_matches','outgoing_binary64_matches']) for t in traces if t['index']==5127)}))

if __name__ == '__main__':
    main()
