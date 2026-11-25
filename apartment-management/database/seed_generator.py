# Deterministic sample data generator; creates SQLite fixture and CSV exports.
import sqlite3, random, csv
from pathlib import Path
from datetime import date, timedelta
import calendar
ROOT=Path(__file__).resolve().parent
random.seed(20261116)
DB=ROOT/'apartment_demo.sqlite'
if DB.exists(): DB.unlink()
c=sqlite3.connect(DB); c.execute('PRAGMA foreign_keys=ON')
c.executescript('''
CREATE TABLE block(block_id INTEGER PRIMARY KEY,block_name TEXT UNIQUE,floors INTEGER);
CREATE TABLE apartment(apartment_id INTEGER PRIMARY KEY,block_id INTEGER,apartment_no TEXT,floor_no INTEGER,apartment_type TEXT,occupancy_status TEXT,UNIQUE(block_id,apartment_no),FOREIGN KEY(block_id) REFERENCES block);
CREATE TABLE resident(resident_id INTEGER PRIMARY KEY,full_name TEXT,apartment_id INTEGER UNIQUE,phone TEXT,email TEXT,FOREIGN KEY(apartment_id) REFERENCES apartment);
CREATE TABLE maintenance_charge(charge_id INTEGER PRIMARY KEY,apartment_id INTEGER,charge_month TEXT,amount REAL,due_date TEXT,UNIQUE(apartment_id,charge_month),FOREIGN KEY(apartment_id) REFERENCES apartment);
CREATE TABLE payment(payment_id INTEGER PRIMARY KEY,charge_id INTEGER,amount_paid REAL,paid_at TEXT,reference_no TEXT UNIQUE,FOREIGN KEY(charge_id) REFERENCES maintenance_charge);
CREATE TABLE complaint(complaint_id INTEGER PRIMARY KEY,apartment_id INTEGER,category TEXT,description TEXT,complaint_date TEXT,status TEXT,assigned_to TEXT,resolution_date TEXT,resolution_days INTEGER,FOREIGN KEY(apartment_id) REFERENCES apartment);
CREATE TABLE complaint_update(update_id INTEGER PRIMARY KEY,complaint_id INTEGER,old_status TEXT,new_status TEXT,changed_by TEXT,note TEXT,changed_at TEXT,FOREIGN KEY(complaint_id) REFERENCES complaint);
''')
c.executescript('''
CREATE TRIGGER payment_limit BEFORE INSERT ON payment WHEN (SELECT COALESCE(SUM(amount_paid),0) FROM payment WHERE charge_id=NEW.charge_id)+NEW.amount_paid > (SELECT amount FROM maintenance_charge WHERE charge_id=NEW.charge_id) BEGIN SELECT RAISE(ABORT,'payment exceeds charge amount'); END;
CREATE TRIGGER resident_occupied BEFORE INSERT ON resident WHEN (SELECT occupancy_status FROM apartment WHERE apartment_id=NEW.apartment_id)<>'Occupied' BEGIN SELECT RAISE(ABORT,'resident requires occupied apartment'); END;
CREATE TRIGGER complaint_occupied BEFORE INSERT ON complaint WHEN (SELECT occupancy_status FROM apartment WHERE apartment_id=NEW.apartment_id)<>'Occupied' BEGIN SELECT RAISE(ABORT,'vacant apartment cannot complain'); END;
CREATE TRIGGER complaint_future BEFORE INSERT ON complaint WHEN NEW.complaint_date>date('now') BEGIN SELECT RAISE(ABORT,'complaint date cannot be future'); END;
CREATE TRIGGER complaint_transition BEFORE UPDATE OF status ON complaint WHEN (OLD.status='Resolved' AND NEW.status<>'Resolved') OR (OLD.status='Open' AND NEW.status='Resolved') OR (OLD.status='In Progress' AND NEW.status='Open') BEGIN SELECT RAISE(ABORT,'invalid complaint status transition'); END;
CREATE TRIGGER complaint_audit AFTER UPDATE OF status ON complaint WHEN OLD.status<>NEW.status BEGIN INSERT INTO complaint_update(complaint_id,old_status,new_status,changed_by,note,changed_at) VALUES(NEW.complaint_id,OLD.status,NEW.status,'test/system','Status changed',datetime('now')); END;
''')
blocks=['A','B','C','D'];
for b in blocks:c.execute('INSERT INTO block VALUES(NULL,?,?)',(b,10))
apt_ids=[]; res_ids=[]
for bi,b in enumerate(blocks,1):
 for n in range(1,51):
  floor=(n-1)//5+1; no=f'{floor:02d}{(n-1)%5+1:02d}'; occ='Occupied' if random.random()<.86 else 'Vacant'
  cur=c.execute('INSERT INTO apartment VALUES(NULL,?,?,?,?,?)',(bi,no,floor,random.choice(['1BHK','2BHK','3BHK']),occ)); aid=cur.lastrowid; apt_ids.append((aid,occ))
  if occ=='Occupied':
   name=f'Resident {aid:03d}'; cur=c.execute('INSERT INTO resident VALUES(NULL,?,?,?,?)',(name,aid,f'9{random.randrange(100000000,999999999)}',f'resident{aid}@example.com')); res_ids.append(aid)
