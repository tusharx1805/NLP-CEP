from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from collections import Counter
import sqlite3,csv,io,json,joblib
from .services.nlp import analyze

BASE=Path(__file__).resolve().parents[2]; DB=BASE/'data'/'complaints.db'
app=FastAPI(title='Noise Pollution Analytics')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
class Complaint(BaseModel):
    name:str='Anonymous'; email:str=''; location:str=''; area:str=''; complaint_text:str; date:str=''; time:str=''
def conn():
    DB.parent.mkdir(exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    with conn() as c:
        c.execute('CREATE TABLE IF NOT EXISTS complaints(id INTEGER PRIMARY KEY,name TEXT,email TEXT,location TEXT,area TEXT,complaint_text TEXT,processed_text TEXT,noise_source TEXT,sentiment TEXT,sentiment_score REAL,severity TEXT,severity_score REAL,is_urgent INTEGER,keywords TEXT,date TEXT,time TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT UNIQUE,password TEXT,role TEXT)')
@app.on_event('startup')
def startup(): init()
def infer(text):
    m=BASE/'models'/'noise_source_model.pkl'; v=BASE/'models'/'tfidf_vectorizer.pkl'
    try: model,vectorizer=(joblib.load(m),joblib.load(v)) if m.exists() and v.exists() else (None,None)
    except Exception: model,vectorizer=None,None
    return analyze(text,model,vectorizer)
def rows(area='',source='',severity='',sentiment_filter='',search=''):
    q='SELECT * FROM complaints WHERE 1=1';args=[]
    for col,val in [('area',area),('noise_source',source),('severity',severity),('sentiment',sentiment_filter)]:
        if val:q+=f' AND {col}=?';args.append(val)
    if search:q+=' AND complaint_text LIKE ?';args.append('%'+search+'%')
    q+=' ORDER BY date DESC,id DESC'
    with conn() as c: out=[dict(r) for r in c.execute(q,args)]
    for x in out:x['keywords']=json.loads(x['keywords'] or '[]');x['is_urgent']=bool(x['is_urgent'])
    return out
@app.get('/api/health')
def health():return {'status':'ok'}
@app.post('/api/complaints/analyze')
def preview(x:Complaint):
    if len(x.complaint_text.strip())<8:raise HTTPException(400,'Please describe the noise in at least 8 characters.')
    return infer(x.complaint_text)
@app.post('/api/complaints')
def create(x:Complaint):
    if len(x.complaint_text.strip())<8:raise HTTPException(400,'Please describe the noise in at least 8 characters.')
    if x.email and ('@' not in x.email or '.' not in x.email.rsplit('@',1)[-1]):raise HTTPException(400,'Enter a valid email address.')
    if x.date:
        try: from datetime import date; date.fromisoformat(x.date)
        except ValueError:raise HTTPException(400,'Date must use YYYY-MM-DD format.')
    a=infer(x.complaint_text)
    with conn() as c:
        cur=c.execute('INSERT INTO complaints(name,email,location,area,complaint_text,processed_text,noise_source,sentiment,sentiment_score,severity,severity_score,is_urgent,keywords,date,time) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(x.name,x.email,x.location,x.area,x.complaint_text,a['processed_text'],a['noise_source'],a['sentiment'],a['sentiment_score'],a['severity'],a['severity_score'],int(a['is_urgent']),json.dumps(a['keywords']),x.date,x.time)); a['id']=cur.lastrowid
    return {**x.model_dump(),**a}
@app.get('/api/complaints')
def listing(area:str='',source:str='',severity:str='',sentiment_filter:str='',search:str=''):return rows(area,source,severity,sentiment_filter,search)
@app.get('/api/complaints/{id}')
def detail(id:int):
    r=next((x for x in rows() if x['id']==id),None)
    if not r:raise HTTPException(404,'Complaint not found')
    r['explanation']=infer(r['complaint_text'])['explanation'];return r
def group(k):return [{'name':n,'count':v} for n,v in Counter(x[k] or 'Unknown' for x in rows()).most_common()]
@app.get('/api/analytics/summary')
def summary():
    rs=rows();return {'total':len(rs),'urgent':sum(x['is_urgent'] for x in rs),'high_critical':sum(x['severity'] in ('HIGH','CRITICAL') for x in rs),'top_source':Counter(x['noise_source'] for x in rs).most_common(1)[0][0] if rs else '—','demo_dataset':True}
@app.get('/api/analytics/by-source')
def sources():return group('noise_source')
@app.get('/api/analytics/by-area')
def areas():return group('area')
@app.get('/api/analytics/by-severity')
def severities():return group('severity')
@app.get('/api/analytics/sentiment')
def sentiments():return group('sentiment')
@app.get('/api/analytics/trends')
def trends():return [{'name':n,'count':v} for n,v in sorted(Counter(x['date'] or 'Undated' for x in rows()).items())]
@app.get('/api/complaints/export')
def export(area:str='',source:str='',severity:str='',sentiment_filter:str='',search:str=''):
    out=io.StringIO();w=csv.writer(out);w.writerow(['ID','Date','Area','Complaint','Noise Source','Sentiment','Severity','Urgent'])
    for x in rows(area,source,severity,sentiment_filter,search):w.writerow([x['id'],x['date'],x['area'],x['complaint_text'],x['noise_source'],x['sentiment'],x['severity'],'Yes' if x['is_urgent'] else 'No'])
    return StreamingResponse(iter([out.getvalue()]),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=complaints.csv'})
class Login(BaseModel):email:str;password:str
@app.post('/api/auth/login')
def login(x:Login):
    if (x.email,x.password)==('admin@demo.local','admin123'):return {'name':'Demo Admin','role':'admin'}
    with conn() as c:r=c.execute('SELECT name,role,password FROM users WHERE email=?',(x.email.lower(),)).fetchone()
    if r and r['password']==__import__('hashlib').sha256(x.password.encode()).hexdigest():return {'name':r['name'],'role':r['role']}
    raise HTTPException(401,'Invalid demo login. Use admin@demo.local / admin123.')
@app.post('/api/auth/register')
def register(x:Login):
    if '@' not in x.email or len(x.password)<6:raise HTTPException(400,'Enter a valid email and a password of at least 6 characters.')
    try:
        with conn() as c:c.execute('INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)',(x.email.split('@')[0],x.email.lower(),__import__('hashlib').sha256(x.password.encode()).hexdigest(),'citizen'))
    except sqlite3.IntegrityError:raise HTTPException(409,'An account with this email already exists.')
    return {'name':x.email.split('@')[0],'role':'citizen'}
