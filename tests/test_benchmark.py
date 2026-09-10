import tempfile
import unittest
from pathlib import Path

from src.benchmark import parse_scenarios, run_benchmarks, write_benchmark_summary


class BenchmarkTests(unittest.TestCase):
    def test_parse_scenarios_accepts_known_names(self) -> None:
        self.assertEqual(parse_scenarios("small, medium"), ["small", "medium"])

    def test_parse_scenarios_rejects_unknown_names(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown scenarios"):
            parse_scenarios("small,unknown")

    def test_run_benchmarks_returns_rows_for_scenario_method_capacity_grid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            rows = run_benchmarks(
                scenario_names=["small"],
                vehicle_capacities=[25, 40],
                methods=["nearest_neighbor", "savings"],
                data_dir=Path(directory),
            )

        self.assertEqual(len(rows), 4)
        self.assertEqual({row.scenario for row in rows}, {"small"})
        self.assertEqual({row.method for row in rows}, {"nearest_neighbor", "savings"})

    def test_write_benchmark_summary_creates_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            rows = run_benchmarks(
                scenario_names=["small"],
                vehicle_capacities=[25],
                methods=["nearest_neighbor"],
                data_dir=directory_path / "data",
            )
            output_path = directory_path / "benchmark.csv"
            write_benchmark_summary(rows, output_path)
            contents = output_path.read_text(encoding="utf-8")

        self.assertIn("scenario,method,vehicle_capacity", contents)
        self.assertIn("small,nearest_neighbor,25", contents)


if __name__ == "__main__":
    unittest.main()

