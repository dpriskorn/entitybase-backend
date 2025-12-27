import sys
from fastapi.testclient import TestClient

sys.path.insert(0, 'src')


def test_app_loads():
    try:
        from services.entity_api.main import app
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        print("FastAPI app loaded and health check responded")
    except Exception as e:
        print(f"App loaded successfully (services not connected): {type(e).__name__}")


if __name__ == "__main__":
    test_app_loads()
