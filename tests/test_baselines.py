import unittest

from shaptcp import cost_aware_additional_coverage_order, shortest_duration_order


class BaselineTests(unittest.TestCase):
    def test_cost_aware_additional_can_prefer_short_test(self):
        matrix = {
            "slow": {"f1", "f2"},
            "fast": {"f3"},
        }
        durations = {"slow": 10.0, "fast": 1.0}

        order = cost_aware_additional_coverage_order(matrix, durations)

        self.assertEqual(order[0], "fast")

    def test_cost_aware_additional_respects_time_budget(self):
        matrix = {
            "slow": {"f1", "f2"},
            "fast": {"f3"},
        }
        durations = {"slow": 10.0, "fast": 1.0}

        order = cost_aware_additional_coverage_order(matrix, durations, time_budget=2.0)

        self.assertEqual(order, ("fast",))

    def test_shortest_duration_order(self):
        matrix = {"b": {"f1"}, "a": {"f2"}, "c": {"f3"}}
        durations = {"b": 2.0, "a": 1.0, "c": 1.0}

        self.assertEqual(shortest_duration_order(matrix, durations), ("a", "c", "b"))


if __name__ == "__main__":
    unittest.main()
