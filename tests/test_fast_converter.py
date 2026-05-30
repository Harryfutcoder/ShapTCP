import importlib.util
import pickle
import tempfile
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "convert_fast_fault_matrix.py"
SPEC = importlib.util.spec_from_file_location("convert_fast_fault_matrix", SCRIPT)
fast_converter = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(fast_converter)


class FastConverterTests(unittest.TestCase):
    def test_converts_c_test_to_fault_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subject_dir = root / "input" / "toy_v1"
            subject_dir.mkdir(parents=True)
            (subject_dir / "toy-line.txt").write_text("a b\nc\n\nx y\n", encoding="utf-8")
            with (subject_dir / "fault_matrix_key_tc.pickle").open("wb") as handle:
                pickle.dump({1: [10, 11], 3: [11]}, handle)

            schema, pickle_path = fast_converter.resolve_schema(subject_dir, "auto")
            loaded = fast_converter.load_pickle_dict(pickle_path)
            converted = fast_converter.convert_c_fault_matrix(loaded, 3)

        self.assertEqual(schema, "c-test-to-faults")
        self.assertEqual(converted["tc_1"], {"fault_10", "fault_11"})
        self.assertEqual(converted["tc_2"], set())
        self.assertEqual(converted["tc_3"], {"fault_11"})

    def test_converts_java_bug_to_tests_schema(self):
        converted = fast_converter.convert_java_fault_matrix({1: [2], 2: [1, 3]}, 3)

        self.assertEqual(converted["tc_1"], {"bug_2"})
        self.assertEqual(converted["tc_2"], {"bug_1"})
        self.assertEqual(converted["tc_3"], {"bug_2"})


if __name__ == "__main__":
    unittest.main()
