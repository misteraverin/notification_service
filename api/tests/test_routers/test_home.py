from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home():
    response = client.get('/')
    assert response.status_code == 200
    assert 'Hello' in response.text


def test_api_route():
    response = client.get('/api/')
    assert response.status_code == 200
    assert 'Mailing Service' in response.text
