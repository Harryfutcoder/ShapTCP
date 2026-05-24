import tempfile
import unittest
from pathlib import Path

from shaptcp import load_binary_incidence_matrix


class IoTests(unittest.TestCase):
    def test_loads_dense_binary_matrix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "matrix.txt"
            path.write_text("101\n011\n", encoding="utf-8")

            dataset = load_binary_incidence_matrix(path)

        self.assertEqual(dataset.test_ids, ("T1", "T2"))
        self.assertEqual(dataset.fault_ids, ("F1", "F2", "F3"))
        self.assertEqual(dataset.test_to_faults["T1"], {"F1", "F3"})
        self.assertEqual(dataset.test_to_faults["T2"], {"F2", "F3"})

    def test_loads_csv_binary_matrix_with_custom_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "matrix.csv"
            path.write_text("1,0,1\n0,1,0\n", encoding="utf-8")

            dataset = load_binary_incidence_matrix(
                path,
                test_ids=("test_a", "test_b"),
                fault_ids=("mut_1", "mut_2", "mut_3"),
            )

        self.assertEqual(dataset.test_to_faults["test_a"], {"mut_1", "mut_3"})
        self.assertEqual(dataset.test_to_faults["test_b"], {"mut_2"})

    def test_rejects_ragged_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "matrix.txt"
            path.write_text("101\n01\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_binary_incidence_matrix(path)

    def test_rejects_non_binary_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "matrix.txt"
            path.write_text("102\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_binary_incidence_matrix(path)


if __name__ == "__main__":
    unittest.main()
