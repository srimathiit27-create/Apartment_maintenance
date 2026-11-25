# Software cost estimation
## Basic COCOMO (illustrative)
Assume 4.0 KLOC, organic mode. Effort = 2.4 × KLOC^1.05 = 2.4 × 4^1.05 ≈ 10.2 person-months. Schedule = 2.5 × Effort^0.38 ≈ 6.0 months. Average team size ≈ 1.7 people. This is an academic estimate; actual KLOC and mode should be recalibrated after implementation sizing.
## Function point estimate (illustrative)
| Function type | Count | Average weight | FP |
|---|---:|---:|---:|
| External inputs | 8 | 4 | 32 |
| External outputs | 6 | 5 | 30 |
| External inquiries | 5 | 4 | 20 |
| Internal logical files | 7 | 10 | 70 |
| External interfaces | 2 | 7 | 14 |
| **Unadjusted FP** | | | **166** |
Assumed value adjustment factor 1.00 gives 166 adjusted FP. Counts are planning assumptions, not measured industry-certified function points.
