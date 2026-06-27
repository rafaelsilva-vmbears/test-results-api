"""
Use cases for parsing JUnit XML files.
"""
from typing import Dict, Any
from app.domain.services.junit_parser_service import JUnitParserService


class JUnitXMLParsingUseCase():
    """Service that implements both parsing use cases."""

    def __init__(self, parser_service: JUnitParserService):
        self.parser_service = parser_service

    def execute(self, xml_content: str, source: str) -> Dict[str, Any]:
        """Parse JUnit XML and return summary data"""
        consolidated_run = self.parser_service.import_from_junit_xml(
            xml_content, source
        )
        return consolidated_run.summary()
