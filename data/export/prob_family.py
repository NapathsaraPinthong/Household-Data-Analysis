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
        '$match': {
            'status': {
                '$ne': 'removed'
            }
        }
    },{
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
            'preserveNullAndEmptyArrays': False
        }
    }
]
    
    # Execute the aggregation pipeline
    results = list(mb_collection.aggregate(pipeline))
    df = pd.DataFrame(results)
    df = extract_number_from_code(df, 'prob_family')
        
    #Save the DataFrame to an Excel file
    file_path = '../dataset/edge/mb-prob_family.xlsx'
    df.to_excel(file_path, index=False, header=False)
    print(f"DataFrame saved to {file_path}") 
    
finally:
    # Ensure the connection is closed even if an error occurs
    client.close()
