# Analytics extraction, preprocessing, feature engineering and EDA.
from pathlib import Path
import os, sqlite3, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
ROOT=Path(__file__).resolve().parents[1]; DB=ROOT/'database/apartment_demo.sqlite'; OUT=ROOT/'python/output'; OUT.mkdir(exist_ok=True)
if os.getenv('DB_HOST'):
    import pymysql
    con=pymysql.connect(host=os.getenv('DB_HOST'),port=int(os.getenv('DB_PORT','3306')),user=os.getenv('DB_USER','root'),password=os.getenv('DB_PASSWORD',''),database=os.getenv('DB_NAME','apartment_mgmt'),charset='utf8mb4')
    print('ANALYTICS_SOURCE=MariaDB')
else:
    con=sqlite3.connect(DB)
    print('ANALYTICS_SOURCE=SQLite offline fixture')
df=pd.read_sql_query('''SELECT mc.charge_id,mc.apartment_id,mc.charge_month,mc.amount,mc.due_date,COALESCE(SUM(p.amount_paid),0) paid,a.block_id,b.block_name,a.occupancy_status FROM maintenance_charge mc JOIN apartment a USING(apartment_id) JOIN block b USING(block_id) LEFT JOIN payment p USING(charge_id) GROUP BY mc.charge_id''',con)
co=pd.read_sql_query('''SELECT c.*,b.block_name FROM complaint c JOIN apartment a USING(apartment_id) JOIN block b USING(block_id)''',con)
# cleaning and feature engineering
for col in ['charge_month','due_date']: df[col]=pd.to_datetime(df[col],errors='coerce')
for col in ['complaint_date','resolution_date']: co[col]=pd.to_datetime(co[col],errors='coerce')
df['balance']=(df.amount-df.paid).clip(lower=0); today=pd.Timestamp('2026-11-16'); df['days_pending']=(today-df.due_date).dt.days.clip(lower=0).where(df.balance>0,0); df['overdue_months']=(df.days_pending/30).astype(int); df['payment_status']='Pending'; df.loc[df.paid>0,'payment_status']='Partial'; df.loc[(df.balance>0)&(df.due_date<today),'payment_status']='Overdue'; df.loc[df.balance==0,'payment_status']='Paid'
co['resolution_time']=co.resolution_days.fillna((today-co.complaint_date).dt.days); co['sla_breach']=((co.status!='Resolved')&(co.complaint_date<today-pd.Timedelta(days=7)))|((co.status=='Resolved')&(co.resolution_days>7))
# Save cleaned extracts
for name,data in [('maintenance_clean.csv',df),('complaints_clean.csv',co)]: data.to_csv(OUT/name,index=False)
sns.set_theme(style='whitegrid'); charts=[]
def chart(name,fn):
 plt.figure(figsize=(9,5)); fn(); plt.tight_layout(); plt.savefig(OUT/f'{name}.png',dpi=130); plt.close(); charts.append(name)
chart('01_dues_by_block',lambda:sns.barplot(data=df.groupby('block_name',as_index=False).balance.sum(),x='block_name',y='balance',color=sns.color_palette()[0]).set(title='Outstanding dues by block',xlabel='Block',ylabel='Balance'))
chart('02_monthly_collection_trend',lambda:sns.lineplot(data=df.assign(month=df.charge_month.dt.strftime('%Y-%m')).groupby('month',as_index=False).paid.sum(),x='month',y='paid',marker='o').set(title='Monthly collection trend',xlabel='Month',ylabel='Collected'))
chart('03_complaints_by_category',lambda:sns.countplot(data=co,x='category',order=co.category.value_counts().index,color=sns.color_palette()[0]).set(title='Complaints by category',xlabel='Category',ylabel='Count'))
chart('04_resolution_time_distribution',lambda:sns.histplot(data=co[co.status=='Resolved'],x='resolution_days',bins=18,kde=True,color=sns.color_palette()[0]).set(title='Resolution-time distribution',xlabel='Days',ylabel='Complaints'))
chart('05_block_category_heatmap',lambda:sns.heatmap(pd.crosstab(co.block_name,co.category),annot=True,fmt='d',cmap='YlOrRd').set(title='Recurring issues: block × category',xlabel='Category',ylabel='Block'))
chart('06_sla_breaches',lambda:sns.countplot(data=co,x='sla_breach',color=sns.color_palette()[0]).set(title='SLA breach count',xlabel='SLA breach',ylabel='Complaints'))
chart('07_payment_status',lambda:sns.countplot(data=df,x='payment_status',order=['Paid','Partial','Pending','Overdue'],color=sns.color_palette()[0]).set(title='Maintenance payment status',xlabel='Status',ylabel='Charges'))
chart('08_occupancy_mix',lambda:sns.countplot(data=pd.read_sql_query('select * from apartment',con),x='occupancy_status',color=sns.color_palette()[0]).set(title='Apartment occupancy',xlabel='Occupancy',ylabel='Apartments'))
chart('09_complaints_over_time',lambda:sns.lineplot(data=co.set_index('complaint_date').resample('MS').size().rename('complaints').reset_index(),x='complaint_date',y='complaints').set(title='Complaints over time',xlabel='Month',ylabel='Complaints'))
chart('10_collection_by_block',lambda:sns.barplot(data=df.groupby('block_name',as_index=False).paid.sum(),x='block_name',y='paid',color=sns.color_palette()[0]).set(title='Total collections by block',xlabel='Block',ylabel='Collected'))
chart('11_pending_age',lambda:sns.histplot(data=df[df.balance>0],x='days_pending',bins=20,color=sns.color_palette()[0]).set(title='Age of pending dues',xlabel='Days since due date',ylabel='Charges'))
chart('12_resolution_by_category',lambda:sns.barplot(data=co[co.status=='Resolved'].groupby('category',as_index=False).resolution_days.mean(),x='category',y='resolution_days',color=sns.color_palette()[0]).set(title='Average resolution time by category',xlabel='Category',ylabel='Days'))
# reproducible metrics/report
metrics={'apartments':int(pd.read_sql_query('select count(*) n from apartment',con).iloc[0,0]),'charges':len(df),'complaints':len(co),'collected':round(float(df.paid.sum()),2),'outstanding':round(float(df.balance.sum()),2),'resolved_pct':round(float((co.status=='Resolved').mean()*100),1),'sla_breaches':int(co.sla_breach.sum()),'charts':len(charts)}
report=['# Apartment Management – Data Insights','',f"- Apartments: {metrics['apartments']}",f"- Monthly charge records: {metrics['charges']}",f"- Complaints: {metrics['complaints']}",f"- Total collected: ₹{metrics['collected']:,.2f}",f"- Outstanding balance: ₹{metrics['outstanding']:,.2f}",f"- Complaint resolution rate: {metrics['resolved_pct']}%",f"- SLA breaches (>7 days): {metrics['sla_breaches']}",'', '## Findings',f"- Highest complaint category: {co.category.value_counts().idxmax()} ({co.category.value_counts().max()} reports).",f"- Highest outstanding block: {df.groupby('block_name').balance.sum().idxmax()}.",f"- Mean resolved complaint time: {co.loc[co.status=='Resolved','resolution_days'].mean():.1f} days.",'', '## Charts',*['- '+x+'.png' for x in charts]]
(OUT/'insight_report.md').write_text('\n'.join(report)+'\n'); (OUT/'metrics.json').write_text(__import__('json').dumps(metrics,indent=2)); print('ANALYTICS',metrics); print('CHARTS',len(charts),'saved to',OUT)
