import tempfile
import unittest
from pathlib import Path

from src.distance import Location
from src.heuristic import (
    route_summary_rows,
    solve_nearest_neighbor,
    write_route_map_svg,
    write_route_summary,
)


class HeuristicTests(unittest.TestCase):
    def test_nearest_neighbor_visits_each_customer_once(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
            Location("C003", 10, 0, 6),
        ]

        routes = solve_nearest_neighbor(locations, vehicle_capacity=10)
        visited = [
            stop.location_id
            for route in routes
            for stop in route.stops
            if stop.location_id != "DEPOT"
        ]

        self.assertEqual(sorted(visited), ["C001", "C002", "C003"])
        self.assertTrue(all(route.load <= 10 for route in routes))

    def test_nearest_neighbor_rejects_oversized_customer(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 11),
        ]

        with self.assertRaisesRegex(ValueError, "exceed vehicle capacity"):
            solve_nearest_neighbor(locations, vehicle_capacity=10)

    def test_route_summary_rows_include_metrics_and_path(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
        ]

        routes = solve_nearest_neighbor(locations, vehicle_capacity=10)
        rows = route_summary_rows(routes)

        self.assertEqual(rows[0]["vehicle_id"], 1)
        self.assertEqual(rows[0]["customer_count"], 2)
        self.assertEqual(rows[0]["load"], 9)
        self.assertIn("DEPOT -> C001 -> C002 -> DEPOT", rows[0]["route"])

    def test_write_route_summary_creates_csv(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
        ]
        routes = solve_nearest_neighbor(locations, vehicle_capacity=10)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "summary.csv"
            write_route_summary(routes, output_path)

            contents = output_path.read_text(encoding="utf-8")

        self.assertIn("vehicle_id,customer_count,load,distance,route", contents)
        self.assertIn("DEPOT -> C001 -> DEPOT", contents)

    def test_write_route_map_svg_includes_legend_and_demand_labels(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
        ]
        routes = solve_nearest_neighbor(locations, vehicle_capacity=10)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "route_map.svg"
            write_route_map_svg(locations, routes, output_path)
            contents = output_path.read_text(encoding="utf-8")

        self.assertIn("Route Legend", contents)
        self.assertIn("Vehicle 1: load 4, dist", contents)
        self.assertIn("C001 d=4", contents)


if __name__ == "__main__":
    unittest.main()
