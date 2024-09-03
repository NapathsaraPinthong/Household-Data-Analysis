import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from connection import client
from data_repository import *
import pandas as pd

try:
    db = client["MSO"]
    household_collection = db["Household"]
    member_collection = db["Member"]

    def export_oid_to_excel(collection, path_name):
        # Create the pipeline to extract the 'oid'
        pipeline = [
            {"$match": {"status": {"$ne": "removed"}}},
            {"$project": {"_id": 1}},
        ]

        # Execute the aggregation pipeline
        results = list(collection.aggregate(pipeline))
        df = pd.DataFrame(results)

        # Save the DataFrame to an Excel file
        df.to_excel(path_name, index=False, header=False)
        print(f"DataFrame saved to {path_name}")

    export_oid_to_excel(household_collection, "../dataset/node/household.xlsx")
    export_oid_to_excel(member_collection, "../dataset/node/member.xlsx")

finally:
    # Ensure the connection is closed even if an error occurs
    client.close()
