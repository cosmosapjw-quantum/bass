"""Single scoped source-bound tau-row numerical and independent-arithmetic run."""
from pathlib import Path
import sys, json, unittest, math, hashlib
from fractions import Fraction as Q
from decimal import Decimal, localcontext
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'code'))
import tau_row as t
import reference


def main():
    contract=json.loads((P/'CONTRACT.json').read_text())
    box=contract['frozen_box'].copy()
    fields={k:v for k,v in box.items() if k not in ('nb','THOMSON_coefficient_K')}
    nb=box['nb'];K=box['THOMSON_coefficient_K']
    src=t.verify_source();w=t.source_weights()
    result=t.row_box(fields=fields,nb=nb,K=K)
    z=[t.SIMPLEX_TOTALS[0]/3,Q(1,5),Q(1,10),Q(1,8),Q(1,7),Q(1,9)]
    point={'H':'5/2','h0':'3/2','href':'5/2','a':'3/2','Pi_m_norm':'1/3','y2':'-1/3','omega_gamma':'1/7','omega_nu':'1/3'}
    chosen=t.row_at_point(z=z,fields=point,nb='5/4',K='1')
    with localcontext() as ctx:
        ctx.prec=85
        decimal_row=reference.full_projected_row(z,point,'5/4','1')
        errors=[abs(Decimal(q.numerator)/Decimal(q.denominator)-d) for q,d in zip(chosen['row'],decimal_row)]
        tolerance=Decimal('2e-25')
        if max(errors)>tolerance: raise AssertionError('INDEPENDENT_DECIMAL_ROW_MISMATCH')
        fd_errors=[]
        for j in t.GEO_COMPACT:
            d=reference.direct_local_fd(z,point,'5/4','1',j,'1/1000000')
            q=chosen['row'][j]; fd_errors.append(abs(Decimal(q.numerator)/Decimal(q.denominator)-d))
        if max(fd_errors)>Decimal('3e-11'): raise AssertionError('FINITE_DIFFERENCE_LOCAL_TANGENT_MISMATCH')
    suite=unittest.defaultTestLoader.discover(str(P/'tests'),pattern='test_tau.py')
    u=unittest.TextTestRunner(stream=sys.stderr,verbosity=1).run(suite)
    if not u.wasSuccessful():raise AssertionError('TAU_NEW_UNIT_TEST_FAIL')
    included=[result['row'][i].includes(chosen['row'][i]) for i in range(30)]
    if not all(included):raise AssertionError('BOX_EXCLUDES_ANCHOR')
    artifact={
      'unit':'BASS_TAU_SOURCE_ROW_20261029','status':'PASS_CONDITIONAL_REPRESENTED_SOURCE_AND_SUPPLIED_BOX',
      'source_binding':contract['source_binding'],'source_SHA256_identity':src,
      'clock':'x=ln(a/a_ref), native increasing tau_T',
      'structure':{'shape':[1,30],'row_index':29,'geometry_columns':[1,2,3,13],'charged_columns':[23,24,25,26,27,28],'potential_nonzero_entries':10,'structural_zero_entries':20,'actual_full30_Jacobian':False},
      'owner_scale_weights':{k: [str(y) for y in v] for k,v in [('w',w['w']),('e',w['e'])]},
      'owner_scale_binary64_normalization':w['normalization_binary64_repr'],
      'diagnostic':{'synthetic_K':str(t.exact(K[0])),'K_source_value':None,'K_source_definition':'GAMMA_PER_NE/1e6',
                    'input_box':box,'row_box_exact':[x.as_json() for x in result['row']],
                    'tau_rhs_box_exact':result['interval_rhs'].as_json(),
                    'source_weight_e_exact':[str(x) for x in w['e']],
                    'point_state_exact':[str(x) for x in z],
                    'point_fields':point,'point_nb':'5/4','point_K':'1',
                    'tau_rhs_point_exact':str(chosen['tau_rhs']),
                    'row_point_exact':[str(x) for x in chosen['row']]},
      'checks':{'unit_methods':u.testsRun,'unit_failures':len(u.failures),'unit_errors':len(u.errors),
                'independent_full62_decimal85_max_abs':str(max(errors)),
                'full62_direct_numeric_tolerance':'2e-25',
                'finite_difference_max_abs':str(max(fd_errors)),
                'finite_difference_tolerance':'3e-11',
                'representative_all30_inclusions':sum(included),'simplex_vertices':24,'selected_box_corner_checks':48,
                'source_proof_CAS':'charged6+geometry4+chain1, Wolfram warning recorded separately'},
      'scientific_claim':{'physical_K_source_constant':None,'physical_whole_corridor':None,'physical_u33':None,'query_rounding':None,
                          'verified_model_provider':None,'actual_ODE_solution_enclosure':False,
                          'L4':False,'global_physical_completion':None,'original_DAG':'28/88','delta':0,
                          'R6':'DISTINCT_AUTHOR_NOT_RUN','C9':'DISTINCT_AUTHOR_NOT_RUN'},
      'notes':['Caveat: K=1 with numeric H/nb source-derived synthetic test box is not physical Thomson calibration',
               'Full 40-geometry to 23-even compact lift and 21-isotope to 9 then 6-charge elimination are preserved',
               'The independent Decimal reference is same-author arithmetic, not distinct-author review',
               'The accepted old chemical6x23 and kinetic/numerical owners are not reexecuted']
    }
    (P/'evidence/PRIMARY.json').write_text(json.dumps(artifact,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':artifact['status'],'tau_rhs_point':float(chosen['tau_rhs']),
                       'row_nonzero':{i:float(chosen['row'][i]) for i in result['nonzero']},
                       'tau_rhs_box':[float(v) for v in (result['interval_rhs'].lo,result['interval_rhs'].hi)],
                       'source_weights':[float(x) for x in w['w']],
                       'unit_methods':u.testsRun,'full62_maxerr':str(max(errors)),'local_fd_maxerr':str(max(fd_errors))},indent=2))

if __name__=='__main__':main()
