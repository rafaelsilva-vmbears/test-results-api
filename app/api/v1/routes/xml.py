"""This module defines FastAPI routes for processing JUnit/XML test result files."""
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from app.domain.services.junit_parser_service import JUnitParserService
from app.application.use_cases.parser_xml.junit_xml_parsing_use_case import JUnitXMLParsingUseCase
from app.utils.file import read_file_content
from app.infrastructure.security.security import verify_write_permission

router = APIRouter(
    prefix="/xml", tags=["XML Processing"], dependencies=[Depends(verify_write_permission)])

junit_parse = JUnitParserService()
parser = JUnitXMLParsingUseCase(junit_parse)


@router.post(
    "/process",
    summary="Process XML test results",
    description="Process JUnit/XML test results and return structured data",
    response_model=Dict[str, Any]
)
async def process_xml_file(
    file: UploadFile = File(...),
    source: str = Query(description="Fonte dos testes", default="xml")
):
    """
    Process an uploaded XML file containing test results.

    - **file**: The XML file to process
    - Returns: Structured test results data
    """
    try:
        # Read the uploaded file content
        xml_content = (await file.read()).decode('utf-8')
        data = parser.execute(xml_content, source)

        return data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing XML file: {str(e)}") from e


@router.post(
    "/process-from-path",
    summary="Process XML test results from file path",
    description="Process JUnit/XML test results from a file path and return structured data",
    response_model=Dict[str, Any]
)
def process_xml_from_path(
    file_path: str = Query(..., description="Path to the XML file to process"),
    source: str = Query(description="Fonte dos testes", default="xml")
):
    """
    Process an XML file from a specified path containing test results.

    - **file_path**: The path to the XML file to process
    - Returns: Structured test results data
    """
    try:
        xml_content = read_file_content(file_path)
        data = parser.execute(xml_content, source)

        return data
    except FileNotFoundError as exc:
        raise exc
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing XML file: {str(e)}") from e
