import unittest

from src.distance import Location, build_distance_matrix, euclidean_distance


class DistanceTests(unittest.TestCase):
    def test_euclidean_distance_uses_pythagorean_distance(self) -> None:
        first = Location("A", 0, 0)
        second = Location("B", 3, 4)

        self.assertEqual(euclidean_distance(first, second), 5)

    def test_distance_matrix_is_symmetric_and_zero_on_diagonal(self) -> None:
        locations = [Location("A", 0, 0), Location("B", 3, 4)]

        matrix = build_distance_matrix(locations)

        self.assertEqual(matrix["A"]["A"], 0)
        self.assertEqual(matrix["B"]["B"], 0)
        self.assertEqual(matrix["A"]["B"], matrix["B"]["A"])


if __name__ == "__main__":
    unittest.main()
