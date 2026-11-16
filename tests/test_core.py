import json
import subprocess
import sys
import unittest
from log_inspector.core import percentile, summarize

class LogTests(unittest.TestCase):
    def test_nearest_rank(self):
        self.assertEqual(percentile(list(range(1, 101)), 95), 95)
        self.assertEqual(percentile([1, 2], 50), 1)
        self.assertIsNone(percentile([], 95))
        with self.assertRaises(ValueError):
            percentile([1], 0)

    def test_bad_records_and_blank_lines(self):
        report = summarize(["\n", "bad", "[]", '{"level":1}', '{}'])
        self.assertEqual(report["malformed_lines"], [2, 3, 4])
        self.assertEqual(report["records"], 1)

    def test_latency_validation(self):
        values = [True, -1, "12", None, float("nan"), float("inf"), 10**400, 0, 20]
        report = summarize(json.dumps({"duration_ms": value}) for value in values)
        self.assertEqual(report["invalid_durations"], 7)
        self.assertEqual(report["latency_ms"], {"count": 2, "p50": 0, "p95": 20})

    def test_errors_and_levels(self):
        report = summarize([json.dumps({"level": "error", "message": "timeout"})] * 2)
        self.assertEqual(report["levels"], {"ERROR": 2})
        self.assertEqual(report["top_errors"], [{"message": "timeout", "count": 2}])

    def test_empty(self):
        self.assertEqual(summarize([])["records"], 0)

    def test_cli(self):
        result = subprocess.run([sys.executable, "-m", "log_inspector", "examples/app.jsonl"],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["records"], 3)
