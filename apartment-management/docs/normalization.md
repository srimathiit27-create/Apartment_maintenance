# Normalization to BCNF
- **1NF:** every column stores one atomic value; payments and complaint updates are separate rows rather than repeating groups.
- **2NF:** each relation has a single-column surrogate primary key; the apartment-month uniqueness key determines charge amount and due date. No non-key attribute depends on part of a composite candidate key.
- **3NF:** resident details depend on resident_id; block name/floors depend on block_id; apartment attributes depend on apartment_id; payment attributes depend on payment_id; complaint attributes depend on complaint_id. Block data is not duplicated in apartment records.
- **BCNF:** every non-trivial functional dependency has a superkey determinant. Candidate keys include block_id, apartment_id, resident_id, charge_id, payment_id, complaint_id and update_id; UNIQUE(apartment_id,charge_month) is a candidate key for maintenance_charge. Views are derived projections/aggregates and do not introduce stored update anomalies.
