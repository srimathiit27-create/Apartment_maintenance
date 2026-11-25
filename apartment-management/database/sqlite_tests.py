import sqlite3
from pathlib import Path
DB=Path(__file__).with_name('apartment_demo.sqlite'); c=sqlite3.connect(DB); c.execute('PRAGMA foreign_keys=ON')
checks=[]
def check(name,fn):
 try: fn(); checks.append((name,'PASS'))
 except Exception as e: checks.append((name,'FAIL: '+str(e)))
def rejects(sql,args=()):
 try:c.execute(sql,args); c.rollback(); raise AssertionError('invalid data was accepted')
 except sqlite3.IntegrityError:c.rollback()
def dup(): rejects("INSERT INTO maintenance_charge(apartment_id,charge_month,amount,due_date) VALUES(1,'2026-01-01',1000,'2026-01-10')")
def fk(): rejects("INSERT INTO resident(full_name,apartment_id,phone) VALUES('bad',99999,'9999999999')")
def no_overpay():
 cid,amt=c.execute('select charge_id,amount from maintenance_charge limit 1').fetchone(); rejects('INSERT INTO payment(charge_id,amount_paid,paid_at,reference_no) VALUES(?,?,?,?)',(cid,amt+1,'2026-11-16','TEST-OVER'))
def counts():
 assert c.execute('select count(*) from block').fetchone()[0]==4
 assert c.execute('select count(*) from apartment').fetchone()[0]==200
 assert c.execute('select count(*) from complaint').fetchone()[0]>=1500
def vacant_resident():
 aid=c.execute("select apartment_id from apartment where occupancy_status='Vacant' limit 1").fetchone()[0]
 rejects("INSERT INTO resident(full_name,apartment_id,phone) VALUES('vacant',?,'9876500000')",(aid,))
def vacant_complaint():
 aid=c.execute("select apartment_id from apartment where occupancy_status='Vacant' limit 1").fetchone()[0]
 rejects("INSERT INTO complaint(apartment_id,category,description,complaint_date) VALUES(?,'Water','vacant','2026-11-16')",(aid,))
def future_complaint():
 aid=c.execute("select apartment_id from resident limit 1").fetchone()[0]
 rejects("INSERT INTO complaint(apartment_id,category,description,complaint_date) VALUES(?,'Water','future','2999-01-01')",(aid,))
def status_audit():
 row=c.execute("select complaint_id,status from complaint where status='Open' limit 1").fetchone()
 if not row: raise AssertionError('No open complaint fixture')
 cid,_=row; rejects("UPDATE complaint SET status='Resolved' WHERE complaint_id=?",(cid,))
 c.execute("UPDATE complaint SET status='In Progress' WHERE complaint_id=?",(cid,)); c.commit()
 c.execute("UPDATE complaint SET status='Resolved' WHERE complaint_id=?",(cid,)); c.commit()
 assert c.execute("select count(*) from complaint_update where complaint_id=? and new_status in ('In Progress','Resolved')",(cid,)).fetchone()[0]>=2
check('unique apartment-month charge',dup);check('foreign key rejects orphan resident',fk);check('overpayment rejected',no_overpay);check('vacant apartment cannot have resident',vacant_resident);check('vacant apartment cannot complain',vacant_complaint);check('future complaint rejected',future_complaint);check('forward-only complaint transitions and audit history',status_audit);check('seed volume checks',counts)
for x in checks: print(*x,sep=': ')
assert all(s=='PASS' for _,s in checks)
