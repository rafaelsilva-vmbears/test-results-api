"""Implements methods to retrieve project metrics from the database."""
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.infrastructure.logging.logging_config import get_logger
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface
from app.domain.interfaces.metrics_repository_interface import MetricsRepositoryInterface
from app.domain.entities.metrics_summary import MetricsSummary
from app.domain.entities.failed_test_summary import FailedTestSummary
from app.domain.entities.module_health_summary import ModuleHealthSummary
from app.domain.entities.flaky_test_summary import FlakyTestSummary
from app.domain.entities.trend_summary import TrendSummary
from app.domain.entities.mttr_summary import MTTRSummary

logger = get_logger(__name__)


class MetricsRepository(MetricsRepositoryInterface):
    """Implements methods to retrieve project metrics from the database."""

    def __init__(self, adapter: DatabaseAdapterInterface):
        self.adapter = adapter
        self.collection = "runs"

    # Retorna métricas de um projeto por período
    def get_summary(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> Optional[MetricsSummary]:
        """Retrieves summary metrics for a given project within a specified date range."""

        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }

        col = self.adapter.get_collection(self.collection)
        matched_count = col.count_documents(query)
        logger.info("Documents matching date range: %d", matched_count)

        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$project",
                "environment": {"$first": "$environment"},
                "total_runs": {"$sum": 1},
                "total_tests": {"$sum": "$total"},
                "total_passes": {"$sum": "$passed"},
                "total_failures": {"$sum": "$failures"},
                "total_skipped": {"$sum": "$skipped"},
                "last_run_number": {"$max": "$run_number"},
                "last_execution_date": {"$max": {"$ifNull": ["$execution_date", "$created_at"]}}
            }},
            # NOVO STAGE: Calcular as médias globais a partir dos totais
            {"$addFields": {
                "avg_pass_rate": {
                    "$cond": {
                        "if": {"$gt": ["$total_tests", 0]},
                        "then": {"$multiply": [
                            {"$divide": ["$total_passes", "$total_tests"]}, 100]},
                        "else": 0
                    }
                },
                "avg_failures": {
                    "$cond": {
                        "if": {"$gt": ["$total_tests", 0]},
                        "then": {"$multiply": [{
                            "$divide": ["$total_failures", "$total_tests"]}, 100]},
                        "else": 0
                    }
                },
                "avg_skipped": {
                    "$cond": {
                        "if": {"$gt": ["$total_tests", 0]},
                        "then": {"$multiply": [
                            {"$divide": ["$total_skipped", "$total_tests"]}, 100]},
                        "else": 0
                    }
                }
            }}
        ]

        result = list(self.adapter.get_collection(
            self.collection).aggregate(pipeline))

        if not result:
            return None

        data = result[0]

        return MetricsSummary(
            project=data["_id"],
            environment=data.get("environment", ""),
            total_runs=int(data.get("total_runs", 0)),
            total_tests=int(data.get("total_tests", 0)),
            total_passes=int(data.get("total_passes", 0)),
            total_failures=int(data.get("total_failures", 0)),
            total_skipped=int(data.get("total_skipped", 0)),
            avg_pass_rate=float(data.get("avg_pass_rate", 0.0)),
            avg_failures=float(data.get("avg_failures", 0.0)),
            avg_skipped=float(data.get("avg_skipped", 0.0)),
            last_run_number=int(data.get("last_run_number", 0)),
            last_execution_date=data.get("last_execution_date")
        )

    # Retorna todos os testes que falharam em um período e por projeto
    def get_failed_tests(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[FailedTestSummary]:
        """Retrieves a list of failed tests for a given project within a specified date range."""

        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }

        # Pipeline simplificada que usa diretamente o campo failed_cases
        pipeline = [
            {"$match": query},
            {"$project": {
                "_id": 0,
                "failed_cases": 1,
                "run_number": 1
            }},
            {"$unwind": "$failed_cases"},
            {"$match": {"failed_cases.status": "failed"}},
            {"$project": {
                "_id": 0,
                "name": "$failed_cases.name",
                "message": "$failed_cases.message",
                "run_number": 1
            }},
            # Agrupa cada teste e junta todos os run_numbers distintos
            {"$group": {
                "_id": "$name",
                "run_numbers": {"$addToSet": "$run_number"},
                "last_message": {"$last": "$message"}
            }},
            {"$project": {
                "_id": 0,
                "name": "$_id",
                "run_numbers": 1, # Return unsorted set
                "last_message": 1
            }},
            {"$sort": {"name": 1}}
        ]

        results_list = list(self.adapter.get_collection(
            self.collection).aggregate(pipeline))

        logger.info(
            "Failed tests fetched successfully for project: %s, start_dt: %s, end_dt: %s",
            project, start_dt, end_dt
        )

        return [
            FailedTestSummary(
                name=res.get("name", ""),
                # Sort manually in Python for compatibility
                run_numbers=sorted(res.get("run_numbers", [])),
                last_message=res.get("last_message", "")
            )
            for res in results_list
        ]

    def get_module_health(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[ModuleHealthSummary]:

        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }
        
        pipeline = [
            {"$match": query},
            {"$project": {"test_results": 1}}
        ]
        
        col = self.adapter.get_collection(self.collection)
        cursor = col.aggregate(pipeline)
        
        module_stats = {}

        for doc in cursor:
            for test in doc.get("test_results", []):
                name = test.get("name", "")
                parts = name.split(' - ')[0] if ' - ' in name else name
                module = '.'.join(parts.split('.')[:-1]) if '.' in parts else parts
                if not module:
                    module = parts
                
                status = test.get("status", "")
                is_fail = 1 if status == "failed" else 0
                
                if module not in module_stats:
                    module_stats[module] = {"fail_count": 0, "total_tests": 0}
                
                module_stats[module]["fail_count"] += is_fail
                module_stats[module]["total_tests"] += 1

        results = []
        for mod, stats in module_stats.items():
            fail_count = stats["fail_count"]
            total_tests = stats["total_tests"]
            fail_rate = (fail_count / total_tests) * 100 if total_tests > 0 else 0.0
            
            # Só incluir módulos que tiveram ao menos uma falha para não sujar o gráfico, ou todos?
            # Se queremos o heatmap de defeitos, faz sentido retornar todos.
            results.append(
                ModuleHealthSummary(
                    module_name=mod, 
                    fail_count=fail_count,
                    total_tests=total_tests,
                    failure_rate=round(fail_rate, 2)
                )
            )

        # Ordenar pelos mais problemáticos (maior quantidade de falhas)
        results.sort(key=lambda x: x.fail_count, reverse=True)
        return results

    def get_flaky_tests(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[FlakyTestSummary]:

        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }
        total_runs = self.adapter.get_collection(self.collection).count_documents(query)

        if total_runs == 0:
            return []

        failed_tests = self.get_failed_tests(project, environment, start_dt, end_dt)
        results = []

        for test in failed_tests:
            fail_count = len(test.run_numbers)
            # A test is flaky if it failed at least once, but not in all runs
            if 0 < fail_count < total_runs:
                # 50% fail rate is max instability. Let's calculate standard failure rate.
                failure_rate = (fail_count / total_runs) * 100
                results.append(FlakyTestSummary(
                    test_name=test.name,
                    fail_count=fail_count,
                    instability_score=round(failure_rate, 2)
                ))

        # Sort by failure rate descending
        results.sort(key=lambda x: x.instability_score, reverse=True)
        return results

    def get_trends(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[TrendSummary]:
        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }

        pipeline = [
            {"$match": query},
            {"$group": {
                # Group by day string formatted YYYY-MM-DD
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d", 
                        "date": {"$ifNull": ["$execution_date", "$created_at"]}
                    }
                },
                "total_runs": {"$sum": 1},
                "total_tests": {"$sum": "$total"},
                "total_passes": {"$sum": "$passed"},
                "total_failures": {"$sum": "$failures"},
                "total_skipped": {"$sum": "$skipped"}
            }},
            {"$project": {
                "date": "$_id",
                "total_runs": 1,
                "total_tests": 1,
                "total_failures": 1,
                "total_skipped": 1,
                "avg_pass_rate": {
                    "$cond": [
                        {"$gt": ["$total_tests", 0]},
                        {"$multiply": [{"$divide": ["$total_passes", "$total_tests"]}, 100]},
                        0
                    ]
                }
            }},
            {"$sort": {"date": 1}}
        ]

        cursor = self.adapter.get_collection(self.collection).aggregate(pipeline)

        return [
            TrendSummary(
                date=doc["date"],
                total_runs=doc.get("total_runs", 0),
                total_tests=doc.get("total_tests", 0),
                avg_pass_rate=round(doc.get("avg_pass_rate", 0), 2),
                total_failures=doc.get("total_failures", 0),
                total_skipped=doc.get("total_skipped", 0)
            )
            for doc in cursor
        ]

    def get_test_cases(
            self,
            project: str,
            environment: str) -> List[str]:
        query = {
            "project": project,
            "environment": environment
        }
        col = self.adapter.get_collection(self.collection)
        distinct_tests = col.distinct("test_results.name", query)

        # Filter out None or empty values and sort alphabetically
        valid_tests = sorted([t for t in distinct_tests if t])
        return valid_tests

    def get_mttr(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> MTTRSummary:

        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }

        # We need executions sorted chronologically
        pipeline = [
            {"$match": query},
            {"$sort": {"execution_date": 1, "created_at": 1}},
            {"$project": {"execution_date": 1, "created_at": 1, "test_results": 1}}
        ]

        col = self.adapter.get_collection(self.collection)
        executions = list(col.aggregate(pipeline))

        broken_tests = {}
        recovery_times = []

        for exec_doc in executions:
            execution_time = exec_doc.get("execution_date") or exec_doc.get("created_at")
            doc_id = exec_doc.get("_id")
            tests = exec_doc.get("test_results", [])

            if not tests:
                continue

            for test in tests:
                test_name = test.get("name")
                status = test.get("status")

                if not test_name:
                    continue

                if status == "failed":
                    if test_name not in broken_tests:
                        broken_tests[test_name] = {"execution_time": execution_time, "doc_id": doc_id}
                elif status == "passed":
                    if test_name in broken_tests:
                        broken_info = broken_tests[test_name]
                        broken_time = broken_info["execution_time"]
                        broken_doc_id = broken_info["doc_id"]

                        # Ignore retries within the same run (flaky test successes)
                        if doc_id == broken_doc_id:
                            continue

                        # Compute recovery time only if the timestamp is strictly greater.
                        # This prevents 0-hour skew from bulk imports that share the exact same timestamp.
                        if execution_time > broken_time:
                            recovery_time = (execution_time - broken_time).total_seconds() / 3600.0
                            print(f"DEBUG: Found recovery for {test_name}. exec_time={execution_time}, broken_time={broken_time}, diff={recovery_time}")
                            recovery_times.append(recovery_time)
                            
                        # Test has recovered in a different run, remove it from broken_tests
                        del broken_tests[test_name]

        avg_mttr = 0.0
        if recovery_times:
            avg_mttr = sum(recovery_times) / len(recovery_times)
            print(f"DEBUG: recovery_times array = {recovery_times}, avg={avg_mttr}")

        return MTTRSummary(
            project=project,
            environment=environment,
            mttr_hours=round(avg_mttr, 2),
            total_recoveries=len(recovery_times)
        )

    def get_common_errors(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> List[CommonErrorSummary]:
        
        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }

        pipeline = [
            {"$match": query},
            {"$unwind": "$failed_cases"},
            # Ensure message is not null
            {"$match": {"failed_cases.message": {"$ne": None}}},
            {"$group": {
                "_id": "$failed_cases.message",
                "count": {"$sum": 1},
                "affected_tests": {"$addToSet": "$failed_cases.name"},
                "affected_runs": {"$addToSet": "$run_number"}
            }},
            {"$sort": {"count": -1}}
        ]

        from app.domain.entities.common_error_summary import CommonErrorSummary

        results_list = list(self.adapter.get_collection(self.collection).aggregate(pipeline))

        return [
            CommonErrorSummary(
                message=res["_id"] if res["_id"] else "No message",
                count=res["count"],
                affected_tests=sorted(res.get("affected_tests", [])),
                affected_runs=sorted(res.get("affected_runs", []))
            )
            for res in results_list
        ]

    def get_performance_metrics(
            self,
            project: str,
            environment: str,
            start_dt: datetime,
            end_dt: datetime) -> 'PerformanceMetricsSummary':
        
        query = {
            "project": project,
            "environment": environment,
            "created_at": {"$gte": start_dt, "$lte": end_dt}
        }

        # Calculate average execution time
        pipeline_avg = [
            {"$match": query},
            {"$group": {
                "_id": None,
                "avg_execution_time": {"$avg": "$time"}
            }}
        ]
        
        col = self.adapter.get_collection(self.collection)
        avg_result = list(col.aggregate(pipeline_avg))
        avg_time = avg_result[0]["avg_execution_time"] if avg_result and avg_result[0].get("avg_execution_time") else 0.0

        # Calculate slowest tests
        pipeline_slowest = [
            {"$match": query},
            {"$unwind": "$test_results"},
            {"$group": {
                "_id": "$test_results.name",
                "avg_duration": {"$avg": "$test_results.time"}
            }},
            {"$sort": {"avg_duration": -1}},
            {"$limit": 10}
        ]
        
        slowest_result = list(col.aggregate(pipeline_slowest))
        
        from app.domain.entities.performance_metrics import PerformanceMetricsSummary, SlowestTestSummary
        
        slowest_tests = [
            SlowestTestSummary(
                test_name=res["_id"],
                avg_duration_seconds=res["avg_duration"] or 0.0
            ) for res in slowest_result if res["_id"]
        ]
        
        return PerformanceMetricsSummary(
            project=project,
            environment=environment,
            avg_execution_time_seconds=avg_time,
            slowest_tests=slowest_tests
        )
