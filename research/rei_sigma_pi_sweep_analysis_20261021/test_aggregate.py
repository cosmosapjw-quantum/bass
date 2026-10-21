"""Focused saved-data mutation checks; no solver, native build or benchmark."""
from __future__ import annotations
import copy
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import aggregate as a
from diagnostics import cancellation, matched_controls

TARGET = Path(__file__).resolve().parent / 'results/inputs/ncp5'


class AggregateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = a.load(TARGET/'small-plan.json')
        cls.manifest = a.load(TARGET/'small-prepared/manifest.json')
        cls.groups = [a.load(path) for path in sorted((TARGET/'small-scope/jobs').rglob('result.json'))]
        cls.default_plan = a.load(TARGET/'default-plan.json')
        cls.source = a.wp.BASELINE

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_fixture(self, groups=None, plan=None, manifest=None, label='result'):
        directory = self.root/label
        directory.mkdir()
        p = copy.deepcopy(self.plan if plan is None else plan)
        m = copy.deepcopy(self.manifest if manifest is None else manifest)
        plan_path = directory/'plan.json'
        plan_path.write_text(json.dumps(p, sort_keys=True))
        m['completion_reuse']['source_plan_sha256'] = a.wp.file_hash(plan_path)
        manifest_path = directory/'manifest.json'
        manifest_path.write_text(json.dumps(m))
        paths = []
        for index, group in enumerate(self.groups if groups is None else groups):
            path = directory/f'group-{index}.json'
            path.write_text(json.dumps(group))
            paths.append(path)
        return a.aggregate(plan_path, directory/'out', manifest_path=manifest_path, results=paths)

    def test_actual_target_relocated_portable_without_context_or_host_toolchain_gate(self):
        split, _ = a.wp.modules()
        with patch.object(split, 'PreparedContext', side_effect=AssertionError('solver context forbidden')), \
             patch.object(split.prior, 'PreparedContext', side_effect=AssertionError('solver context forbidden')):
            summary = self.run_fixture()
        self.assertEqual((summary['expected_count'],summary['successful_pending_count'],summary['missing_pending_count'],summary['history_rows']), (5,5,0,15))
        cohort = next(iter(summary['cohorts'].values()))
        self.assertEqual(cohort['toolchain_json'], a.wp.canonical(self.manifest['toolchain']).decode())
        self.assertEqual(cohort['nsteps'],2)

    def test_missing_is_partial_not_zero_or_changed_denominator(self):
        summary = self.run_fixture(self.groups[:-1])
        self.assertEqual((summary['status'],summary['expected_count'],summary['successful_pending_count'],summary['missing_pending_count'],summary['history_rows']), ('PARTIAL',5,4,1,12))

    def test_unexpected_case_is_rejected(self):
        groups = copy.deepcopy(self.groups)
        groups[0]['cases'][0]['case']['case_id'] = 'unexpected'
        with self.assertRaisesRegex(a.InputIntegrityError,'UNEXPECTED_CASE'):
            self.run_fixture(groups)

    def test_scientific_duplicate_ignores_group_reuse_metadata(self):
        duplicate = copy.deepcopy(self.groups[0])
        for item in duplicate.get('case_cache',[]): item['reused'] = not item['reused']
        summary = self.run_fixture([*self.groups,duplicate])
        self.assertEqual((summary['case_count'],summary['scientific_duplicate_count'],summary['history_rows']),(5,1,15))

    def test_conflicting_scientific_duplicate_is_rejected(self):
        duplicate = copy.deepcopy(self.groups[0])
        duplicate['cases'][0]['owner_result']['geometry_integrations'] += 1
        with self.assertRaisesRegex(a.InputIntegrityError,'CONFLICTING_SCIENTIFIC_DUPLICATE'):
            self.run_fixture([*self.groups,duplicate])

    def test_wrong_group_and_owner_nsteps(self):
        for location in ('group','owner'):
            with self.subTest(location=location):
                groups = copy.deepcopy(self.groups)
                if location == 'group': groups[0]['nsteps'] = 64
                else: groups[0]['cases'][0]['owner_result']['nsteps'] = 64
                with self.assertRaisesRegex(a.InputIntegrityError,'NSTEPS|STEP_COUNT'):
                    self.run_fixture(groups,label=location)

    def test_wrong_science_binding(self):
        groups = copy.deepcopy(self.groups)
        groups[0]['science_binding']['source'] = '0'*64
        with self.assertRaisesRegex(a.InputIntegrityError,'GROUP_SCIENCE_BINDING'):
            self.run_fixture(groups)

    def test_redundant_physical_row_is_checked_without_replacement(self):
        groups = copy.deepcopy(self.groups)
        groups[0]['cases'][0]['initial']['Pi_component_norm_sum'] += 1e-4
        with self.assertRaisesRegex(a.PhysicsError,'COMPONENT_SCALED_ARITHMETIC_FAILED'):
            self.run_fixture(groups)

    def test_failed_gate_is_physics_diagnosis(self):
        groups = copy.deepcopy(self.groups)
        groups[0]['cases'][0]['gates']['number_5e-12'] = False
        with self.assertRaisesRegex(a.PhysicsError,'ORIGINAL_PHYSICS_GATE_FAILED'):
            self.run_fixture(groups)

    def test_zero_scale_exact_cancellation_and_absent_control(self):
        values = cancellation([0.,1.,1.],[0.,-1.,-.5])
        self.assertEqual(values['cancellation_status'], ['ZERO_COMPONENT_SCALE','EXACT_CANCELLATION','FINITE'])
        self.assertEqual(values['residual_fraction'][:2], [None,0.])
        self.assertEqual(values['condition'][:2], [None,None])
        sample = {'case_id':'target','signed_Sigma_requested':0.,'signed_Pi_m_requested':1.,'signed_Pi_r_requested':-1.,
                  'cohort_id':'native2','initial_signed_Sigma':0.,'final_signed_Sigma':1e-8}
        control = {**sample,'case_id':'wrong_cohort_control','signed_Pi_m_requested':0.,'signed_Pi_r_requested':0.,'cohort_id':'archived64'}
        rows = [sample,control]
        matched_controls(rows)
        self.assertEqual(sample['control_status'],'MISSING_CONTROL')
        self.assertIsNone(sample['control_subtracted_final_signed_Sigma'])
        self.assertEqual(sample['raw_delta_signed_Sigma'],1e-8)

    def test_completed729_exact_float_projection_and_requested_alias(self):
        plan = copy.deepcopy(self.default_plan)
        original_label = plan['completed'][0]['case_id']
        plan['completed'][0]['case_id'] = 'legitimate_alias'
        path = self.root/'plan.json'
        path.write_text(json.dumps(plan))
        summary = a.aggregate(path,self.root/'completed')
        self.assertEqual((summary['expected_count'],summary['reused_completed_count'],summary['successful_pending_count'],summary['history_rows']),(729,729,0,0))
        with (self.source/a.wp.CASES).open(newline='') as stream:
            original = {r['case_id']:r for r in csv.DictReader(stream)}
        with (self.root/'completed/cases.csv').open(newline='') as stream:
            projected = list(csv.DictReader(stream))
        for row in projected:
            old = original[original_label if row['case_id']=='legitimate_alias' else row['case_id']]
            for key,value in old.items():
                if key == 'case_id': continue
                try:
                    number = float(value)
                except ValueError:
                    self.assertEqual(row[key],value)
                else:
                    self.assertEqual(float(row[key]),number)

    def test_actual_first_second_worker_scope_duplicate(self):
        native = Path(__file__).resolve().parents[1]/'rei_sigma_pi_native_moments_20261021/evidence/worker'
        summary = a.aggregate(native/'plan.json',self.root/'worker',manifest_path=native/'prepared/manifest.json',
                              scopes=[native/'scope_first',native/'scope_second'])
        self.assertEqual((summary['expected_count'],summary['successful_pending_count'],summary['scientific_duplicate_count'],summary['history_rows']),(1,1,1,3))


if __name__ == '__main__':
    unittest.main()
