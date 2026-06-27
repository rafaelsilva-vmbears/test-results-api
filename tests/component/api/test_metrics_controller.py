
import pytest
from datetime import datetime
from app.infrastructure.security.security import verify_api_key
from app.main import app

def verify_api_key_override():
    return True

@pytest.fixture(autouse=True)
def bypass_auth():
    app.dependency_overrides[verify_api_key] = verify_api_key_override
    yield
    app.dependency_overrides.pop(verify_api_key, None)

def test_get_metrics_summary(client, mock_mongo_adapter):
    """
    GIVEN existing run data
    WHEN calling GET /metrics/summary
    THEN it should return aggregated data
    """
    # Arrange
    base_date = datetime(2023, 1, 15)
    mock_mongo_adapter.get_collection("runs").insert_many([
        {
            "project": "myproj", "environment": "prod", "run_number": 1, "created_at": base_date,
            "total": 10, "passed": 8, "failures": 2, "skipped": 0, "error": 0
        },
        {
            "project": "myproj", "environment": "prod", "run_number": 2, "created_at": base_date,
            "total": 10, "passed": 10, "failures": 0, "skipped": 0, "error": 0
        }
    ])

    # Act
    # Note: Using Brazilian date format as required by validate_date_range
    response = client.get(
        "/metrics/summary",
        params={
            "project": "MyProj", # Case insensitive check
            "environment": "Prod",
            "start_date": "01/01/2023",
            "end_date": "31/01/2023"
        }
    )

    # Assert
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert data["project"] == "myproj"
    assert data["total_runs"] == 2
    assert data["avg_pass_rate"] == 90.0

def test_get_failed_tests_list(client, mock_mongo_adapter):
    """
    GIVEN run data with failures
    WHEN calling GET /metrics/failures
    THEN it should return list of failed tests with details
    """
    # Arrange
    base_date = datetime(2023, 1, 15)
    mock_mongo_adapter.get_collection("runs").insert_one({
        "project": "myproj", "environment": "prod", "run_number": 10, "created_at": base_date,
        "failed_cases": [
            {"name": "test.Fail", "message": "NPE", "status": "failed"}
        ]
    })

    # Act
    response = client.get(
        "/metrics/failures",
        params={
            "project": "MyProj",
            "environment": "Prod",
            "start_date": "01/01/2023",
            "end_date": "31/01/2023"
        }
    )

    # Assert
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test.Fail"
    assert data[0]["run_numbers"] == [10]
