# Vehicle Routing Experiment Report

## Summary

- Baseline route plan uses 3 routes.
- Baseline route plan travels 518.77 distance units.
- Baseline route plan serves 93 units of demand.
- Lowest-distance capacity scenario: capacity 50 with total distance 431.08.
- Fewest-route capacity scenario: capacity 50 using 2 routes.

## Scenario Comparison

| method | vehicle_capacity | route_count | total_distance | average_utilization | runtime_ms |
| --- | --- | --- | --- | --- | --- |
| nearest_neighbor | 25 | 4 | 685.02 | 0.93 | 0.564 |
| nearest_neighbor | 30 | 4 | 716.31 | 0.775 | 0.501 |
| nearest_neighbor | 40 | 3 | 518.77 | 0.775 | 0.503 |
| nearest_neighbor | 50 | 2 | 474.83 | 0.93 | 0.476 |
| savings | 25 | 4 | 535.53 | 0.93 | 2.823 |
| savings | 30 | 4 | 511.08 | 0.775 | 3.003 |
| savings | 40 | 3 | 445.25 | 0.775 | 2.193 |
| savings | 50 | 2 | 431.08 | 0.93 | 1.671 |

## Baseline Routes

| vehicle_id | customer_count | load | distance | route |
| --- | --- | --- | --- | --- |
| 1 | 9 | 40 | 209.36 | DEPOT -> C007 -> C005 -> C020 -> C010 -> C006 -> C012 -> C003 -> C017 -> C013 -> DEPOT |
| 2 | 9 | 37 | 185.47 | DEPOT -> C019 -> C009 -> C018 -> C015 -> C008 -> C016 -> C001 -> C004 -> C002 -> DEPOT |
| 3 | 2 | 16 | 123.94 | DEPOT -> C014 -> C011 -> DEPOT |

## Interpretation

Increasing vehicle capacity generally reduces the number of routes, but route distance still depends on the construction heuristic. In this sample, the Clarke-Wright savings heuristic improves on the nearest-neighbor baseline because it explicitly evaluates the distance saved by merging single-customer routes. This creates a stronger benchmark for a future solver-based optimization model.
