import unittest

from shaptcp import apply_fault_clusters, cluster_faults_by_cofailure


class FaultClusteringTests(unittest.TestCase):
    def test_cofailure_clustering_deduplicates_identical_signatures(self):
        fault_to_tests = {
            "sig_a": {"T1", "T2"},
            "sig_b": {"T1", "T2"},
            "sig_c": {"T3"},
        }
        test_to_faults = {
            "T1": {"sig_a", "sig_b"},
            "T2": {"sig_a", "sig_b"},
            "T3": {"sig_c"},
        }

        clusters = cluster_faults_by_cofailure(fault_to_tests, threshold=1.0)
        clustered = apply_fault_clusters(test_to_faults, clusters)

        self.assertEqual(len(clustered["T1"]), 1)
        self.assertEqual(len(clustered["T2"]), 1)
        self.assertEqual(len(clustered["T3"]), 1)

    def test_threshold_validation(self):
        with self.assertRaises(ValueError):
            cluster_faults_by_cofailure({}, threshold=1.1)


if __name__ == "__main__":
    unittest.main()
