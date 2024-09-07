import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import client
from data_repository import *
import pandas as pd

try:
    db = client['MSO']
    hh_collection = db['Household']

    pipeline = [
        {"$match": {"status": {"$ne": "removed"}}},
        {
            '$project': {
                '_id': 1,
                'province_code': 1
            }
        }
    ]

    # Execute the aggregation pipeline
    results = list(hh_collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    # Save the DataFrame to an Excel file without headers
    file_path = '../dataset/edge/hh-province_code.xlsx'
    df.to_excel(file_path, index=False, header=False)
    print(f"DataFrame saved to {file_path}")

finally:
    # Ensure the connection is closed even if an error occurs
    client.close()