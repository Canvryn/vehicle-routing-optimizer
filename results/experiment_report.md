# Vehicle Routing Experiment Report

## Summary

- Baseline route plan uses 3 routes.
- Baseline route plan travels 518.77 distance units.
- Baseline route plan serves 93 units of demand.
- Lowest-distance capacity scenario: capacity 50 with total distance 474.83.
- Fewest-route capacity scenario: capacity 50 using 2 routes.

## Scenario Comparison

| vehicle_capacity | route_count | total_distance | average_utilization | runtime_ms |
| --- | --- | --- | --- | --- |
| 25 | 4 | 685.02 | 0.93 | 0.564 |
| 30 | 4 | 716.31 | 0.775 | 0.494 |
| 40 | 3 | 518.77 | 0.775 | 0.499 |
| 50 | 2 | 474.83 | 0.93 | 0.522 |

## Baseline Routes

| vehicle_id | customer_count | load | distance | route |
| --- | --- | --- | --- | --- |
| 1 | 9 | 40 | 209.36 | DEPOT -> C007 -> C005 -> C020 -> C010 -> C006 -> C012 -> C003 -> C017 -> C013 -> DEPOT |
| 2 | 9 | 37 | 185.47 | DEPOT -> C019 -> C009 -> C018 -> C015 -> C008 -> C016 -> C001 -> C004 -> C002 -> DEPOT |
| 3 | 2 | 16 | 123.94 | DEPOT -> C014 -> C011 -> DEPOT |

## Interpretation

Increasing vehicle capacity generally reduces the number of routes, but the nearest-neighbor heuristic can still produce non-monotonic distance changes because early greedy choices affect later routing options. This motivates comparing the baseline against a solver-based optimization model in a future phase.
