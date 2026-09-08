import tempfile
import unittest
from pathlib import Path

from src.report import (
    build_experiment_report,
    find_best_objective_scenario,
    find_fewest_route_scenario,
    find_lowest_distance_scenario,
    write_experiment_report,
)


class ReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario_rows = [
            {
                "method": "nearest_neighbor",
                "vehicle_capacity": "25",
                "route_count": "4",
                "total_distance": "685.02",
                "total_lateness": "15.0",
                "late_stops": "2",
                "objective_value": "835.02",
                "average_utilization": "0.93",
                "runtime_ms": "0.254",
            },
            {
                "method": "savings",
                "vehicle_capacity": "50",
                "route_count": "2",
                "total_distance": "474.83",
                "total_lateness": "2.0",
                "late_stops": "1",
                "objective_value": "494.83",
                "average_utilization": "0.93",
                "runtime_ms": "0.436",
            },
        ]
        self.route_rows = [
            {
                "vehicle_id": "1",
                "customer_count": "2",
                "load": "9",
                "distance": "20.5",
                "route": "DEPOT -> C001 -> C002 -> DEPOT",
            }
        ]

    def test_find_lowest_distance_scenario(self) -> None:
        result = find_lowest_distance_scenario(self.scenario_rows)

        self.assertEqual(result["vehicle_capacity"], "50")

    def test_find_fewest_route_scenario(self) -> None:
        result = find_fewest_route_scenario(self.scenario_rows)

        self.assertEqual(result["route_count"], "2")

    def test_find_best_objective_scenario(self) -> None:
        result = find_best_objective_scenario(self.scenario_rows)

        self.assertEqual(result["method"], "savings")

    def test_build_experiment_report_includes_summary_and_tables(self) -> None:
        report = build_experiment_report(self.scenario_rows, self.route_rows)

        self.assertIn("# Vehicle Routing Experiment Report", report)
        self.assertIn("Lowest-distance capacity scenario", report)
        self.assertIn("Best lateness-aware objective", report)
        self.assertIn("| method | vehicle_capacity | route_count", report)
        self.assertIn("DEPOT -> C001 -> C002 -> DEPOT", report)

    def test_write_experiment_report_creates_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            scenarios_path = directory_path / "scenarios.csv"
            routes_path = directory_path / "routes.csv"
            output_path = directory_path / "report.md"
            scenarios_path.write_text(
                "method,vehicle_capacity,route_count,total_distance,total_lateness,late_stops,on_time_rate,objective_value,average_utilization,runtime_ms\n"
                "savings,50,2,474.83,2.0,1,0.95,494.83,0.93,0.436\n",
                encoding="utf-8",
            )
            routes_path.write_text(
                "vehicle_id,customer_count,load,distance,route\n"
                "1,2,9,20.5,DEPOT -> C001 -> C002 -> DEPOT\n",
                encoding="utf-8",
            )

            write_experiment_report(scenarios_path, routes_path, output_path)

            self.assertTrue(output_path.exists())
            self.assertIn("Vehicle Routing Experiment Report", output_path.read_text())


if __name__ == "__main__":
    unittest.main()
