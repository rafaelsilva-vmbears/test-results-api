"""This FastAPI router (`/xml-execution`) defines an endpoint for processing JUnit/XML test results and creating execution records.

**Key Components:**

*   **Dependencies:** `verify_api_key` for authentication.
*   **`JUnitParserService`:** Parses XML content.
*   **`JUnitXMLParsingUseCase`:** Orchestrates XML parsing using `JUnitParserService`.
*   **`CreateExecutionUseCase`:** Creates execution records in the database
"""


from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from starlette.concurrency import run_in_threadpool
from zoneinfo import ZoneInfo
from datetime import datetime

from app.domain.services.junit_parser_service import JUnitParserService
from app.application.use_cases.parser_xml.junit_xml_parsing_use_case import JUnitXMLParsingUseCase
from app.api.schemas.execution import CreateExecutionResponseSchema
from app.application.dtos.execution_dto import CreateExecutionDTO, TestDTO
from app.infrastructure.security.security import verify_write_permission
from app.application.use_cases.execution.create_exections_use_case import CreateExecutionUseCase

BR_ZONE_INFO = ZoneInfo("America/Sao_Paulo")
from app.api.dependencies import get_create_execution_use_case

router = APIRouter(
    prefix="/xml-execution",
    tags=["XML Processing and Execution Creation"],
    dependencies=[Depends(verify_write_permission)]
)

junit_parse = JUnitParserService()
parser = JUnitXMLParsingUseCase(junit_parse)


@router.post(
    "/process-and-save",
    summary="Process XML test results and create execution",
    description="Process JUnit/XML test results, and if successful, create a new execution record",
    response_model=CreateExecutionResponseSchema,
    responses={
        201: {
            "description": "Execution created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "execution-id-string"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data or processing error",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "type": "ProcessingError",
                            "message": "Error processing XML file: ...",
                            "status_code": 400,
                            "timestamp": "2023-10-01T12:00:00Z",
                            "path": "/xml-execution/process-and-save"
                        }
                    }
                }
            }
        }
    }
)
async def process_xml_and_create_execution(
    file: UploadFile = File(...),
    project: str = Query(..., description="Nome do projeto (obrigatório)"),
    environment: str = Query(...,
                             description="Ambiente da execução (obrigatório)"),
    source: str = Query(description="Fonte dos testes", default="xml"),
    use_case: CreateExecutionUseCase = Depends(get_create_execution_use_case)
):
    """
    Process an uploaded XML file containing test results and create an execution record.

    - **file**: The XML file to process
    - **project**: Project name (required)
    - **environment**: Execution environment (required)
    - **source**: Test source (optional)
    - Returns: Execution ID if successful
    """
    try:

        xml_content = (await file.read()).decode('utf-8')
        parsed_data = parser.execute(xml_content, source)



        # Convert parsed data dict to Application DTO
        execution_payload = CreateExecutionDTO(
            total=parsed_data.get('total', 0),
            passed=parsed_data.get('passed'),
            failures=parsed_data.get('failures', 0),
            errors=parsed_data.get('errors'),
            skipped=parsed_data.get('skipped', 0),
            pass_rate=parsed_data.get('pass_rate', 0.0),
            failure_rate=parsed_data.get('failure_rate', 0.0),
            skipped_rate=parsed_data.get('skipped_rate', 0.0),
            time=parsed_data.get('time'),
            source=source.lower(),
            tests=[TestDTO(**t) if isinstance(t, dict) else TestDTO(**t.model_dump()) for t in parsed_data.get('tests', [])],
            failed_cases=[TestDTO(**t) if isinstance(t, dict) else TestDTO(**t.model_dump()) for t in parsed_data.get('failed_cases', [])],
            created_at=datetime.fromisoformat(parsed_data.get('created_at')) if isinstance(parsed_data.get('created_at'), str) else parsed_data.get('created_at', datetime.now(BR_ZONE_INFO)),
            execution_date=datetime.fromisoformat(parsed_data.get('execution_date')) if isinstance(parsed_data.get('execution_date'), str) else parsed_data.get('execution_date')
        )

        # Executar use case síncrono em thread pool
        entity = await run_in_threadpool(
            use_case.execute,
            execution_payload,
            project,
            environment
        )

        return CreateExecutionResponseSchema(id=str(entity.id))

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing XML file and creating execution: {str(e)}"
        ) from e
