import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from app.infrastructure.db.mappers.mappers import doc_to_entity, entity_to_doc
from app.domain.entities.execution_entity import ExecutionEntity

def test_mapper_complete_doc():
    """Test mapping a complete document with all fields."""
    doc = {
        "id": "123",
        "project": "test-project",
        "source": "jenkins",
        "environment": "dev",
        "run_number": 1,
        "created_at": "2023-01-01T12:00:00",
        "total": 10,
        "failures": 2,
        "skipped": 1,
        "passed": 7,
        "pass_rate": 70.0,
        "failure_rate": 20.0,
        "skipped_rate": 10.0,
        "test_results": [],
        "failed_cases": []
    }

    entity = doc_to_entity(doc)

    assert entity.id == "123"
    assert entity.project == "test-project"
    assert entity.source == "jenkins"
    assert entity.total == 10
    print("✅ Complete document mapped successfully")

def test_mapper_missing_optional_fields():
    """Test mapping a document missing optional fields (like source)."""
    doc = {
        "id": "456",
        "project": "test-project-2",
        # "source" missing
        "environment": "prod",
        "run_number": 2,
        "created_at": "2023-01-02T12:00:00",
        "total": 5
    }

    entity = doc_to_entity(doc)

    assert entity.id == "456"
    assert entity.project == "test-project-2"
    assert entity.source is None  # Should be None, not raise KeyError
    assert entity.total == 5
    # Defaults
    assert entity.failures == 0
    print("✅ Document with missing optional fields mapped successfully")

if __name__ == "__main__":
    try:
        test_mapper_complete_doc()
        test_mapper_missing_optional_fields()
        print("\n🎉 All mapper tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
