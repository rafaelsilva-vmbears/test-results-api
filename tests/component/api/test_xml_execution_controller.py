
import pytest
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
    # Safely remove override if it exists (client fixture might have cleared it)
    app.dependency_overrides.pop(verify_api_key, None)
    app.dependency_overrides.pop(verify_read_permission, None)
    app.dependency_overrides.pop(verify_write_permission, None)

def test_process_xml_and_create_execution_success(client, mock_mongo_adapter):
    """
    GIVEN a valid XML file and project parameters
    WHEN calling POST /process-and-save
    THEN it should persist data in the DB and return the ID.
    """
    # Arrange
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="com.example.Test" time="1.0">
        <testcase name="testPass" classname="com.example.Test" time="0.1"/>
        <testcase name="testFail" classname="com.example.Test" time="0.2">
            <failure message="Error"/>
        </testcase>
    </testsuite>
    """
    files = {"file": ("results.xml", xml_content, "text/xml")}
    params = {"project": "ComponentTest", "environment": "UAT", "source": "Jenkins"}

    # Act
    # X-API-Key header is NOT needed because of override
    response = client.post(
        "/xml-execution/process-and-save",
        files=files,
        params=params
    )

    # Assert 1: API Response
    assert response.status_code == 200, f"Response: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["id"] is not None

    # Assert 2: Database Persistence (Wiring Verification)
    # Check if 'runs' collection has the document
    runs = list(mock_mongo_adapter.get_collection("runs").find())
    assert len(runs) == 1
    stored_run = runs[0]

    # Check normalized fields
    assert stored_run["project"] == "componenttest"
    assert stored_run["environment"] == "uat"
    assert stored_run["total"] == 2
    assert stored_run["failures"] == 1

    # Check if 'projects' collection was updated (Repository logic)
    proj = mock_mongo_adapter.get_collection("projects").find_one({"_id": "componenttest"})
    assert proj is not None
    assert proj["total_runs"] == 1
