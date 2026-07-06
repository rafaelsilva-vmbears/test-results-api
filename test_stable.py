from unittest.mock import MagicMock
from app.application.use_cases.metrics.get_stable_tests_use_case import GetStableTestsUseCase

def test_get_stable_tests():
    mock_repo = MagicMock()
    mock_repo.get_stable_tests.return_value = []
    
    use_case = GetStableTestsUseCase(mock_repo)
    result = use_case.execute("proj", "env")
    assert result == []
    print("Test passed!")

if __name__ == "__main__":
    test_get_stable_tests()
