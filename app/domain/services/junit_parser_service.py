
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from app.domain.entities.test_case_result import ConsolidatedTestRun, TestCaseResult, TestResultStatus

logger = logging.getLogger(__name__)

BR_ZONE_INFO = ZoneInfo("America/Sao_Paulo")


try:
    from defusedxml.ElementTree import fromstring as safe_fromstring, ParseError as DefusedParseError
    _USE_DEFUSED = True
except Exception:
    safe_fromstring = ET.fromstring
    DefusedParseError = ET.ParseError
    _USE_DEFUSED = False
    logger.debug(
        "defusedxml not available — ensure XML inputs are trusted or install defusedxml to mitigate XXE.")


class JUnitParserService:
    """
    Serviço de domínio para parse de XML JUnit/xUnit.
    Mantém-se síncrono: execute-o em um threadpool a partir de rotas async quando necessário.
    """

    def import_from_junit_xml(self, xml_content: str, source: str) -> ConsolidatedTestRun:
        return self.parse_xunit_xml(xml_content, source)

    @staticmethod
    def _extract_testcases(testsuite: ET.Element) -> List[TestCaseResult]:
        cases: List[TestCaseResult] = []

        for testcase in testsuite.findall("testcase"):
            classname = testcase.attrib.get("classname")
            name = testcase.attrib.get("name")

            # Helper for time parsing
            time_attr = testcase.attrib.get("time")
            try:
                time_val = float(time_attr) if time_attr not in (None, "") else 0.0
            except (TypeError, ValueError):
                logger.debug("Invalid time on testcase %s.%s: %s", classname, name, time_attr)
                time_val = 0.0

            # Status determination
            status = TestResultStatus.PASSED
            message = None

            failure = testcase.find("failure")
            error = testcase.find("error")
            skipped = testcase.find("skipped")

            if failure is not None:
                status = TestResultStatus.FAILED
                message = (failure.attrib.get("message") or (failure.text or "").strip() or "No message")
            elif error is not None:
                status = TestResultStatus.ERROR
                message = (error.attrib.get("message") or (error.text or "").strip() or "No message")
            elif skipped is not None:
                status = TestResultStatus.SKIPPED
                message = (skipped.attrib.get("message") or (skipped.text or "").strip() or None)

            cases.append(TestCaseResult(
                name=name or "unknown",
                classname=classname,
                status=status,
                time=time_val,
                message=message
            ))

        for child_suite in testsuite.findall("testsuite"):
            cases.extend(JUnitParserService._extract_testcases(child_suite))

        return cases

    @staticmethod
    def parse_xunit_xml(xml_content: str, source: str, use_iterparse: bool = False) -> ConsolidatedTestRun:
        """
        Parse xUnit/JUnit XML content and return a ConsolidatedTestRun entity.

        Args:
            xml_content: XML content as string
            source: source identifier
            use_iterparse: If True, parse with iterparse (streaming). Useful for very large XMLs.
        """
        if not xml_content or not xml_content.strip():
            raise ValueError("XML content cannot be empty or whitespace.")

        try:
            if use_iterparse:
                with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False) as tmp:
                    tmp.write(xml_content)
                    tmp.flush()
                    tmp_path = tmp.name
                try:
                    it = ET.iterparse(tmp_path, events=("end",))
                    root = None
                    for event, elem in it:
                        if root is None:
                            root = elem.getroottree() if hasattr(elem, "getroottree") else elem
                    root = ET.parse(tmp_path).getroot()
                finally:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
            else:
                root = safe_fromstring(xml_content)
        except (DefusedParseError, ET.ParseError) as exc:
            logger.debug("XML parsing error: %s", exc)
            raise ValueError(f"Failed to parse XML: {exc}") from exc
        except Exception as exc:
            logger.exception("Unexpected error while parsing XML")
            raise ValueError(f"Unexpected error parsing XML: {exc}") from exc

        testsuite_elements: List[ET.Element] = []
        tag = getattr(root, "tag", None)
        if tag == "testsuite":
            testsuite_elements = [root]
        elif tag == "testsuites":
            testsuite_elements = list(root.findall("testsuite"))
        else:
            testsuite_elements = list(root.findall(".//testsuite"))

        if not testsuite_elements:
            raise ValueError("No <testsuite> elements found in XML")

        test_results: List[TestCaseResult] = []
        for ts in testsuite_elements:
            test_results.extend(JUnitParserService._extract_testcases(ts))

        root_time = root.attrib.get("time") if hasattr(
            root, "attrib") else None
        try:
            total_time = float(root_time) if root_time not in (
                None, "") else sum(t.time for t in test_results)
        except Exception:
            total_time = sum(t.time for t in test_results)

        execution_date = None
        root_timestamp_str = root.attrib.get("timestamp") if hasattr(root, "attrib") else None
        if root_timestamp_str:
            try:
                from datetime import datetime
                execution_date = datetime.fromisoformat(root_timestamp_str)
            except ValueError:
                pass

        consolidated_run = ConsolidatedTestRun(
            test_results=test_results,
            time=total_time,
            source=source,
            execution_date=execution_date
        )

        return consolidated_run
