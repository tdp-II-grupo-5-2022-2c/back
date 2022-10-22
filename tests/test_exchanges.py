from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_exchange():
    response = client.post("/exchanges")
    print(response)
    assert response == None
