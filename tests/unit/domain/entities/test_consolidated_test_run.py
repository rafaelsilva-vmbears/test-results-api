
import pytest
from app.domain.entities.test_case_result import ConsolidatedTestRun, TestCaseResult, TestResultStatus, TestStatus

class TestConsolidatedTestRun:

    def test_should_calculate_statistics_automatically(self):
        """
        GIVEN a run with mixed result tests
        WHEN statistics are calculated
        THEN counts and rates should be accurate
        """
        tests = [
            TestCaseResult(name="t1", status=TestResultStatus.PASSED),
            TestCaseResult(name="t2", status=TestResultStatus.PASSED),
            TestCaseResult(name="t3", status=TestResultStatus.FAILED),
            TestCaseResult(name="t4", status=TestResultStatus.SKIPPED),
        ]

        run = ConsolidatedTestRun(test_results=tests)

        # It calculates in __post_init__
        assert run.total == 4
        assert run.passed == 2
        assert run.failures == 1
        assert run.skipped == 1
        assert run.status == TestStatus.FAILURE

        # Check rates
        assert run.success_rate == 50.0
        assert run.failure_rate == 25.0
        assert run.skipped_rate == 25.0

    def test_should_detect_overall_success(self):
        """
        GIVEN all tests passed
        WHEN calculated
        THEN status should be SUCCESS
        """
        run = ConsolidatedTestRun(test_results=[
            TestCaseResult(name="t1", status=TestResultStatus.PASSED)
        ])
        assert run.status == TestStatus.SUCCESS

    def test_should_detect_skipped_run(self):
        """
        GIVEN all tests skipped
        WHEN calculated
        THEN status should be SKIPPED
        """
        run = ConsolidatedTestRun(test_results=[
            TestCaseResult(name="t1", status=TestResultStatus.SKIPPED)
        ])
        assert run.status == TestStatus.SKIPPED

    def test_should_aggregate_errors_into_failures_count(self):
        """
        GIVEN mixed failures and errors
        WHEN calculated
        THEN 'failures' property should include both, but 'error' detail is separate
        """
        tests = [
            TestCaseResult(name="t1", status=TestResultStatus.FAILED),
            TestCaseResult(name="t2", status=TestResultStatus.ERROR),
        ]
        run = ConsolidatedTestRun(test_results=tests)

        assert run.failures == 2  # Aggregated
        assert run.error == 1     # Detail
        assert run.status == TestStatus.FAILURE

    def test_add_test_result_should_recalculate_stats(self):
        """
        GIVEN an existing run
        WHEN add_test_result is called
        THEN statistics should update dynamically
        """
        run = ConsolidatedTestRun(test_results=[])
        assert run.total == 0

        run.add_test_result(TestCaseResult(name="new", status=TestResultStatus.PASSED))

        assert run.total == 1
        assert run.passed == 1
        assert run.success_rate == 100.0

    def test_get_slowest_tests(self):
        """
        GIVEN tests with different execution times
        WHEN get_slowest_tests is called
        THEN successful return ordered by time desc
        """
        t1 = TestCaseResult(name="fast", time=0.1)
        t2 = TestCaseResult(name="slow", time=5.0)
        t3 = TestCaseResult(name="medium", time=1.0)

        run = ConsolidatedTestRun(test_results=[t1, t2, t3])

        slowest = run.get_slowest_tests(limit=2)
        assert len(slowest) == 2
        assert slowest[0].name == "slow"
        assert slowest[1].name == "medium"

    def test_summary_serialization(self):
        """
        GIVEN a completed run
        WHEN summary is called
        THEN it should return a dictionary with correct calculated fields
        """
        # failures=1 (FAILED) and error=1 (ERROR) -> total failures count = 2 in Entity logic
        # But summary() splits them.
        tests = [
            TestCaseResult(name="p", status=TestResultStatus.PASSED),
            TestCaseResult(name="f", status=TestResultStatus.FAILED),
            TestCaseResult(name="e", status=TestResultStatus.ERROR),
        ]
        run = ConsolidatedTestRun(test_results=tests)

        summ = run.summary()

        assert summ["total"] == 3
        # In summary(), "failures" is failures_only (FAILED status only)
        # Entity.failures aggregates FAILED + ERROR.
        # Check source: failures_only = self.failures - self.error
        # self.failures = 1+1=2. self.error=1. result=1. Correct.
        assert summ["failures"] == 1
        assert summ["errors"] == 1
        assert summ["passed"] == 1
        assert summ["status"] == "failure"
        assert len(summ["failed_cases"]) == 2  # Includes both failed and error
