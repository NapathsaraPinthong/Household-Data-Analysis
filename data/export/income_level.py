import sys
import os
import pandas as pd

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import client
from data_repository import export_hh_income_level

try:
    db = client['MSO']
    hh_collection = db['Household']
    mb_collection = db['Member']
    
    # Step 1: Query Household collection for non-removed households
    hh_ids = hh_collection.find(
        {'status': {'$ne': 'removed'}},
        {'_id': 1}
    )
    
    # Convert to a list of _id values
    hh_id_list = [household['_id'] for household in hh_ids]
    
    # Step 2: Query Member collection for members with hh_id in the household list
    members = mb_collection.find(
        {'hh_id': {'$in': hh_id_list}, 'status': {'$ne': 'removed'}},
        {'hh_id': 1, '_id': 1, 'sum_income': '$SUM_INCOME' }
    )
    
    # Convert the member query results to a DataFrame
    member_data = list(members)
    df_members = pd.DataFrame(member_data)

    file_path = '../dataset/edge/hh-income_level.xlsx'
    export_hh_income_level(df_members, file_path)
    print(f"DataFrame saved to {file_path}")
    
finally:
    # Ensure the connection is closed even if an error occurs
    client.close()
