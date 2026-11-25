# Requirements traceability matrix
| Requirement | Database | Java | Website | Python |
|---|---|---|---|---|
| Resident details | resident | ResidentDao | resident portal | join extract |
| Apartment details | block, apartment | model/service extension | building grid | occupancy chart |
| Monthly dues/payments | charge, payment, view | PaymentService | demo payment | dues features/charts |
| Complaint registration | complaint | service boundary | raise complaint | complaint extract |
| Complaint status/audit | trigger, complaint_update | ComplaintService | admin queue | resolution metrics |
| Reports | 3 views + queries | Streams + SQL | KPIs/charts | 12 charts/report |
