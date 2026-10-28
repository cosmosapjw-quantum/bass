import sys,unittest,math,copy,random
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import tau_row as tr
import reference

FIELDS={'H':'5/2','h0':'3/2','href':'5/2','a':'3/2','Pi_m_norm':'1/3','y2':'-1/3','omega_gamma':'1/7','omega_nu':'1/3'}
BOX={'H':['2','3'],'h0':['1','2'],'href':['2','3'],'a':['1','2'],'Pi_m_norm':['-1','2'],'y2':['-2','1'],'omega_gamma':['0','1/3'],'omega_nu':['1/5','1/2']}
T=tr.SIMPLEX_TOTALS
Z=[T[0]/3,F(1,5),F(1,10),F(1,8),F(1,7),F(1,9)]
W=tr.source_weights()

class TauTests(unittest.TestCase):
 def test_source_byte_hashes(self):self.assertEqual(len(tr.verify_source()),6)
 def test_row_dimensions(self):self.assertEqual(len(tr.row_at_point(z=Z,fields=FIELDS,nb='5/4',K='1')['row']),30)
 def test_compact30_position(self):self.assertEqual(tr.TAU_ROW,29)
 def test_geometry_mapping(self):self.assertEqual(tr.GEO_COMPACT,(1,2,3,13))
 def test_exact_six_charged_columns(self):self.assertEqual(tr.CHARGED,tuple(range(23,29)))
 def test_sparse_row_10_and_20(self):
  r=tr.row_box(fields=BOX,nb=['1','2'],K=['1','1']);self.assertEqual((len(r['nonzero']),len(r['zero'])),(10,20))
 def test_tau_column_exact_zero(self):self.assertEqual(tr.row_at_point(z=Z,fields=FIELDS,nb='1',K='1')['row'][29],0)
 def test_source_lift_weights(self):
  s=W['individual'];self.assertEqual(W['w'],[s['H1']+s['D'],s['He3']+s['He4'],s['Li6']+s['Li7']])
 def test_ion_charges_source(self):self.assertEqual(W['e'],[W['w'][0],W['w'][1],2*W['w'][1],W['w'][2],2*W['w'][2],3*W['w'][2]])
 def test_not_old_synthetic_weights(self):self.assertNotEqual(W['w'],list(map(F,('2','3','5'))))
 def test_tau_rhs_nonnegative(self):self.assertGreater(tr.row_at_point(z=Z,fields=FIELDS,nb='1',K='1')['tau_rhs'],0)
 def test_geometry_signs_for_signed_input(self):
  p=tr.row_at_point(z=Z,fields=FIELDS,nb='1',K='1')['row'];self.assertTrue(p[1]>0 and p[2]>0 and p[3]<0 and p[13]<0)
 def test_all_20_source_zero_at_point(self):
  p=tr.row_at_point(z=Z,fields=FIELDS,nb='1',K='1')['row'];rr=tr.row_box(fields=BOX,nb=['1','2'],K=['1','1']);self.assertTrue(all(p[i]==0 for i in rr['zero']))
 def test_full62_direct_projection_decimal(self):
  a=tr.row_at_point(z=Z,fields=FIELDS,nb='5/4',K='1')['row'];b=reference.full_projected_row(Z,FIELDS,'5/4','1')
  self.assertEqual(len(b),30)
  for x,y in zip(a,b): self.assertLessEqual(abs(Decimal(x.numerator)/Decimal(x.denominator)-y),Decimal('2e-25'))
 def test_electron_source_full21(self):
  p=tr.row_at_point(z=Z,fields=FIELDS,nb='5/4',K='1');a=reference.source_full_electrons(Z,'5/4')
  self.assertLessEqual(abs(Decimal(p['electron_over_nb'].numerator)/Decimal(p['electron_over_nb'].denominator)*Decimal('1.25')-a),Decimal('2e-25'))
 def test_geom_finite_difference_tangent(self):
  p=tr.row_at_point(z=Z,fields=FIELDS,nb='5/4',K='1')['row']
  for j in (1,2,3,13):
   fd=reference.direct_local_fd(Z,FIELDS,'5/4','1',j,'1/1000000')
   pp=Decimal(p[j].numerator)/Decimal(p[j].denominator)
   self.assertLess(abs(fd-pp),Decimal('3e-11'))
 def test_wrong_sign_control(self):
  p=tr.row_at_point(z=Z,fields=FIELDS,nb='5/4',K='1')['row'];self.assertGreater(abs(p[3]-(-p[3])),F(0))
 def test_exact_interval_contains_anchor(self):
  b=tr.row_box(fields=BOX,nb=['1','2'],K=['1','1'])['row'];r=tr.row_at_point(z=Z,fields=FIELDS,nb='5/4',K='1')['row']
  for I,v in zip(b,r):self.assertTrue(I.includes(v))
 def test_box_roundtrip_and_zero_purity(self):
  o=tr.row_box(fields=BOX,nb=['1','2'],K=['1','1']);self.assertTrue(all(o['row'][i].as_json()==['0','0'] for i in o['zero']))
 def test_state_24_simplex_vertices(self):
  import itertools
  for h,he,li in itertools.product(range(2),range(3),range(4)):
   z=[F(0)]*6
   if h:z[0]=T[0]
   if he:z[he]=1
   if li:z[li+2]=1
   tr.membership(z)
 def test_all_vertices_selected_field_corners(self):
  import itertools
  out=tr.row_box(fields=BOX,nb=['1','2'],K=['1','1'])['row'];count=0
  for h,he,li in itertools.product(range(2),range(3),range(4)):
   z=[F(0)]*6
   if h:z[0]=T[0]
   if he:z[he]=1
   if li:z[li+2]=1
   for q in [0,1]:
    fields={k:v[q] for k,v in BOX.items()};r=tr.row_at_point(z=z,fields=fields,nb=('1','2')[q],K='1')['row']
    self.assertTrue(all(I.includes(v) for I,v in zip(out,r)));count+=1
  self.assertEqual(count,48)
 def test_invalid_source_binding(self):
  with self.assertRaises(ValueError):tr.row_box(fields=BOX,nb=('1','2'),K='1',binding='wrong')
 def test_missing_positive_H(self):
  f=dict(BOX);f['H']=['0','1']
  with self.assertRaises(ValueError):tr.row_box(fields=f,nb=['1','2'],K='1')
 def test_negative_nb_or_K(self):
  for args in ({'nb':['-1','2'],'K':'1'},{'nb':'1','K':['-1','0']}):
   with self.assertRaises(ValueError):tr.row_box(fields=BOX,**args)
 def test_bad_omega_rejected(self):
  f=dict(BOX);f['omega_nu']=['-1','1']
  with self.assertRaises(ValueError):tr.row_box(fields=f,nb='1',K='1')
 def test_bad_simplex_rejected(self):
  for z in ([F(-1)]+list(Z[1:]),[F(2)]+list(Z[1:]),[F(0),F(1),F(1),F(0),F(0),F(0)]):
   with self.assertRaises(ValueError):tr.membership(z)
 def test_no_physical_promote(self):
  b=tr.row_box(fields=BOX,nb=['1','2'],K='1');self.assertFalse(b['full30_provider']);self.assertFalse(b['actual_whole_corridor']);self.assertFalse(b['owner_THOMSON_prefactor_bound'])
 def test_zero_electron_geometry_only(self):
  p=tr.row_at_point(z=[0]*6,fields=FIELDS,nb='1',K='1');self.assertEqual(p['tau_rhs'],0)
  self.assertTrue(all(p['row'][j]==0 for j in tr.GEO_COMPACT))
 def test_zero_K_whole_row(self):self.assertTrue(all(x==0 for x in tr.row_at_point(z=Z,fields=FIELDS,nb='1',K='0')['row']))
 def test_float_bool_reject(self):
  for arg in [0.2,True,None]:
   with self.assertRaises(ValueError):tr.exact(arg)
 def test_interval_signed_product_and_reversal(self):
  self.assertEqual(tr.interval(('-2','3'))*tr.interval(('1','2')),tr.Interval(-4,6))
  with self.assertRaises(ValueError):tr.Interval(3,2)
 def test_source_time_not_state_derivative(self):
  self.assertEqual(tr.row_at_point(z=Z,fields=FIELDS,nb='1',K='1')['row'][0],0)

if __name__=='__main__':unittest.main(verbosity=2)
