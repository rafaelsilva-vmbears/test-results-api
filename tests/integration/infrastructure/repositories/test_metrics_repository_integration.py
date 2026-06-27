
import pytest
import mongomock
from datetime import datetime
from unittest.mock import Mock

from app.infrastructure.repositories.metrics_repository import MetricsRepository
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

class TestMetricsRepositoryIntegration:

    @pytest.fixture
    def mock_adapter(self):
        """
        Creates a mock adapter that mimics the behavior of the real adapter
        but returns mongomock primitives.
        """
        adapter = Mock(spec=DatabaseAdapterInterface)
        # Create an in-memory client
        client = mongomock.MongoClient()
        db = client.test_db

        # When get_collection is called, return the mongomock collection
        def get_collection_side_effect(name):
            return db[name]

        adapter.get_collection.side_effect = get_collection_side_effect
        return adapter

    @pytest.fixture
    def sut(self, mock_adapter):
        return MetricsRepository(adapter=mock_adapter)

    def test_get_summary_integration(self, sut, mock_adapter):
        """
        Integration test verifying the aggregation pipeline against mongomock.
        """
        # Arrange: Insert data into the in-memory db
        collection = mock_adapter.get_collection("runs")

        # Data setup
        base_date = datetime(2023, 1, 15)
        docs = [
            {
                "project": "ProjA",
                "environment": "Prod",
                "run_number": 1,
                "created_at": base_date,
                "total": 10, "passed": 8, "failures": 2, "skipped": 0, "error": 0
            },
            {
                "project": "ProjA",
                "environment": "Prod",
                "run_number": 2,
                "created_at": base_date,
                "total": 10, "passed": 10, "failures": 0, "skipped": 0, "error": 0
            },
            # Different project (should be excluded)
            {
                "project": "ProjB",
                "environment": "Prod",
                "run_number": 1,
                "created_at": base_date,
                "total": 5, "passed": 5, "failures": 0, "skipped": 0, "error": 0
            }
        ]
        collection.insert_many(docs)

        # Act
        summary = sut.get_summary(
            project="ProjA",
            environment="Prod",
            start_dt=datetime(2023, 1, 1),
            end_dt=datetime(2023, 1, 31)
        )

        # Assert
        assert summary is not None
        assert summary.project == "ProjA"
        assert summary.total_runs == 2
        assert summary.total_tests == 20
        assert summary.total_passes == 18 # 8 + 10
        assert summary.total_failures == 2 # 2 + 0

        # Check calculated averages
        # Pass rate: (18 / 20) * 100 = 90.0
        assert summary.avg_pass_rate == 90.0
        assert summary.avg_failures == 10.0

    def test_get_mttr_ignores_same_run_flaky_test(self, sut, mock_adapter):
        """
        Integration test verifying that get_mttr correctly ignores 
        a test that fails and passes within the same execution run.
        """
        collection = mock_adapter.get_collection("runs")
        
        base_date = datetime(2023, 1, 15, 10, 0, 0)
        docs = [
            {
                "_id": "run_1",
                "project": "ProjA",
                "environment": "Prod",
                "run_number": 1,
                "execution_date": base_date,
                "created_at": base_date,
                "test_results": [
                    {"name": "test_flaky", "status": "failed"},
                    {"name": "test_flaky", "status": "passed"}
                ]
            },
            {
                "_id": "run_2",
                "project": "ProjA",
                "environment": "Prod",
                "run_number": 2,
                "execution_date": datetime(2023, 1, 15, 12, 0, 0),
                "created_at": datetime(2023, 1, 15, 12, 0, 0),
                "test_results": [
                    {"name": "test_genuine_recovery", "status": "failed"}
                ]
            },
            {
                "_id": "run_3",
                "project": "ProjA",
                "environment": "Prod",
                "run_number": 3,
                "execution_date": datetime(2023, 1, 15, 15, 0, 0),
                "created_at": datetime(2023, 1, 15, 15, 0, 0),
                "test_results": [
                    {"name": "test_genuine_recovery", "status": "passed"}
                ]
            }
        ]
        collection.insert_many(docs)

        mttr_summary = sut.get_mttr(
            project="ProjA",
            environment="Prod",
            start_dt=datetime(2023, 1, 1),
            end_dt=datetime(2023, 1, 31)
        )

        assert mttr_summary is not None
        # It should ignore the 0.0 hour recovery from run_1, 
        # and only count the 3.0 hour recovery (15:00 - 12:00) from run_2 to run_3.
        assert mttr_summary.total_recoveries == 1
        assert mttr_summary.mttr_hours == 3.0
