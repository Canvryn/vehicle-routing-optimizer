import unittest

from src.distance import Location
from src.heuristic import solve_nearest_neighbor


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


if __name__ == "__main__":
    unittest.main()
