from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .distance import Location, build_distance_matrix
    from .heuristic import Route, format_route, load_locations, route_distance
    from .savings import solve_clarke_wright_savings
except ImportError:
    from distance import Location, build_distance_matrix
    from heuristic import Route, format_route, load_locations, route_distance
    from savings import solve_clarke_wright_savings


def two_opt_stops(
    stops: list[Location], matrix: dict[str, dict[str, float]]
) -> list[Location]:
    """Improve a single depot-bounded route using 2-opt edge swaps."""

    if len(stops) <= 4:
        return stops

    best_stops = stops[:]
    best_distance = route_distance(best_stops, matrix)
    improved = True

    while improved:
        improved = False
        for start in range(1, len(best_stops) - 2):
            for end in range(start + 1, len(best_stops) - 1):
                candidate = (
                    best_stops[:start]
                    + list(reversed(best_stops[start : end + 1]))
                    + best_stops[end + 1 :]
                )
                candidate_distance = route_distance(candidate, matrix)
                if candidate_distance + 1e-9 < best_distance:
                    best_stops = candidate
                    best_distance = candidate_distance
                    improved = True
        stops = best_stops

    return best_stops


def improve_routes_with_two_opt(locations: list[Location], routes: list[Route]) -> list[Route]:
    """Apply 2-opt to each route without changing vehicle assignments."""

    matrix = build_distance_matrix(locations)
    improved_routes: list[Route] = []
    for route in routes:
        improved_stops = two_opt_stops(route.stops, matrix)
        improved_routes.append(
            Route(
                vehicle_id=route.vehicle_id,
                stops=improved_stops,
                load=route.load,
                distance=route_distance(improved_stops, matrix),
            )
        )
    return improved_routes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run savings heuristic plus 2-opt.")
    parser.add_argument("--input", type=Path, default=Path("data/sample_customers.csv"))
    parser.add_argument("--vehicle-capacity", type=int, default=40)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    locations = load_locations(args.input)
    initial_routes = solve_clarke_wright_savings(locations, args.vehicle_capacity)
    improved_routes = improve_routes_with_two_opt(locations, initial_routes)
    initial_distance = sum(route.distance for route in initial_routes)
    improved_distance = sum(route.distance for route in improved_routes)

    print(f"Initial distance: {initial_distance:.2f}")
    print(f"Improved distance: {improved_distance:.2f}")
    print(f"Improvement: {initial_distance - improved_distance:.2f}")
    print()
    for route in improved_routes:
        print(format_route(route))


if __name__ == "__main__":
    main()

