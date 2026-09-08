import tempfile
import unittest
from pathlib import Path

from src.distance import Location
from src.experiments import (
    evaluate_capacity_scenario,
    parse_capacities,
    parse_methods,
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

        self.assertEqual(result.method, "nearest_neighbor")
        self.assertEqual(result.vehicle_capacity, 10)
        self.assertEqual(result.total_demand, 15)
        self.assertEqual(result.route_count, len(routes))
        self.assertGreater(result.total_distance, 0)
        self.assertGreaterEqual(result.total_lateness, 0)
        self.assertGreaterEqual(result.objective_value, result.total_distance)
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

    def test_run_capacity_scenarios_compares_selected_methods(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
        ]

        results = run_capacity_scenarios(
            locations, [10], methods=["nearest_neighbor", "savings", "savings_2opt"]
        )

        self.assertEqual(
            [result.method for result in results],
            ["nearest_neighbor", "savings", "savings_2opt"],
        )

    def test_evaluate_capacity_scenario_supports_two_opt_method(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
        ]

        result, routes = evaluate_capacity_scenario(
            locations, vehicle_capacity=10, method="nearest_neighbor_2opt"
        )

        self.assertEqual(result.method, "nearest_neighbor_2opt")
        self.assertEqual(result.route_count, len(routes))

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

        self.assertIn(
            "method,vehicle_capacity,route_count,total_distance,total_lateness",
            contents,
        )
        self.assertIn("nearest_neighbor,10,1", contents)

    def test_lateness_penalty_changes_objective_value(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 300, 0, 4),
        ]

        low_penalty, _ = evaluate_capacity_scenario(
            locations, vehicle_capacity=10, lateness_penalty=1
        )
        high_penalty, _ = evaluate_capacity_scenario(
            locations, vehicle_capacity=10, lateness_penalty=100
        )

        self.assertGreater(high_penalty.objective_value, low_penalty.objective_value)

    def test_parse_capacities_rejects_nonpositive_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            parse_capacities("20,0")

    def test_parse_methods_rejects_empty_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one method"):
            parse_methods(" , ")


if __name__ == "__main__":
    unittest.main()
