
from app.application.dtos.execution_dto import TestDTO

def test_test_dto_accepts_short_name():
    """
    GIVEN a dictionary with 'short_name'
    WHEN instantiating TestDTO
    THEN it should accept the field and store it
    """
    data = {
        "name": "full name",
        "status": "passed",
        "short_name": "short name"
    }

    dto = TestDTO(**data)

    assert dto.name == "full name"
    assert dto.short_name == "short name"
    assert dto.status == "passed"
