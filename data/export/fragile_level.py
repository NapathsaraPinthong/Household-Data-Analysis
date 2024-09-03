import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import client
from data_repository import *
import pandas as pd

try:
    db = client['MSO']
    hh_collection = db['Household']
    mb_collection = db['Member']
    
    pipeline = [
        {
            '$match': {
                'status': {
                    '$ne': 'removed'
                }
            }
        }, {
            '$lookup': {
                'from': 'Member', 
                'localField': '_id', 
                'foreignField': 'hh_id', 
                'as': 'members'
            }
        }, {
            '$match': {
                'members': {
                    '$ne': []
                }
            }
        }, {
            '$unwind': {
                'path': '$members', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$match': {
                'members.status': {
                    '$ne': 'removed'
                }
            }
        }, {
            '$project': {
                '_id': 0, 
                'hh_id': '$_id', 
                'mb_id': '$members._id', 
                'age': '$members.age', 
                'sum_income': '$members.SUM_INCOME', 
                'is_disabled': '$members.is_disabled', 
                'prob_family': {
                    '$map': {
                        'input': '$members.prob_family', 
                        'as': 'item', 
                        'in': {
                            'code': '$$item.code'
                        }
                    }
                }, 
                'prob_health': {
                    '$map': {
                        'input': '$members.prob_health', 
                        'as': 'item', 
                        'in': {
                            'code': '$$item.code'
                        }
                    }
                }
            }
        }
    ]
    
    # Execute the aggregation pipeline
    results = list(hh_collection.aggregate(pipeline))
    df = pd.DataFrame(results)
        
    #Save the DataFrame to an Excel file
    file_path = '../dataset/edge/hh_fg-level.xlsx'
    export_hh_fg_level(df, file_path)
    print(f"DataFrame saved to {file_path}") 
    
finally:
    # Ensure the connection is closed even if an error occurs
    client.close()
