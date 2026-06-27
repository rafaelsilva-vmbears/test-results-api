
import pytest
from datetime import datetime
from bson.objectid import ObjectId
from app.infrastructure.security.security import verify_api_key, verify_read_permission, verify_write_permission
from app.main import app

def verify_api_key_override():
    return True

@pytest.fixture(autouse=True)
def bypass_auth():
    app.dependency_overrides[verify_api_key] = verify_api_key_override
    app.dependency_overrides[verify_read_permission] = verify_api_key_override
    app.dependency_overrides[verify_write_permission] = verify_api_key_override
    yield
    app.dependency_overrides.pop(verify_api_key, None)
    app.dependency_overrides.pop(verify_read_permission, None)
    app.dependency_overrides.pop(verify_write_permission, None)

def test_list_executions(client, mock_mongo_adapter):
    """
    GIVEN existing executions
    WHEN calling GET /executions with date range
    THEN return list of executions
    """
    # Arrange
    base_date = datetime(2023, 1, 15)
    mock_mongo_adapter.get_collection("runs").insert_one({
        "project": "projx",
        "environment": "uat",
        "run_number": 1,
        "created_at": base_date,
        "total": 10,
        "passed": 10,
        "failures": 0,
        "skipped": 0,
        "errors": 0,
        "pass_rate": 100.0,
        "failure_rate": 0.0,
        "skipped_rate": 0.0,
        "test_results": [],
        "failed_cases": []
    })

    # Act
    # /executions prefix defined in executions.py, mapped in main?
    # executions.py says prefix="/executions", main says app.include_router(executions.router)
    # So URL is /executions
    response = client.get(
        "/executions",
        params={
            "project": "ProjX",
            "environment": "UAT",
            "start_date": "01/01/2023",
            "end_date": "31/01/2023"
        }
    )

    # Assert
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert len(data) == 1
    assert data[0]["project"] == "projx"
    assert data[0]["run_number"] == 1

def test_get_execution_by_id_success(client, mock_mongo_adapter):
    """
    GIVEN an execution ID
    WHEN calling GET /executions/{id}
    THEN return the details
    """
    # Arrange
    # Need to insert with a known ObjectId
    oid = ObjectId()
    mock_mongo_adapter.get_collection("runs").insert_one({
        "_id": oid,
        "project": "projy",
        "environment": "qa",
        "run_number": 5,
        "created_at": datetime.now(),
        "total": 100,
        "passed": 95,
        "failures": 5,
        "skipped": 0,
        "errors": 0,
        "pass_rate": 95.0,
        "failure_rate": 5.0,
        "skipped_rate": 0.0,
        "test_results": [],
        "failed_cases": []
    })

    # Act
    response = client.get(f"/executions/{str(oid)}")

    # Assert
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert data["id"] == str(oid)
    assert data["project"] == "projy"

def test_get_execution_by_id_not_found(client, mock_mongo_adapter):
    """
    GIVEN a non-existent ID
    WHEN calling GET /executions/{id}
    THEN return 404
    """
    fake_id = str(ObjectId())
    response = client.get(f"/executions/{fake_id}")

    assert response.status_code == 404
