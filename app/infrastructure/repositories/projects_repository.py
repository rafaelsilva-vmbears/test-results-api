from typing import Any, Dict, List, Optional
from app.infrastructure.db.interfaces.database_adapter_interface import DatabaseAdapterInterface

class ProjectsRepository:
    def __init__(self, adapter: DatabaseAdapterInterface):
        self.adapter = adapter
        self.collection = "projects"

    def list_projects(self, name: Optional[str], limit: int) -> List[Dict[str, Any]]:
        pipeline = []

        # 1. Match filter (if name provided)
        if name:
            pipeline.append({"$match": {"name": {"$regex": name, "$options": "i"}}})

        # 2. Sort by last_seen_at desc
        pipeline.append({"$sort": {"last_seen_at": -1}})

        # 3. Limit (optimization: limit before lookup)
        pipeline.append({"$limit": limit})

        # 4. Lookup counters to find environments
        pipeline.append({
            "$lookup": {
                "from": "counters",
                "localField": "_id",
                "foreignField": "_id",
                "as": "counter_info"
            }
        })

        # 5. Extract environments from counter_info[0].seq keys
        pipeline.append({
            "$addFields": {
                "counter_doc": {"$arrayElemAt": ["$counter_info", 0]}
            }
        })

        pipeline.append({
            "$addFields": {
                "environments": {
                    "$cond": {
                        "if": {"$ifNull": ["$counter_doc.seq", False]},
                        "then": {
                            "$map": {
                                "input": {"$objectToArray": "$counter_doc.seq"},
                                "as": "kv",
                                "in": {
                                    "name": "$$kv.k",
                                    "total_runs": "$$kv.v"
                                }
                            }
                        },
                        "else": []
                    }
                }
            }
        })

        # 6. Project final fields (hide lookup artifacts)
        pipeline.append({"$project": {"counter_info": 0, "counter_doc": 0}})

        # Execute aggregation
        # Note: We execute on projects collection
        docs = list(self.adapter.get_collection(self.collection).aggregate(pipeline))

        # Map _id to id to match Adapter standard behavior
        for doc in docs:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])

        return docs
