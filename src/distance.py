from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class Location:
    """A depot or customer location in a two-dimensional service region."""

    location_id: str
    x: float
    y: float
    demand: int = 0


def euclidean_distance(first: Location, second: Location) -> float:
    """Return the Euclidean distance between two locations."""

    return hypot(first.x - second.x, first.y - second.y)


def build_distance_matrix(locations: list[Location]) -> dict[str, dict[str, float]]:
    """Build a nested distance matrix keyed by location id."""

    matrix: dict[str, dict[str, float]] = {}
    for origin in locations:
        matrix[origin.location_id] = {}
        for destination in locations:
            matrix[origin.location_id][destination.location_id] = euclidean_distance(
                origin, destination
            )
    return matrix

