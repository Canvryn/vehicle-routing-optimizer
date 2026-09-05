import tempfile
import unittest
from pathlib import Path

from src.distance import Location
from src.heuristic import Route
from src.time_windows import (
    TimeWindow,
    build_default_time_windows,
    evaluate_route_timings,
    timing_summary,
    write_timing_report,
)


class TimeWindowTests(unittest.TestCase):
    def test_default_time_windows_include_depot_and_customers(self) -> None:
        locations = [
            Location("DEPOT", 0, 0, 0),
            Location("C001", 1, 0, 4),
        ]

        windows = build_default_time_windows(locations)

        self.assertEqual(windows["DEPOT"].earliest, 0)
        self.assertGreater(windows["DEPOT"].latest, windows["C001"].latest)
        self.assertGreater(windows["C001"].service_time, 0)

    def test_evaluate_route_timings_calculates_waiting_and_lateness(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customer = Location("C001", 3, 4, 2)
        route = Route(vehicle_id=1, stops=[depot, customer, depot], load=2, distance=10)
        windows = {
            "DEPOT": TimeWindow("DEPOT", earliest=0, latest=100, service_time=0),
            "C001": TimeWindow("C001", earliest=10, latest=12, service_time=5),
        }

        timings = evaluate_route_timings([depot, customer], [route], windows)
        customer_timing = timings[1]

        self.assertEqual(customer_timing.arrival_time, 5)
        self.assertEqual(customer_timing.waiting_time, 5)
        self.assertEqual(customer_timing.lateness, 0)
        self.assertEqual(customer_timing.departure_time, 15)

    def test_timing_summary_counts_late_stops(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customer = Location("C001", 10, 0, 2)
        route = Route(vehicle_id=1, stops=[depot, customer, depot], load=2, distance=20)
        windows = {
            "DEPOT": TimeWindow("DEPOT", earliest=0, latest=100, service_time=0),
            "C001": TimeWindow("C001", earliest=0, latest=5, service_time=0),
        }

        timings = evaluate_route_timings([depot, customer], [route], windows)
        summary = timing_summary(timings)

        self.assertEqual(summary["customer_stops"], 1)
        self.assertEqual(summary["late_stops"], 1)
        self.assertEqual(summary["total_lateness"], 5)
        self.assertEqual(summary["on_time_rate"], 0)

    def test_write_timing_report_creates_csv(self) -> None:
        depot = Location("DEPOT", 0, 0, 0)
        customer = Location("C001", 1, 0, 2)
        route = Route(vehicle_id=1, stops=[depot, customer, depot], load=2, distance=2)
        windows = {
            "DEPOT": TimeWindow("DEPOT", earliest=0, latest=100, service_time=0),
            "C001": TimeWindow("C001", earliest=0, latest=100, service_time=0),
        }
        timings = evaluate_route_timings([depot, customer], [route], windows)

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "timing.csv"
            write_timing_report(timings, output_path)
            contents = output_path.read_text(encoding="utf-8")

        self.assertIn("vehicle_id,location_id,arrival_time", contents)
        self.assertIn("C001", contents)


if __name__ == "__main__":
    unittest.main()

