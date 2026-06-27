
import pytest
from unittest.mock import Mock, create_autospec

from app.application.use_cases.parser_xml.junit_xml_parsing_use_case import JUnitXMLParsingUseCase
from app.domain.services.junit_parser_service import JUnitParserService
from app.domain.entities.test_case_result import ConsolidatedTestRun

@pytest.fixture
def mock_service():
    return create_autospec(JUnitParserService, instance=True)

@pytest.fixture
def sut(mock_service):
    """Subject Under Test"""
    return JUnitXMLParsingUseCase(parser_service=mock_service)

class TestJUnitXMLParsingUseCase:

    def test_should_orchestrate_parsing_and_return_summary(self, sut, mock_service):
        """
        GIVEN xml content
        WHEN execute is called
        THEN it should call service to import and then return summary
        """
        # Arrange
        xml_content = "<root></root>"
        source = "jenkins"

        # Mock the consolidated run returned by service
        mock_consolidated = Mock(spec=ConsolidatedTestRun)
        mock_consolidated.summary.return_value = {"status": "success"}

        mock_service.import_from_junit_xml.return_value = mock_consolidated

        # Act
        result = sut.execute(xml_content, source)

        # Assert
        mock_service.import_from_junit_xml.assert_called_once_with(xml_content, source)
        mock_consolidated.summary.assert_called_once()
        assert result == {"status": "success"}
