# Software Requirements Specification (SRS)
## 1. Purpose and scope
ApartmentCare manages blocks, apartments, residents, monthly maintenance charges, payments and facility complaints. It supports resident self-service, administrative complaint triage and data analysis.
## 2. Actors
- Resident: views own dues, records a payment and registers/tracks complaints.
- Association administrator: maintains records, assigns complaints, advances status and reviews reports.
- Analyst: retrieves operational data and produces EDA/visualizations.
## 3. Functional requirements
FR-01 maintain resident contact records; FR-02 maintain apartment/block/occupancy; FR-03 issue one charge per apartment/month; FR-04 accept partial/full payments; FR-05 derive Paid/Partial/Pending/Overdue; FR-06 register dated category-based complaints; FR-07 enforce Open → In Progress → Resolved; FR-08 audit status changes; FR-09 produce dues and complaint reports; FR-10 preprocess and visualize data.
## 4. Non-functional requirements
Referential integrity, auditable updates, transactional writes, responsive UI, validation, accessibility, maintainable layered Java code, reproducible analytics.
## 5. Business rules
Unique(apartment_id, charge_month); payment sum cannot exceed charge; overdue is unpaid balance after due date; no resident/complaint for vacant apartment; complaint date not future; resolved complaint stores date and elapsed days; no backward/reopened status.
## 6. Assumptions and limitations
The static website uses localStorage and simulated payment records; it is a front-end demonstration, not a production payment gateway or authenticated multi-user portal. MariaDB schema is authoritative; SQLite fixture supports offline reproducible testing.
