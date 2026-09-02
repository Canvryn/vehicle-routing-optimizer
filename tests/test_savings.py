import unittest

from src.distance import Location, build_distance_matrix
from src.savings import calculate_savings, solve_clarke_wright_savings
from src.validate import validate_routes


class SavingsHeuristicTests(unittest.TestCase):
    def test_calculate_savings_orders_pairs_by_descending_savings(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customers = [
            Location("C001", 1, 0, 1),
            Location("C002", 2, 0, 1),
            Location("C003", 10, 0, 1),
        ]
        matrix = build_distance_matrix([depot, *customers])

        savings = calculate_savings(depot, customers, matrix)

        self.assertGreaterEqual(savings[0][0], savings[-1][0])
        self.assertEqual(len(savings), 3)

    def test_savings_solution_is_feasible(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
            Location("C002", 2, 0, 5),
            Location("C003", 10, 0, 6),
            Location("C004", 11, 0, 3),
        ]

        routes = solve_clarke_wright_savings(locations, vehicle_capacity=10)
        report = validate_routes(locations, routes, vehicle_capacity=10)

        self.assertTrue(report.is_feasible)
        self.assertEqual(report.total_visited_customers, 4)

    def test_savings_rejects_oversized_customer(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 11),
        ]

        with self.assertRaisesRegex(ValueError, "exceed vehicle capacity"):
            solve_clarke_wright_savings(locations, vehicle_capacity=10)


if __name__ == "__main__":
    unittest.main()

