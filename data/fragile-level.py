from connection import client
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
    
    def export_hh_fg_level(df, path_name):
        def is_dependent(member):
            # Check if member is dependent based on the given criteria
            is_child = 0 <= member['age'] <= 18
            is_single_parent = False
            if isinstance(member['prob_family'], list):
                is_single_parent = any(code in ['PBFA14', 'PBFA25'] for code in [item.get('code') for item in member['prob_family']])

            is_senior = member['age'] >= 60
            is_disabled = member['is_disabled'] == 1
            is_patient = False
            if isinstance(member['prob_health'], list):
                is_patient = any(code in ['PBHE4', 'PBHE8'] for code in [item.get('code') for item in member['prob_health']])

            return is_child or is_single_parent or is_senior or is_disabled or is_patient

        # Calculate if each member is dependent
        df['is_dependent'] = df.apply(is_dependent, axis=1)

        # Aggregate household income and count dependents for each household
        household_summary = df.groupby('hh_id').agg(
            total_income=pd.NamedAgg(column='sum_income', aggfunc='sum'),
            num_dependents=pd.NamedAgg(column='is_dependent', aggfunc='sum')
        ).reset_index()

        # Determine fragile level based on criteria
        def determine_fg_level(row):
            if row['total_income'] >= 100000 and row['num_dependents'] >= 1:
                return 0
            elif row['total_income'] < 100000 and row['num_dependents'] == 0:
                return 1
            elif row['total_income'] < 100000 and 1 <= row['num_dependents'] <= 2:
                return 2
            elif row['total_income'] < 100000 and row['num_dependents'] > 2:
                return 3
            else:
                return -1  # Just in case there's an unexpected situation

        household_summary['fg_level'] = household_summary.apply(determine_fg_level, axis=1)

        # Merge the fg_level back to the original DataFrame
        df = df.merge(household_summary[['hh_id', 'fg_level']], on='hh_id', how='left')
        
        # Prepare DataFrame for export with member ID and income level
        export_df = df[['hh_id', 'fg_level']].copy()

        # Export to Excel without header
        export_df.to_excel(path_name, index=False, header=False)
        
    #Save the DataFrame to an Excel file
    file_path = 'hh_fg-level.xlsx'
    export_hh_fg_level(df, file_path)
    print(f"DataFrame saved to {file_path}") 
    
finally:
    # Ensure the connection is closed even if an error occurs
    client.close()
