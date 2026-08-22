import tempfile
import unittest
from pathlib import Path

from src.distance import Location
from src.experiments import (
    evaluate_capacity_scenario,
    parse_capacities,
    run_capacity_scenarios,
    write_scenario_results,
)


class ExperimentTests(unittest.TestCase):
    def test_evaluate_capacity_scenario_returns_key_metrics(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
            Location("C003", 8, 0, 6),
        ]

        result, routes = evaluate_capacity_scenario(locations, vehicle_capacity=10)

        self.assertEqual(result.vehicle_capacity, 10)
        self.assertEqual(result.total_demand, 15)
        self.assertEqual(result.route_count, len(routes))
        self.assertGreater(result.total_distance, 0)
        self.assertGreaterEqual(result.average_utilization, 0)
        self.assertLessEqual(result.average_utilization, 1)

    def test_run_capacity_scenarios_preserves_capacity_order(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
        ]

        results = run_capacity_scenarios(locations, [10, 20])

        self.assertEqual([result.vehicle_capacity for result in results], [10, 20])

    def test_write_scenario_results_creates_csv(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
        ]
        results = run_capacity_scenarios(locations, [10])

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "scenarios.csv"
            write_scenario_results(results, output_path)
            contents = output_path.read_text(encoding="utf-8")

        self.assertIn("vehicle_capacity,route_count,total_distance", contents)
        self.assertIn("10,1", contents)

    def test_parse_capacities_rejects_nonpositive_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            parse_capacities("20,0")


if __name__ == "__main__":
    unittest.main()

