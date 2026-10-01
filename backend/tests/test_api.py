from fastapi.testclient import TestClient
from app.main import app
def test_health_and_validation():
    with TestClient(app) as c:
        assert c.get('/api/health').json()['status']=='ok'
        assert c.post('/api/complaints/analyze',json={'complaint_text':'no'}).status_code==400
