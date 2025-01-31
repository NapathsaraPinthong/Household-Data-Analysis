import pandas as pd
import numpy as np


# Check if member is dependent based on the given criteria
def is_dependent(member):
    is_child = 0 <= member["age"] <= 18
    is_single_parent = False
    is_senior = False
    is_disabled = member.get("is_disabled", 0) == 1
    is_patient = False

    if isinstance(member["prob_family"], list):
        is_single_parent = any(code in ["PBFA14", "PBFA25"] for code in member["prob_family"])

    if isinstance(member["prob_health"], list):
        is_patient = any(code in ["PBHE4", "PBHE8"] for code in member["prob_health"])

    if "age" in member:
        is_senior = member["age"] >= 60

    return is_child or is_single_parent or is_senior or is_disabled or is_patient


# Determine fragile level based on criteria
def determine_fg_level(row):
    if row["avg_income"] * 12  >= 100000 and row["num_dependents"] >= 1:
        return 0
    elif row["avg_income"] * 12  < 100000 and row["num_dependents"] == 0:
        return 1
    elif row["avg_income"] * 12  < 100000 and 1 <= row["num_dependents"] <= 2:
        return 2
    elif row["avg_income"] * 12  < 100000 and row["num_dependents"] > 2:
        return 3
    else:
        return -1  


# Determine income level based on criteria
def determine_income_level(row):
    if pd.isna(row["avg_income"]):
        return np.nan  
    elif row["avg_income"] * 12 < 100000:
        return 1
    elif row["avg_income"] * 12 >= 100000:
        return 2


def export_hh_income_level(df, path_name):
    household_summary = (
        df.groupby("hh_id")
        .agg(
            total_income=pd.NamedAgg(column="sum_income", aggfunc="sum"),
            num_members=pd.NamedAgg(column="hh_id", aggfunc="size")
        )
        .reset_index()
    )

    # Calculate average income per person
    household_summary["avg_income"] = (
        household_summary["total_income"] / household_summary["num_members"]
    )

    household_summary["income_level"] = household_summary.apply(
        determine_income_level, axis=1
    )
    export_df = household_summary[["hh_id", "income_level"]].copy()
    export_df.to_excel(path_name, index=False, header=False)


def export_hh_fg_level(df, path_name):
    # Calculate if each member is dependent
    df["is_dependent"] = df.apply(is_dependent, axis=1)
    
    # Aggregate household income and count dependents for each household
    household_summary = (
        df.groupby("hh_id")
        .agg(
            total_income=pd.NamedAgg(column="sum_income", aggfunc="sum"),
            num_dependents=pd.NamedAgg(column="is_dependent", aggfunc="sum"),
            num_members=pd.NamedAgg(column="hh_id", aggfunc="size")
        )
        .reset_index()
    )

    # Calculate average income per person
    household_summary["avg_income"] = (
        household_summary["total_income"] / household_summary["num_members"]
    )

    household_summary["fg_level"] = household_summary.apply(determine_fg_level, axis=1)
  
    export_df = household_summary[["hh_id", "fg_level"]].copy()
    export_df.to_excel(path_name, index=False, header=False)


def assign_age_group(age):
    if age < 6:
        return 1
    elif age < 12:
        return 2
    elif age < 18:
        return 3
    elif age < 60:
        return 4
    else:
        return 5


def extract_number_from_code(df, column_name):
    # Only extract numeric portion if the value is not null
    df[column_name] = df[column_name].apply(
        lambda x: int("".join(filter(str.isdigit, x))) if pd.notnull(x) else x
    )
    return df
