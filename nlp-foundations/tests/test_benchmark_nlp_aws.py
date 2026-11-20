"""Reproducible benchmark correctness tests; no internet or pretrained weights."""
from pathlib import Path
import importlib.util
import tempfile
import unittest
from types import SimpleNamespace

PATH = Path(__file__).resolve().parents[1] / "benchmark_nlp_aws.py"
spec = importlib.util.spec_from_file_location("benchmark_nlp_aws", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BenchmarkTests(unittest.TestCase):
    def test_percentiles(self):
        self.assertEqual(module.percentile([5, 1, 3], 0.5), 3)
        self.assertEqual(module.percentile([1, 2, 3], 0), 1)
        self.assertIsNone(module.percentile([], .95))

    def test_monthly_volume(self):
        self.assertEqual(100 * 3600 * 8, 2_880_000)
        self.assertEqual(100 * 3600 * 8 * 30, 86_400_000)

    def test_missing_model_has_no_cost_projection(self):
        args = module.parse_args([])
        result = module.pricing({"id": "pretrained", "instance": "c7i.xlarge", "status": "NOT_MEASURED"}, args, 8)
        self.assertEqual(result["status"], "NO_BENCHMARK")
        self.assertIsNone(result["estimated_cost_active_usd"])
        self.assertIsNone(result["replicas_assumed"])

    def test_real_cost_formula_has_ebs_even_with_short_run(self):
        args = module.parse_args([])
        result = module.pricing({
            "id": "rules", "instance": "m7i.large", "status": "MEASURED",
            "inference": {"sequential_rps": 1000, "avg_response_body_bytes": 50, "peak_process_rss_mib": 100},
            "inputs": {"tokens_per_message_avg": None},
        }, args, 8)
        self.assertEqual(result["replicas_assumed"], 1)
        self.assertAlmostEqual(result["ec2_compute_active_usd"], 0.8064)
        self.assertAlmostEqual(result["ebs_usd"], 2.4)
        self.assertAlmostEqual(result["estimated_cost_active_usd"], 3.2064)
        self.assertEqual(result["provider_token_charge_usd"], 0)
        self.assertEqual(result["status"], "UNVERIFIED_HOST_PROJECTION")

    def test_stress_does_not_confuse_target_with_capacity(self):
        result = module.stress(lambda txt: "ACCESO", ["texto"], target_rps=15,
                               duration=.4, workers=2, backlog=3)
        self.assertEqual(result["offered"], 6)
        self.assertEqual(result["completed"], 6)
        self.assertEqual(result["rejected"], 0)
        self.assertGreater(result["achieved_rps_including_drain"], 0)

    def test_20_messages_read(self):
        self.assertEqual(len(module.get_data()), 20)


if __name__ == "__main__":
    unittest.main()
