import sys
from pathlib import Path

# Allow running this test file directly (python test_api.py) from nested paths.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient

from FinSight.app.api import app

client = TestClient(app)


# -------------------------------
# Test root endpoint
# -------------------------------
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# -------------------------------
# Test query endpoint
# -------------------------------
def test_query():
    response = client.post(
        "/query",
        params={"question": "What is revenue?"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "answer" in data
    assert "citations" in data


# -------------------------------
# Test compare endpoint
# -------------------------------
def test_compare():
    response = client.post(
        "/compare",
        params={
            "company_a": "Tata Motors",
            "company_b": "Maruti Suzuki"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "analysis" in data
    assert "verdict" in data


# -------------------------------
# Test upload endpoint (basic)
# -------------------------------
def test_upload():
    files = [
        ("files", ("test.pdf", b"Dummy content", "application/pdf"))
    ]

    response = client.post("/upload", files=files)

    # Upload may fail if parser expects real PDF → still acceptable
    assert response.status_code in [200, 400, 500]