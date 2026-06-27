
import pytest
import mongomock
from datetime import datetime, timezone
from unittest.mock import Mock
from app.infrastructure.repositories.execution_repository import ExecutionRepository
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface
from app.domain.entities.execution_entity import ExecutionEntity

class TestExecutionRepositoryIntegration:

    @pytest.fixture
    def mock_adapter(self):
        adapter = Mock(spec=DatabaseAdapterInterface)
        client = mongomock.MongoClient()
        db = client.test_db

        # Helper to mimic Adapter method signatures connecting to Mongomock
        def get_collection(name):
            return db[name]

        def insert_one(col_name, data):
            # mongomock insert_one returns InsertOneResult, adapter needs str or ObjectId
            res = db[col_name].insert_one(data)
            return str(res.inserted_id)

        def find(collection, query, sort=None, limit=0):
             cursor = db[collection].find(query)
             if sort:
                 cursor.sort(sort)
             if limit:
                 cursor.limit(limit)
             return list(cursor)

        def find_one_and_update(collection, query, update, upsert=False, return_after=False):
            return db[collection].find_one_and_update(
                query, update, upsert=upsert, return_document=return_after
            )

        def find_one(collection, query):
            return db[collection].find_one(query)

        def update_one(collection, query, update, upsert=False):
            return db[collection].update_one(query, update, upsert=upsert)

        adapter.get_collection.side_effect = get_collection
        adapter.insert_one.side_effect = insert_one
        adapter.find.side_effect = find
        adapter.find_one_and_update.side_effect = find_one_and_update
        adapter.find_one.side_effect = find_one
        pass # update_one is called on collection object returned by get_collection in repo code
             # Wait, repo calls adapter.get_collection().update_one() DIRECTLY in insert_execution line 82
             # But it calls adapter.insert_one() wrapper in line 58.
             # Mixed usage. I need to handle both patterns.

        return adapter

    @pytest.fixture
    def sut(self, mock_adapter):
        return ExecutionRepository(adapter=mock_adapter)

    def test_get_next_run_number_atomic_increment(self, sut, mock_adapter):
        """
        Integration test verifying atomic increment on 'counters' collection.
        """
        project = "MyProject"
        env = "rc"

        # 1st Call - Should start at 2 (since $inc triggers on upsert likely, logic says return .seq.env)
        # Logic: update $inc: {seq.env: 1}. If new, starts at 1. return_after=True.

        val1 = sut.get_next_run_number(project, env)
        assert val1 == 1

        # 2nd Call - Should increment
        val2 = sut.get_next_run_number(project, env)
        assert val2 == 2

        # Verify persistence in mongomock
        doc = mock_adapter.get_collection("counters").find_one({"_id": "myproject"})
        assert doc["seq"]["rc"] == 2

    def test_insert_execution_updates_projects_collection(self, sut, mock_adapter):
        """
        Verifies that inserting an execution ALSO updates the 'projects' metadata collection.
        """
        execution = ExecutionEntity(
            id=None,
            project="NewProj",
            environment="UAT",
            run_number=10,
            source="Test",
            created_at=datetime.now(),
            total=5, passed=5, failures=0, skipped=0,
            pass_rate=100.0, failure_rate=0.0, skipped_rate=0.0,
            tests=[], failed_cases=[]
        )

        # Act
        sut.insert_execution(execution)

        # Assert 1: Run inserted
        runs = list(mock_adapter.get_collection("runs").find())
        assert len(runs) == 1
        assert runs[0]["project"] == "newproj"

        # Assert 2: Project Metadata Updated
        proj = mock_adapter.get_collection("projects").find_one({"_id": "newproj"})
        assert proj is not None
        assert proj["name"] == "newproj" # Name is derived from ID, so it is lowercased
        assert "uat" in proj["environments"]
        assert proj["total_runs"] == 1

    def test_find_executions_filtering(self, sut, mock_adapter):
        """
        Verify filters work against mongomock.
        """
        # Arrange
        valid_date = datetime(2023, 1, 15)
        # Bypassing repository insert to just mock data state quicker
        mock_adapter.get_collection("runs").insert_many([
            {"project": "p1", "environment": "dev", "created_at": valid_date, "total": 1},
            {"project": "p1", "environment": "prod", "created_at": valid_date, "total": 1}, # wrong env
            {"project": "p2", "environment": "dev", "created_at": valid_date, "total": 1},  # wrong proj
        ])

        # Act
        results = sut.find_executions(
            project="P1", # Upper/Mixed case input
            environment="DEV",
            start_dt=datetime(2023, 1, 1),
            end_dt=datetime(2023, 1, 31)
        )

        # Assert
        assert len(results) == 1
        assert results[0].project == "p1"
        assert results[0].environment == "dev"
