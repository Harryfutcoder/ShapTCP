import math
import unittest

from shaptcp import apfd, apfdc, time_to_first_fault


class MetricsTests(unittest.TestCase):
    def test_apfd_rewards_earlier_dense_fault_detection(self):
        matrix = {
            "A": {"f1", "f2"},
            "C": {"f3"},
        }

        self.assertGreater(apfd(("A", "C"), matrix), apfd(("C", "A"), matrix))

    def test_apfd_returns_nan_for_empty_fault_set(self):
        self.assertTrue(math.isnan(apfd(("A",), {"A": set()})))

    def test_apfdc_prefers_fast_fault_detection_when_faults_equal(self):
        matrix = {
            "slow": {"f1"},
            "fast": {"f2"},
        }
        durations = {"slow": 10.0, "fast": 1.0}

        self.assertGreater(
            apfdc(("fast", "slow"), matrix, durations),
            apfdc(("slow", "fast"), matrix, durations),
        )

    def test_time_to_first_fault(self):
        matrix = {
            "empty": set(),
            "faulty": {"f1"},
        }
        durations = {"empty": 2.0, "faulty": 3.0}

        self.assertEqual(time_to_first_fault(("empty", "faulty"), matrix, durations), 5.0)


if __name__ == "__main__":
    unittest.main()
