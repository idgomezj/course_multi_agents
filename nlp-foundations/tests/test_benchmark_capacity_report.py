"""Offline correctness tests for benchmark report cost projections."""
import importlib.util
import json
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('capacity_report', BASE/'benchmark_capacity_report.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
DATA = json.loads((BASE/'datos'/'benchmark_three_models_20261120.json').read_text(encoding='utf-8'))


class TestCapacityProjection(unittest.TestCase):
    def test_volume_and_cost_from_real_measurements(self):
        out = M.project(DATA)
        self.assertEqual(out['scenario']['monthly_requests'], 864_000_000)
        models = {m['id']:m for m in out['models']}
        self.assertEqual(models['rules']['replicas_recommended_proxy'],1)
        self.assertEqual(models['ml']['replicas_recommended_proxy'],2)
        self.assertEqual(models['pretrained']['replicas_recommended_proxy'],39)
        self.assertAlmostEqual(models['rules']['total_active_usd'],26.592,places=2)
        self.assertAlmostEqual(models['ml']['total_active_usd'],53.184,places=2)
        self.assertAlmostEqual(models['pretrained']['total_active_usd'],1826.76,places=2)

    def test_pretrained_tokens_not_paid_vendor_tokens(self):
        model = M.project(DATA)['models'][2]
        self.assertEqual(model['model_input_tokens_month'],92_448_000_000)
        self.assertEqual(model['provider_token_api_cost_usd'],0)
        self.assertGreater(model['infra_per_million_nli_tokens_usd'],0)

    def test_interactive_html_contains_all_three(self):
        html = '''<html><head></head><body><h2>Demand and monthly infrastructure estimate</h2><p>old</p><h2>Model tokens and cost attribution</h2><p>old tokens</p><h2>How token costs work here</h2></body></html>'''
        final, projection = M.enhance_html(html,DATA)
        self.assertIn('id="proj-rps"', final)
        self.assertIn('864,000,000', final)
        self.assertIn('id="projection-total-pretrained"', final)
        self.assertIn('id="projection-total-ml"', final)
        self.assertNotIn('<p>old</p>', final)
        self.assertNotIn('<p>old tokens</p>', final)
        self.assertIn('92,448,000,000', final)
        second, _=M.enhance_html(final,DATA)
        self.assertEqual(second.count('id="capacity-projection-js"'),1)
        self.assertEqual(second.count('id="capacity-style"'),1)

    def test_volume_varies_with_hours(self):
        p=M.project(DATA,target_rps=500,hours_day=4,days=20)
        self.assertEqual(p['scenario']['monthly_requests'],144_000_000)
        self.assertLess(p['models'][2]['total_active_usd'],1826.76)

    def test_error_on_invalid_inputs(self):
        with self.assertRaises(ValueError):M.project(DATA,target_rps=0)
        with self.assertRaises(ValueError):M.project(DATA,capacity_fraction=1.2)

if __name__=='__main__': unittest.main()
