import os
from pymongo import MongoClient
from datetime import datetime, timedelta

def run():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["test_results"]
    collection = db["runs"]

    runs = list(collection.find().sort("run_number", 1))

    total_runs = len(runs)
    if total_runs == 0:
        print("No runs found.")
        return

    print(f"Found {total_runs} runs. Updating dates...")

    now = datetime.utcnow()

    for index, doc in enumerate(runs):
        # Shift back by (total_runs - 1 - index) days
        # If 8 runs: index 0 -> 7 days ago, index 7 -> today
        days_ago = (total_runs - 1) - index
        new_date = now - timedelta(days=days_ago)

        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"created_at": new_date}}
        )
        print(f"Run {doc['run_number']} updated to {new_date.strftime('%Y-%m-%d')}")

    print("Successfully updated dates!")

if __name__ == "__main__":
    run()
