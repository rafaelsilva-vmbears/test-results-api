import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, Request

from app.infrastructure.security.security import (
    verify_master_key,
    verify_api_key,
    _verify_permission
)
from app.domain.entities.permission_enum import Permission

class TestSecurityCoverage:

    def test_verify_master_key_not_configured(self):
        # Mock os.getenv to return None for MASTER_KEY
        with patch("app.infrastructure.security.security.MASTER_KEY", None):
            with pytest.raises(HTTPException) as exc:
                verify_master_key("some-key")
            assert exc.value.status_code == 500
            assert "Master Key not configured" in exc.value.detail

    def test_verify_permission_db_exception(self):
        # Mock request with a DB adapter that raises an Exception
        mock_request = Mock(spec=Request)
        mock_db_adapter = Mock()
        # The repo uses find_one, so we mock that to raise
        mock_db_adapter.find_one.side_effect = Exception("DB Connection Fail")
        mock_request.app.state.db_adapter = mock_db_adapter

        # Should catch exception and raise 401 (as per logic flow falling through)
        # Wait, the code catches Exception and passes, then raises 401 at the end.
        with patch("app.infrastructure.security.security.MASTER_KEY", None):
            with patch("app.infrastructure.security.security.LEGACY_API_KEY", None):
                with pytest.raises(HTTPException) as exc:
                    _verify_permission(mock_request, "some-key", Permission.READ)
                assert exc.value.status_code == 401
                assert "Invalid or revoked API Key" in exc.value.detail

    def test_verify_api_key_exception_handling(self):
        # Test the deprecated verify_api_key exception swallowing
        mock_request = Mock(spec=Request)
        mock_request.app.state.db_adapter.find_one.side_effect = Exception("Boom")

        with patch("app.infrastructure.security.security.MASTER_KEY", None):
            with patch("app.infrastructure.security.security.LEGACY_API_KEY", None):
                with pytest.raises(HTTPException) as exc:
                    verify_api_key(mock_request, "some-key")
                assert exc.value.status_code == 401
