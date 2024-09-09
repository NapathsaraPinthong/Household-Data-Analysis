import sys
import os
import pandas as pd

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import client
from data_repository import export_hh_fg_level

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
        {
            'hh_id': 1, 
            'mb_id': '$_id', 
            'age': 1, 
            'sum_income': '$SUM_INCOME', 
            'is_disabled': 1, 
            'prob_family': 1, 
            'prob_health': 1
        }
    )
    # Step 3: Process the member data and extract 'code' from prob_family and prob_health
    member_data = []
    for member in members:
        if member.get('prob_family') is not None:
            member['prob_family'] = [item['code'] for item in member['prob_family'] if item]
        else:
            member['prob_family'] = []
        
        if member.get('prob_health') is not None:
            member['prob_health'] = [item['code'] for item in member['prob_health'] if item]
        else:
            member['prob_health'] = []
        
        member_data.append(member)
    
    # Convert the processed data to a DataFrame
    df_members = pd.DataFrame(member_data)
    
    # Step 4: Save the DataFrame to an Excel file
    file_path = '../dataset/edge/hh-fg_level.xlsx'
    export_hh_fg_level(df_members, file_path)
    print(f"DataFrame saved to {file_path}")
    
finally:
    # Ensure the connection is closed even if an error occurs
    client.close()
