import unittest

from src.distance import Location, build_distance_matrix
from src.heuristic import Route, route_distance
from src.improve import improve_routes_with_two_opt, two_opt_stops
from src.validate import validate_routes


class TwoOptImprovementTests(unittest.TestCase):
    def test_two_opt_does_not_worsen_route_distance(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        stops = [
            depot,
            Location("C001", 0, 10, 1),
            Location("C002", 10, 0, 1),
            Location("C003", 10, 10, 1),
            depot,
        ]
        matrix = build_distance_matrix(stops)

        improved = two_opt_stops(stops, matrix)

        self.assertLessEqual(route_distance(improved, matrix), route_distance(stops, matrix))

    def test_improve_routes_preserves_feasibility_and_load(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customers = [
            Location("C001", 0, 10, 2),
            Location("C002", 10, 0, 3),
            Location("C003", 10, 10, 4),
        ]
        locations = [depot, *customers]
        route = Route(
            vehicle_id=1,
            stops=[depot, customers[0], customers[1], customers[2], depot],
            load=9,
            distance=0,
        )

        improved_routes = improve_routes_with_two_opt(locations, [route])
        report = validate_routes(locations, improved_routes, vehicle_capacity=10)

        self.assertTrue(report.is_feasible)
        self.assertEqual(improved_routes[0].load, 9)
        self.assertEqual(improved_routes[0].stops[0].location_id, "DEPOT")
        self.assertEqual(improved_routes[0].stops[-1].location_id, "DEPOT")


if __name__ == "__main__":
    unittest.main()

