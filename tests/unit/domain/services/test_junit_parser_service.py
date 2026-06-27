
import pytest
from app.domain.services.junit_parser_service import JUnitParserService
from app.domain.entities.test_case_result import ConsolidatedTestRun, TestResultStatus

class TestJUnitParserService:

    @pytest.fixture
    def sut(self):
        """Subject Under Test"""
        return JUnitParserService()

    def test_should_parse_valid_xml_correctly(self, sut):
        """
        GIVEN a valid JUnit XML with various statuses
        WHEN import_from_junit_xml is called
        THEN it should return a ConsolidatedTestRun with correct statistics and details
        """
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <testsuite name="com.example.Test" time="1.234">
            <testcase name="testPass" classname="com.example.Test" time="0.100"/>
            <testcase name="testFail" classname="com.example.Test" time="0.200">
                <failure message="Assertion failed">Expected 1 but got 2</failure>
            </testcase>
            <testcase name="testError" classname="com.example.Test" time="0.300">
                <error message="NullPointerException"/>
            </testcase>
            <testcase name="testSkip" classname="com.example.Test" time="0.000">
                <skipped/>
            </testcase>
        </testsuite>
        """

        result = sut.import_from_junit_xml(xml_content, source="jenkins")

        assert isinstance(result, ConsolidatedTestRun)
        assert result.total == 4
        assert result.passed == 1
        assert result.failures == 2  # Failures + Errors
        assert result.error == 1     # Detail count
        assert result.skipped == 1
        assert result.source == "jenkins"

        # Check details
        assert len(result.test_results) == 4

        # Verify passed
        passed = result.get_tests_by_status(TestResultStatus.PASSED)[0]
        assert passed.full_name == "com.example.Test - testPass"
        assert passed.time == 0.100

        # Verify failure message
        failed = result.get_tests_by_status(TestResultStatus.FAILED)[0]
        assert failed.full_name == "com.example.Test - testFail"
        assert "Assertion failed" in failed.message

    def test_should_handle_nested_testsuites_recursively(self, sut):
        """
        GIVEN an XML with nested testsuites
        WHEN parsed
        THEN it should flatten all testcases into the consolidated run
        """
        xml_content = """
        <testsuites>
            <testsuite name="Suite1">
                <testcase name="Case1" classname="Class1"/>
            </testsuite>
            <testsuite name="Suite2">
                 <testsuite name="Suite2.1">
                    <testcase name="Case2" classname="Class2"/>
                 </testsuite>
            </testsuite>
        </testsuites>
        """

        result = sut.import_from_junit_xml(xml_content, source="s3")

        assert result.total == 2
        names = [t.full_name for t in result.test_results]
        assert "Class1 - Case1" in names
        assert "Class2 - Case2" in names

    def test_should_accept_empty_classname(self, sut):
        """
        GIVEN a testcase without a classname attribute
        WHEN parsed
        THEN it should default name handling gracefully
        """
        xml_content = """<testsuite><testcase name="StandaloneTest"/></testsuite>"""
        result = sut.import_from_junit_xml(xml_content, source="local")

        test = result.test_results[0]
        assert test.name == "StandaloneTest"
        assert test.classname is None

    def test_should_raise_error_for_malformed_xml(self, sut):
        """
        GIVEN invalid XML content
        WHEN parsed
        THEN it should raise a ValueError
        """
        with pytest.raises(ValueError, match="Failed to parse XML"):
            sut.import_from_junit_xml("<invalid>unclosed tag", source="test")

    def test_should_raise_error_for_empty_content(self, sut):
        """
        GIVEN empty string
        WHEN parsed
        THEN it should raise ValueError
        """
        with pytest.raises(ValueError, match="XML content cannot be empty"):
            sut.import_from_junit_xml("   ", source="test")
