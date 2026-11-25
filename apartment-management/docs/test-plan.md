# Test plan and execution record
| ID | Scenario | Expected result | Executed result |
|---|---|---|---|
| DB-01 | duplicate apartment-month charge | reject | SQLite fixture constraint PASS |
| DB-02 | orphan resident foreign key | reject | SQLite fixture FK PASS |
| DB-03 | payment above charge | reject | SQLite fixture payment-limit trigger PASS |
| DATA-01 | seeded data volume | 4 blocks, 200 apartments, >=1500 complaints | Executed by seed generator |
| JAVA-01 | eight concurrent attempts to pay same demo charge | exactly one accepted | Java atomic demo PASS; DB JDBC locking requires MariaDB runtime |
| DATA-02 | SQL/Java/Python row-count reconciliation | identical counts | run_all.sh compares 200 apartments, 2,400 charges, 1,600 complaints across SQLite/CSV Java snapshot/Python |
| WEB-01 | page loads, tabs, resident dues, apartment selection, theme | no JS errors | Headless Chromium test |
| PY-01 | analytics | >=11 charts and metrics report | Executed by run_all.sh |

The SQLite fixture is an offline test mirror, not proof that MariaDB triggers have been executed. Apply `database/schema.sql` and run `database/tests.sql` against MariaDB to validate the production DDL/triggers.
