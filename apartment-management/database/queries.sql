USE apartment_mgmt;
-- Join: resident and apartment
SELECT r.resident_id,r.full_name,b.block_name,a.apartment_no FROM resident r JOIN apartment a USING(apartment_id) JOIN block b USING(block_id);
-- HAVING: blocks with at least 20 open complaints
SELECT b.block_name,COUNT(*) open_count FROM complaint c JOIN apartment a USING(apartment_id) JOIN block b USING(block_id) WHERE c.status<>'Resolved' GROUP BY b.block_name HAVING COUNT(*)>=20;
-- Subquery: residents with unpaid balance
SELECT full_name FROM resident WHERE apartment_id IN (SELECT apartment_id FROM v_pending_dues);
-- Window function: rank blocks by collected amount
SELECT block_name,collected,DENSE_RANK() OVER(ORDER BY collected DESC) collection_rank FROM (SELECT b.block_name,SUM(p.amount_paid) collected FROM payment p JOIN maintenance_charge mc USING(charge_id) JOIN apartment a USING(apartment_id) JOIN block b USING(block_id) GROUP BY b.block_name) x;
-- Recursive CTE: enumerate floors for each block
WITH RECURSIVE floors(block_id,block_name,floor_no,max_floor) AS (SELECT block_id,block_name,1,floors FROM block UNION ALL SELECT block_id,block_name,floor_no+1,max_floor FROM floors WHERE floor_no<max_floor) SELECT block_name,floor_no FROM floors ORDER BY block_name,floor_no;
-- Reports
SELECT * FROM v_pending_dues ORDER BY due_date;
SELECT status,COUNT(*) FROM complaint GROUP BY status;
SELECT * FROM v_category_complaints ORDER BY total_complaints DESC;
