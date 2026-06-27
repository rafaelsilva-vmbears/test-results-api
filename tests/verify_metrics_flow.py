import sys
import os
from datetime import datetime, timedelta
from typing import Optional

sys.path.append(os.getcwd())

from app.domain.entities.metrics_summary import MetricsSummary
from app.application.use_cases.metrics.get_run_summary_use_case import GetRunSummaryUseCase

# Mock Repository
class MockMetricsRepository:
    def get_summary(
        self,
        project: str,
        environment: str,
        start_dt: datetime,
        end_dt: datetime
    ) -> Optional[MetricsSummary]:
        if project == "empty":
            return None

        return MetricsSummary(
            project=project,
            environment=environment,
            total_runs=10,
            total_tests=100,
            total_passes=80,
            total_failures=20,
            total_skipped=0,
            avg_pass_rate=80.0,
            avg_failures=20.0,
            avg_skipped=0.0,
            last_run_number=5,
            last_execution_date=datetime.now()
        )

def test_metrics_flow():
    repo = MockMetricsRepository()
    use_case = GetRunSummaryUseCase(repo)

    start = datetime.now() - timedelta(days=7)
    end = datetime.now()

    # Test Success Case
    result = use_case.execute("test-project", "dev", start, end)

    assert result is not None
    assert result.project == "test-project"
    assert result.total_runs == 10
    # Verify rounding logic in Use Case still works (though input is integer/round already)
    assert result.avg_pass_rate == 80.0
    print("✅ Metrics Use Case flow verification passed")

    # Test Empty Case
    empty_result = use_case.execute("empty", "dev", start, end)
    assert empty_result is None
    print("✅ Empty result handled correctly")

if __name__ == "__main__":
    try:
        test_metrics_flow()
        print("\n🎉 All metrics flow tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
