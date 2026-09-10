import tempfile
import unittest
from pathlib import Path

from src.generate_data import (
    SCENARIO_PRESETS,
    generate_customers,
    generate_preset_customers,
    write_customers,
)


class GenerateDataTests(unittest.TestCase):
    def test_generate_customers_includes_depot_and_requested_customer_count(self) -> None:
        rows = generate_customers(customer_count=3, seed=1)

        self.assertEqual(rows[0]["location_id"], "DEPOT")
        self.assertEqual(len(rows), 4)

    def test_generate_customers_respects_demand_bounds(self) -> None:
        rows = generate_customers(customer_count=5, seed=1, min_demand=6, max_demand=8)
        demands = [int(row["demand"]) for row in rows if row["location_id"] != "DEPOT"]

        self.assertTrue(all(6 <= demand <= 8 for demand in demands))

    def test_generate_preset_customers_uses_named_scenario_size(self) -> None:
        rows = generate_preset_customers("small")

        self.assertEqual(len(rows), SCENARIO_PRESETS["small"].customer_count + 1)

    def test_generate_preset_customers_rejects_unknown_name(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown scenario preset"):
            generate_preset_customers("unknown")

    def test_write_customers_creates_csv(self) -> None:
        rows = generate_customers(customer_count=1, seed=1)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "customers.csv"
            write_customers(rows, output_path)
            contents = output_path.read_text(encoding="utf-8")

        self.assertIn("location_id,x,y,demand", contents)
        self.assertIn("DEPOT", contents)


if __name__ == "__main__":
    unittest.main()

