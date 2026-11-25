-- MariaDB integration tests. Run after schema.sql; creates and removes isolated ZZ_TEST fixtures.
USE apartment_mgmt;
DELIMITER $$
CREATE PROCEDURE run_negative_tests(IN p_occupied INT, IN p_vacant INT, IN p_charge BIGINT, IN p_complaint BIGINT)
BEGIN
  DECLARE rejected BOOLEAN DEFAULT FALSE;
  -- Duplicate apartment/month charge must be rejected by UNIQUE.
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected=TRUE;
    INSERT INTO maintenance_charge(apartment_id,charge_month,amount,due_date)
      SELECT apartment_id,charge_month,amount,due_date FROM maintenance_charge WHERE charge_id=p_charge;
  END;
  IF NOT rejected THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='TEST FAILED: duplicate apartment-month charge accepted'; END IF;
  -- Vacant apartment cannot register a complaint.
  SET rejected=FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected=TRUE;
    INSERT INTO complaint(apartment_id,category,description,complaint_date)
      VALUES(p_vacant,'Water','Negative test',CURRENT_DATE());
  END;
  IF NOT rejected THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='TEST FAILED: vacant apartment complaint accepted'; END IF;
  -- Future complaint date must be rejected.
  SET rejected=FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected=TRUE;
    INSERT INTO complaint(apartment_id,category,description,complaint_date)
      VALUES(p_occupied,'Water','Future date negative test',CURRENT_DATE()+INTERVAL 1 DAY);
  END;
  IF NOT rejected THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='TEST FAILED: future complaint accepted'; END IF;
  -- Direct Open -> Resolved transition must be rejected.
  SET rejected=FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected=TRUE;
    UPDATE complaint SET status='Resolved' WHERE complaint_id=p_complaint;
  END;
  IF NOT rejected THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='TEST FAILED: invalid complaint transition accepted'; END IF;
  -- Payment greater than the monthly charge must be rejected.
  SET rejected=FALSE;
  BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET rejected=TRUE;
    INSERT INTO payment(charge_id,amount_paid,reference_no) VALUES(p_charge,1001,'ZZ-OVERPAY-TEST');
  END;
  IF NOT rejected THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='TEST FAILED: overpayment accepted'; END IF;
END$$
DELIMITER ;

INSERT INTO block(block_name,floors) VALUES('ZZ_TEST',1);
SET @test_block=LAST_INSERT_ID();
INSERT INTO apartment(block_id,apartment_no,floor_no,apartment_type,occupancy_status) VALUES
(@test_block,'T-01',1,'2BHK','Occupied'),(@test_block,'T-02',1,'2BHK','Vacant');
SET @test_occupied=LAST_INSERT_ID();
SET @test_vacant=@test_occupied+1;
INSERT INTO resident(full_name,apartment_id,phone) VALUES('ZZ Test Resident',@test_occupied,'9876500001');
INSERT INTO maintenance_charge(apartment_id,charge_month,amount,due_date) VALUES(@test_occupied,'2099-01-01',1000,'2099-01-10');
SET @test_charge=LAST_INSERT_ID();
INSERT INTO complaint(apartment_id,category,description,complaint_date) VALUES(@test_occupied,'Water','ZZ test complaint',CURRENT_DATE());
SET @test_complaint=LAST_INSERT_ID();
CALL run_negative_tests(@test_occupied,@test_vacant,@test_charge,@test_complaint);
SELECT 'PASS: duplicate charge, vacant complaint, future complaint, invalid transition, and overpayment all rejected' AS test_result;
DROP PROCEDURE run_negative_tests;
DELETE FROM complaint_update WHERE complaint_id=@test_complaint;
DELETE FROM complaint WHERE complaint_id=@test_complaint;
DELETE FROM payment WHERE charge_id=@test_charge;
DELETE FROM maintenance_charge WHERE charge_id=@test_charge;
DELETE FROM resident WHERE apartment_id=@test_occupied;
DELETE FROM apartment WHERE block_id=@test_block;
DELETE FROM block WHERE block_id=@test_block;
