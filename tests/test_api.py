from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert 'entries' in r.json()

def test_translate():
    r = client.post('/translate', json={'text': 'namaskar apa jal', 'debug': True})
    assert r.status_code == 200
    data = r.json()
    assert 'translated_text' in data
    assert data['translated_text'].startswith('नमस्कार')
