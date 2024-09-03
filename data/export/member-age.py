import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import client
from data_repository import *
import pandas as pd

try:
    db = client['MSO']
    member_collection = db['Member']

    # Define the aggregation pipeline to extract the 'oid' from '_id' and 'hh_id' fields
    pipeline = [
        {"$match": {"status": {"$ne": "removed"}}},
        {
            '$project': {
                '_id': 1,
                'age': 1
            }
        }
    ]

    # Execute the aggregation pipeline
    results = list(member_collection.aggregate(pipeline))
    df = pd.DataFrame(results)

    # Assign age group based on current age
    df['age_group'] = df['age'].apply(assign_age_group)

    # Prepare DataFrame for export with member ID and age group
    df = df[['_id', 'age_group']]

    # Save the DataFrame to an Excel file without headers
    file_path = '../dataset/edge/mb-age.xlsx'
    df.to_excel(file_path, index=False, header=False)
    print(f"DataFrame saved to {file_path}")

finally:
    # Ensure the connection is closed even if an error occurs
    client.close()