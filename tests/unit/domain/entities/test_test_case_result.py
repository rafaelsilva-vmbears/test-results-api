
import pytest
from app.domain.entities.test_case_result import TestCaseResult, TestResultStatus

class TestTestCaseResult:

    def test_full_name_construction(self):
        t1 = TestCaseResult(name="test", classname="pkg.Class")
        assert t1.full_name == "pkg.Class - test"

        t2 = TestCaseResult(name="test", classname=None)
        assert t2.full_name == "test"

    def test_is_failure_property(self):
        passed = TestCaseResult(status=TestResultStatus.PASSED)
        assert not passed.is_failure

        failed = TestCaseResult(status=TestResultStatus.FAILED)
        assert failed.is_failure

        error = TestCaseResult(status=TestResultStatus.ERROR)
        assert error.is_failure

        skipped = TestCaseResult(status=TestResultStatus.SKIPPED)
        assert not skipped.is_failure

    def test_serialization(self):
        t = TestCaseResult(name="n", status=TestResultStatus.PASSED)
        d = t.to_dict()
        assert d["name"] == "n"
        assert d["status"] == "passed"

        t2 = TestCaseResult.from_dict(d)
        assert t2.status == TestResultStatus.PASSED