# 12 months charges per apartment; 600+? exactly 2400
charge_ids=[]; today=date(2026,11,16)
for aid,occ in apt_ids:
 for m in range(1,13):
  month=date(2026,m,1); due=month+timedelta(days=9); amount=random.choice([1500,1800,2000,2200,2500]); cur=c.execute('INSERT INTO maintenance_charge VALUES(NULL,?,?,?,?)',(aid,month.isoformat(),amount,due.isoformat())); cid=cur.lastrowid; charge_ids.append((cid,amount,due))
  r=random.random(); paid=amount if r<.66 else (round(amount*.5,2) if r<.75 else 0)
  if paid: c.execute('INSERT INTO payment VALUES(NULL,?,?,?,?)',(cid,paid,(due-timedelta(days=random.randint(0,8))).isoformat(),f'PAY-{cid:06d}'))
# 1600 complaints on occupied apartments
cats=['Water','Electrical','Cleanliness','Lift','Security','Plumbing','Other']; descriptions=['Low water pressure','Corridor light not working','Waste collection delayed','Lift maintenance request','Gate access issue','Pipe leakage','Common area repair']
for i in range(1600):
 aid=random.choice(res_ids); d=today-timedelta(days=random.randint(0,360)); status=random.choices(['Open','In Progress','Resolved'],[.22,.2,.58])[0]; resolution=(d+timedelta(days=random.randint(1,18))) if status=='Resolved' else None
 if resolution and resolution>today: resolution=today
 days=(resolution-d).days if resolution else None; cat=random.choice(cats)
 cur=c.execute('INSERT INTO complaint VALUES(NULL,?,?,?,?,?,?,?,?)',(aid,cat,random.choice(descriptions),d.isoformat(),status,random.choice(['Maintenance Team','Electrician','Plumber','Admin']),resolution.isoformat() if resolution else None,days)); cid=cur.lastrowid
 c.execute('INSERT INTO complaint_update VALUES(NULL,?,?,?,?,?,?)',(cid,None,'Open','Resident','Complaint registered',d.isoformat()))
 if status!='Open': c.execute('INSERT INTO complaint_update VALUES(NULL,?,?,?,?,?,?)',(cid,'Open','In Progress','Admin','Assigned',d.isoformat()))
 if status=='Resolved': c.execute('INSERT INTO complaint_update VALUES(NULL,?,?,?,?,?,?)',(cid,'In Progress','Resolved','Admin','Resolved',resolution.isoformat()))
c.commit()
# CSV exports for analysis and browser demo
for table in ['block','apartment','resident','maintenance_charge','payment','complaint','complaint_update']:
 rows=c.execute(f'SELECT * FROM {table}').fetchall(); cols=[x[1] for x in c.execute(f'PRAGMA table_info({table})')]
 with (ROOT/f'{table}.csv').open('w',newline='') as f:
  wr=csv.writer(f);wr.writerow(cols);wr.writerows(rows)
print(f'SEEDED blocks={c.execute("select count(*) from block").fetchone()[0]} apartments={c.execute("select count(*) from apartment").fetchone()[0]} residents={c.execute("select count(*) from resident").fetchone()[0]} charges={c.execute("select count(*) from maintenance_charge").fetchone()[0]} complaints={c.execute("select count(*) from complaint").fetchone()[0]} payments={c.execute("select count(*) from payment").fetchone()[0]}')
# MariaDB import script (explicit IDs preserve foreign-key relationships).
def sql_value(value):
    if value is None: return 'NULL'
    if isinstance(value, (int, float)): return str(value)
    return "'" + str(value).replace("'", "''") + "'"
lines=['USE apartment_mgmt;','SET FOREIGN_KEY_CHECKS=0;']
for table in ['block','apartment','resident','maintenance_charge','payment','complaint','complaint_update']:
    cols=[x[1] for x in c.execute(f'PRAGMA table_info({table})')]
    for row in c.execute(f'SELECT * FROM {table}'):
        lines.append(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(sql_value(v) for v in row)});")
lines.append('SET FOREIGN_KEY_CHECKS=1;')
(ROOT/'mariadb_seed.sql').write_text('\n'.join(lines)+'\n')
print('MARIADB_SEED_SQL',ROOT/'mariadb_seed.sql',f'{len(lines)-3} inserts')
