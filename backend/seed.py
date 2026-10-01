import sys,random,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from app.main import init,conn,infer
import csv
ROOT=Path(__file__).resolve().parents[1];init(); areas=['Kharghar','Panvel','Vashi','Nerul','Belapur','Airoli','Thane','Andheri']
with (ROOT/'data'/'noise_complaints.csv').open(encoding='utf-8',newline='') as f: records=list(csv.DictReader(f))
with conn() as c:
    if not c.execute('select count(*) from complaints').fetchone()[0]:
        for i,r in enumerate(random.Random(7).sample(records,150)):
            t=r['text'];a=infer(t);area=areas[i%len(areas)]
            # Keep known synthetic labels so the first-run demo charts span every source class.
            c.execute('INSERT INTO complaints(name,location,area,complaint_text,processed_text,noise_source,sentiment,sentiment_score,severity,severity_score,is_urgent,keywords,date,time) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',('Demo citizen','Near '+area+' junction',area,t,a['processed_text'],r['noise_source'],r['sentiment'],a['sentiment_score'],r['severity'].upper(),a['severity_score'],int(a['is_urgent']),json.dumps(a['keywords']),f'2026-09-{i%28+1:02d}','22:00'))
print('Seeded 150 synthetic records if database was empty.')
