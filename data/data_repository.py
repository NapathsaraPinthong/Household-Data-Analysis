import pandas as pd
import numpy as np


# Check if member is dependent based on the given criteria
def is_dependent(member):
    is_child = 0 <= member['age'] <= 18
    is_single_parent = False
    is_senior = False  
    is_disabled = member.get('is_disabled', 0) == 1
    is_patient = False

    if isinstance(member['prob_family'], list):
        is_single_parent = any(code in ['PBFA14', 'PBFA25'] for code in [item.get('code') for item in member['prob_family']])

    if isinstance(member['prob_health'], list):
        is_patient = any(code in ['PBHE4', 'PBHE8'] for code in [item.get('code') for item in member['prob_health']])

    if 'age' in member:
        is_senior = member['age'] >= 60

    return is_child or is_single_parent or is_senior or is_disabled or is_patient

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

# Determine income level based on criteria
def determine_income_level(row):
    if pd.isna(row['total_income']):
        return np.nan  # Handle NaN values
    elif row['total_income'] < 100000:
        return 1
    elif row['total_income'] >= 100000:
        return 2

def export_hh_income_level(df, path_name):
    household_summary = df.groupby('hh_id').agg(
        total_income=pd.NamedAgg(column='sum_income', aggfunc='sum')
    ).reset_index()
    household_summary['income_level'] = household_summary.apply(determine_income_level, axis=1)
    df_summary = df.merge(household_summary[['hh_id', 'income_level']], on='hh_id', how='left')
    export_df = df_summary[['hh_id', 'income_level']].copy()
    export_df.to_excel(path_name, index=False, header=False)
    

def export_hh_fg_level(df, path_name):
    # Calculate if each member is dependent
    df['is_dependent'] = df.apply(is_dependent, axis=1)
    # Aggregate household income and count dependents for each household
    household_summary = df.groupby('hh_id').agg(
        total_income=pd.NamedAgg(column='sum_income', aggfunc='sum'),
        num_dependents=pd.NamedAgg(column='is_dependent', aggfunc='sum')
    ).reset_index()
    household_summary['fg_level'] = household_summary.apply(determine_fg_level, axis=1)
    # Merge the fg_level back to the original DataFrame
    df = df.merge(household_summary[['hh_id', 'fg_level']], on='hh_id', how='left')
    
    # Prepare DataFrame for export with member ID and income level
    export_df = df[['hh_id', 'fg_level']].copy()
    # Export to Excel without header
    export_df.to_excel(path_name, index=False, header=False)
