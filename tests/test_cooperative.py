import unittest

from shaptcp import (
    additional_coverage_order,
    apfd,
    fault_recall_at_k,
    rare_fault_recall_at_k,
    redundancy_at_k,
    shaptcp_order,
    static_shapley_scores,
)


class CooperativeTests(unittest.TestCase):
    def test_static_shapley_splits_shared_fault_credit(self):
        matrix = {
            "A": {"f1", "f2"},
            "B": {"f1", "f2"},
            "C": {"f3"},
        }

        scores = static_shapley_scores(matrix)

        self.assertAlmostEqual(scores["A"], 1.0)
        self.assertAlmostEqual(scores["B"], 1.0)
        self.assertAlmostEqual(scores["C"], 1.0)

    def test_shaptcp_avoids_redundant_second_pick(self):
        matrix = {
            "A": {"f1", "f2"},
            "B": {"f1", "f2"},
            "C": {"f3"},
        }

        order = shaptcp_order(matrix).order

        self.assertEqual(order[:2], ("A", "C"))

    def test_lexicographic_unique_is_policy_not_apfd_guarantee(self):
        matrix = {
            "A": {"f1", "f2"},
            "B": {"f1", "f2"},
            "C": {"f3"},
        }

        unique_order = shaptcp_order(matrix, budget_count=2, lexicographic_unique=True).order
        dense_first = ("A", "C")

        self.assertEqual(unique_order, ("C", "A"))
        self.assertLess(apfd(unique_order, matrix), apfd(dense_first, matrix))

    def test_additional_coverage_baseline_matches_expected(self):
        matrix = {
            "A": {"f1", "f2"},
            "B": {"f1", "f2"},
            "C": {"f3"},
        }

        self.assertEqual(additional_coverage_order(matrix), ("A", "C", "B"))

    def test_count_budget_limits_order(self):
        matrix = {"A": {"f1"}, "B": {"f2"}, "C": {"f3"}}

        order = shaptcp_order(matrix, budget_count=2).order

        self.assertEqual(len(order), 2)

    def test_time_budget_skips_tests_that_do_not_fit(self):
        matrix = {
            "slow": {"f1", "f2"},
            "fast": {"f3"},
        }
        durations = {"slow": 10.0, "fast": 1.0}

        order = shaptcp_order(matrix, durations=durations, time_budget=2.0).order

        self.assertEqual(order, ("fast",))

    def test_cost_exponent_can_change_first_choice(self):
        matrix = {
            "slow": {"f1", "f2"},
            "fast": {"f3"},
        }
        durations = {"slow": 10.0, "fast": 1.0}

        pure = shaptcp_order(matrix, durations=durations, cost_exponent=0.0).order
        cost = shaptcp_order(matrix, durations=durations, cost_exponent=1.0).order

        self.assertEqual(pure[0], "slow")
        self.assertEqual(cost[0], "fast")

    def test_recall_and_redundancy_metrics(self):
        matrix = {
            "A": {"f1", "f2"},
            "B": {"f1", "f2"},
            "C": {"f3"},
        }
        order = ("A", "B", "C")

        self.assertAlmostEqual(fault_recall_at_k(order, matrix, k=2), 2 / 3)
        self.assertAlmostEqual(rare_fault_recall_at_k(order, matrix, k=2), 0.0)
        self.assertGreater(redundancy_at_k(order, matrix, k=2), 0.0)


if __name__ == "__main__":
    unittest.main()
