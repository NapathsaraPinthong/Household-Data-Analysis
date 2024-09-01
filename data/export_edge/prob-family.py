import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import client
from data_repository import *
import pandas as pd

try:
    db = client['MSO']
    mb_collection = db['Member']
    
    pipeline = [
    {
        '$project': {
            'prob_family': {
                '$map': {
                    'input': '$prob_family', 
                    'as': 'item', 
                    'in': '$$item.code'
                }
            }
        }
    }, {
        '$unwind': {
            'path': '$prob_family', 
            'preserveNullAndEmptyArrays': True
        }
    }
]
    
    # Execute the aggregation pipeline
    results = list(mb_collection.aggregate(pipeline))
    df = pd.DataFrame(results)
        
    #Save the DataFrame to an Excel file
    file_path = '../dataset/edge/mb_prob-family.xlsx'
    df.to_excel(file_path, index=False, header=False)
    print(f"DataFrame saved to {file_path}") 
    
finally:
    # Ensure the connection is closed even if an error occurs
    client.close()
