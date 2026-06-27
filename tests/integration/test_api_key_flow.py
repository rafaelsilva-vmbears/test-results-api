from app.api.v1.routes.admin.admin_api_keys import router as admin_router

# Mock dependencies if necessary, or use real DB if environment allows.
# For this test, we assume a real Mongo connection is possible or we rely on the existing configuration.
# If running locally with Mongo, this should work.

def test_api_key_lifecycle(client):
    master_key_header = {"X-API-Key": "test-master-key"}

    import uuid
    unique_team = f"Test Team {uuid.uuid4()}"

    # 1. Create API Key
    payload = {"team_name": unique_team, "permissions": ["READ"]}
    response = client.post("/admin/api-keys", json=payload, headers=master_key_header)
    print(f"DEBUG: Response {response.status_code}: {response.text}")
    assert response.status_code == 201
    data = response.json()
    new_api_key = data["key"]
    key_id = data["id"]

    # 2. Verify we can list it
    response = client.get("/admin/api-keys", headers=master_key_header)
    assert response.status_code == 200
    keys = response.json()
    assert any(k["id"] == key_id for k in keys)

    # 2.5 Verification: Try to create duplicate key for same team (should fail)
    response = client.post("/admin/api-keys", json=payload, headers=master_key_header)
    assert response.status_code == 409

    # 2.6 Verification: Try to create duplicate key with different case (should fail due to normalization)
    payload_upper = {"team_name": unique_team.upper(), "permissions": ["READ"]}
    response = client.post("/admin/api-keys", json=payload_upper, headers=master_key_header)
    assert response.status_code == 409

    # 2.7 Verification: Try to create key with invalid permission (should fail validation)
    payload_invalid = {"team_name": "Other Team", "permissions": ["INVALID_PERM"]}
    response = client.post("/admin/api-keys", json=payload_invalid, headers=master_key_header)
    assert response.status_code == 422

    # 3. Use new API Key on a protected route (READ permission should allow GET)
    response = client.get("/projects?limit=1", headers={"X-API-Key": new_api_key})
    assert response.status_code != 401
    assert response.status_code != 403

    # 3.5 Verification: Try to use READ key for WRITE operation (should fail)
    execution_payload = {
        "project": "Test Project",
        "environment": "Test Env",
        "total": 10,
        "passed": 10,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "time": 100,
        "tests": [],
        # Added required fields
        "pass_rate": 100.0,
        "failure_rate": 0.0,
        "skipped_rate": 0.0,
        "source": "integration-test",
        "failed_cases": [],
        "created_at": "2023-10-01T12:00:00Z"
    }
    # Note: Using READ key on POST /executions
    response = client.post("/executions?project=Test&environment=Dev", json=execution_payload, headers={"X-API-Key": new_api_key})
    assert response.status_code == 403

    # 3.6 Verification: Try to use READ key for XML upload (should fail)
    # Using /xml/process-from-path as it doesn't require multipart setup for simple unauthorized check
    # Dependency verification happens BEFORE function execution, so we expect 403, not 404/500.
    response = client.post("/xml/process-from-path?file_path=dummy.xml", headers={"X-API-Key": new_api_key})
    assert response.status_code == 403

    # 3.7 Verification: Try to use READ key for XML execution (should fail)
    # Note: Requires multipart/form-data, but the 403 check happens before body parsing
    response = client.post(
        "/xml-execution/process-and-save?project=Test&environment=Dev",
        headers={"X-API-Key": new_api_key},
        # Sending empty body/files to trigger auth check first.
    )
    assert response.status_code == 403

    # 3.8 Verification: Update permissions to include WRITE
    update_payload = {"permissions": ["READ", "WRITE"]}
    response = client.put(f"/admin/api-keys/{new_api_key}", json=update_payload, headers=master_key_header)
    assert response.status_code == 204

    # 3.9 Verification: Retry WRITE operation with updated permissions (should succeed)
    response = client.post("/executions?project=Test&environment=rc", json=execution_payload, headers={"X-API-Key": new_api_key})
    assert response.status_code == 200

    # 4. Revoke API Key
    response = client.delete(f"/admin/api-keys/{new_api_key}", headers=master_key_header)
    assert response.status_code == 204

    # 5. Verify access is denied
    response = client.get("/projects?limit=1", headers={"X-API-Key": new_api_key})
    assert response.status_code == 401

def test_admin_protection(client):
    # Try accessing admin without key
    response = client.get("/admin/api-keys")
    assert response.status_code == 401 or response.status_code == 403 or response.status_code == 500 # Depends on error handler
    # Actually VerifyMasterKey raises 500 if NO MASTER KEY set, or 403 if invalid.
    # We set MASTER_KEY in fixture. So expect 403 or 401 if missing header completely.
    # verify_master_key gets Header alias=API_KEY_NAME.

    # Check unauthorized
    response = client.get("/admin/api-keys", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 403
