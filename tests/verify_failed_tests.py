import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add project root to path
sys.path.append(os.getcwd())

from app.domain.entities.failed_test_summary import FailedTestSummary
from app.application.use_cases.metrics.get_failed_tests_use_case import GetFailedTestsUseCase
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface

# Mock Repository
class MockMetricsRepository:
    def get_summary(self, project, environment, start_dt, end_dt):
        return None

    def get_failed_tests(
        self,
        project: str,
        environment: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> List[FailedTestSummary]:
        if project == "empty":
            return []

        return [
            FailedTestSummary(
                name="test_login_page_failure",
                run_numbers=[101, 102, 105],
                last_message="TimeoutException: Element not found"
            ),
            FailedTestSummary(
                name="test_cart_update_error",
                run_numbers=[103],
                last_message="API Error 500"
            )
        ]

def test_failed_tests_flow():
    repo = MockMetricsRepository()
    use_case = GetFailedTestsUseCase(repo)

    start = datetime.now() - timedelta(days=7)
    end = datetime.now()

    # Test Success Case
    results = use_case.execute("test-project", "dev", start, end)

    assert len(results) == 2
    assert results[0].name == "test_login_page_failure"
    assert results[0].run_numbers == [101, 102, 105]
    assert results[0].last_message == "TimeoutException: Element not found"

    print("✅ Failed Tests Use Case flow verification passed")

    # Test Empty Case
    empty_results = use_case.execute("empty", "dev", start, end)
    assert len(empty_results) == 0
    print("✅ Empty result handled correctly")

if __name__ == "__main__":
    try:
        test_failed_tests_flow()
        print("\n🎉 All failed tests flow tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
