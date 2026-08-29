import unittest

from src.distance import Location
from src.heuristic import Route, solve_nearest_neighbor
from src.validate import format_feasibility_report, validate_routes


class RouteValidationTests(unittest.TestCase):
    def test_validate_routes_accepts_feasible_solution(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
        ]
        routes = solve_nearest_neighbor(locations, vehicle_capacity=10)

        report = validate_routes(locations, routes, vehicle_capacity=10)

        self.assertTrue(report.is_feasible)
        self.assertEqual(report.customer_count, 2)
        self.assertEqual(report.total_visited_customers, 2)

    def test_validate_routes_detects_capacity_violation(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customer = Location("C001", 1, 0, 8)
        route = Route(vehicle_id=1, stops=[depot, customer, depot], load=8, distance=2)

        report = validate_routes([depot, customer], [route], vehicle_capacity=5)

        self.assertFalse(report.is_feasible)
        self.assertIn("capacity", [violation.rule for violation in report.violations])

    def test_validate_routes_detects_missing_and_duplicate_customers(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        first = Location("C001", 1, 0, 4)
        second = Location("C002", 2, 0, 5)
        route = Route(
            vehicle_id=1,
            stops=[depot, first, first, depot],
            load=8,
            distance=4,
        )

        report = validate_routes([depot, first, second], [route], vehicle_capacity=10)
        rules = [violation.rule for violation in report.violations]

        self.assertFalse(report.is_feasible)
        self.assertIn("missing_customer", rules)
        self.assertIn("duplicate_customer", rules)

    def test_validate_routes_detects_route_not_returning_to_depot(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customer = Location("C001", 1, 0, 4)
        route = Route(vehicle_id=1, stops=[depot, customer], load=4, distance=1)

        report = validate_routes([depot, customer], [route], vehicle_capacity=10)

        self.assertFalse(report.is_feasible)
        self.assertIn("depot_return", [violation.rule for violation in report.violations])

    def test_format_feasibility_report_lists_violations(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customer = Location("C001", 1, 0, 8)
        route = Route(vehicle_id=1, stops=[depot, customer, depot], load=8, distance=2)
        report = validate_routes([depot, customer], [route], vehicle_capacity=5)

        formatted = format_feasibility_report(report)

        self.assertIn("Solution status: infeasible", formatted)
        self.assertIn("Violations:", formatted)
        self.assertIn("capacity", formatted)


if __name__ == "__main__":
    unittest.main()

