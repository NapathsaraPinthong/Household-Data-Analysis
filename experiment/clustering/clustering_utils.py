import os
import pandas as pd
import pickle
import numpy as np

def create_and_save_hh_mb_attr_dicts(directory_path, hh_output_file, mb_output_file):
    # Initialize dictionaries for households and members
    hh_attr_dict = {}
    mb_attr_dict = {}

    # Get a list of all files in the specified directory
    files = os.listdir(directory_path)

    # Process each file
    for file_name in files:
        # Determine the full file path
        file_path = os.path.join(directory_path, file_name)

        # Check if the file name matches the household or member file format
        if file_name.startswith("hh-") and file_name.endswith(".xlsx"):
            # Extract the attribute name from the file name, e.g., 'fg_level' from 'hh-fg_level.xlsx'
            attr_name = file_name.split('-')[1].split('.')[0]

            # Load the household data
            hh_df = pd.read_excel(file_path, header=None, names=["hh_id", attr_name])

            # Populate hh_attr_dict with each household's attribute
            for _, row in hh_df.iterrows():
                hh_id = row['hh_id']
                attr_value = row[attr_name]
                
                if hh_id not in hh_attr_dict:
                    hh_attr_dict[hh_id] = {}
                hh_attr_dict[hh_id][attr_name] = attr_value

        elif file_name.startswith("mb-") and file_name.endswith(".xlsx"):
            # Extract the attribute name from the file name, e.g., 'prob_family' from 'mb-prob_family.xlsx'
            attr_name = file_name.split('-')[1].split('.')[0]

            # Load the member data
            mb_df = pd.read_excel(file_path, header=None, names=["mb_id", attr_name])

            # Populate mb_attr_dict with each member's attribute
            for _, row in mb_df.iterrows():
                mb_id = row['mb_id']
                attr_value = row[attr_name]
                
                if mb_id not in mb_attr_dict:
                    mb_attr_dict[mb_id] = {}

                # For attributes with multiple values, store them as lists
                if attr_name in ["prob_family", "prob_health"]:
                    if attr_name not in mb_attr_dict[mb_id]:
                        mb_attr_dict[mb_id][attr_name] = []
                    mb_attr_dict[mb_id][attr_name].append(attr_value)
                else:
                    # Single-valued attributes
                    mb_attr_dict[mb_id][attr_name] = attr_value

    # Save the dictionaries to files using pickle
    with open(hh_output_file, 'wb') as hh_file:
        pickle.dump(hh_attr_dict, hh_file)
        print(f"Household attributes dictionary saved to {hh_output_file}")

    with open(mb_output_file, 'wb') as mb_file:
        pickle.dump(mb_attr_dict, mb_file)
        print(f"Member attributes dictionary saved to {mb_output_file}")

def evaluate_fg_level_distribution(file_path, attributes_dict_path):
    # Read the clustering results from the Excel file
    cluster_df = pd.read_excel(file_path)

    # Load the household attributes dictionary
    with open(attributes_dict_path, 'rb') as file:
        household_attributes = pickle.load(file)

    # Map the cluster IDs to their corresponding fg_levels using the household attributes
    # Remove the 'hh' prefix and convert to np.int64 for mapping
    cluster_df['fg_level'] = cluster_df['node_id'].apply(
        lambda x: household_attributes.get(np.int64(int(x[2:])), {}).get('fg_level')
    )

    # Check for any missing fg_level values
    if cluster_df['fg_level'].isnull().any():
        missing_ids = cluster_df[cluster_df['fg_level'].isnull()]['node_id']
        print("Warning: Some 'fg_level' values could not be found in the attributes dictionary.")
        print("Missing node_ids:")
        print(missing_ids)

    # Calculate the count of each fg_level within each cluster
    fg_level_distribution = cluster_df.groupby(['cluster', 'fg_level']).size().unstack(fill_value=0)

    # Calculate the percentage distribution of fg_level in each cluster
    fg_level_percentage = fg_level_distribution.div(fg_level_distribution.sum(axis=1), axis=0) * 100

    # Display the percentage distribution
    print("Percentage distribution of fg_level within each cluster using " + file_path)
    print(fg_level_percentage)

import pandas as pd
import pickle

import pandas as pd
import numpy as np
import pickle

def analyze_cluster_attributes(cluster_file, hh_member_dict_file, household_attributes_file, member_attributes_file):
    # Load cluster data
    cluster_df = pd.read_excel(cluster_file)

    # Remove 'hh' prefix and convert to np.int64 for consistent lookups
    cluster_df['node_id'] = cluster_df['node_id'].apply(lambda x: np.int64(int(x[2:])))

    # Load household-member mapping
    with open(hh_member_dict_file, 'rb') as f:
        hh_member_dict = pickle.load(f)
    
    # Load household and member attributes
    with open(household_attributes_file, 'rb') as f:
        household_attributes = pickle.load(f)
        
    with open(member_attributes_file, 'rb') as f:
        member_attributes = pickle.load(f)

    # Prepare a dictionary to hold count data for each cluster and attribute
    attribute_counts = {}

    # Iterate over clusters in the cluster file
    for cluster_id in sorted(cluster_df['cluster'].unique()):
        cluster_households = cluster_df[cluster_df['cluster'] == cluster_id]['node_id']
        
        # Initialize the counts for this cluster
        cluster_counts = {
            'income_level1': 0, 'income_level2': 0, 'solid0': 0, 'solid1': 0,
            'fg_level-1': 0, 'fg_level0': 0, 'fg_level1': 0, 'fg_level2': 0, 'fg_level3': 0,
            'age1': 0, 'age2': 0, 'age3': 0, 'age4': 0, 'age5': 0,
            'disabled0': 0, 'disabled1': 0,
            # Prob family and health levels
            **{f'prob_family{i}': 0 for i in range(1, 26)},
            **{f'prob_health{i}': 0 for i in range(1, 14)}
        }

        # Process each household in the cluster
        for hh_id in cluster_households:
            # Get household attributes
            hh_attributes = household_attributes.get(hh_id, {})
            # Update household-related attributes
            for attr, value in hh_attributes.items():
                attr = attr + str(value)
                if attr in cluster_counts:
                    cluster_counts[attr] += 1
            
            # Process each member in the household
            members = hh_member_dict.get(hh_id, [])
            for member_id in members:
                # Remove 'mb' prefix, convert to np.int64 for member attributes lookup
                member_id = np.int64(int(member_id))
                member_attributes_data = member_attributes.get(member_id, {})

                # Update member-related attributes
                for attr, value in member_attributes_data.items():
                    # Handle prob_family and prob_health as lists
                    if attr in ["prob_family", "prob_health"]:
                        for val in value:
                            list_attr = f"{attr}{val}"
                            if list_attr in cluster_counts:
                                cluster_counts[list_attr] += 1
                    else:
                        # Handle single-valued attributes
                        attr = attr + str(value)
                        if attr in cluster_counts:
                            cluster_counts[attr] += 1

        # Store the counts for this cluster
        attribute_counts[cluster_id] = cluster_counts

    # Convert the attribute_counts dictionary into a DataFrame
    results_df = pd.DataFrame.from_dict(attribute_counts, orient='index').reset_index()
    results_df = results_df.rename(columns={'index': 'Cluster'})

    # Export or print the result
    print(results_df)
    output_file = f'./analysis/{cluster_file.split("/")[2].split(".")[0]}_attributes_analysis.xlsx'
    results_df.to_excel(output_file, index=False)
    print(f"Analysis results saved to '{output_file}'")

### Example usage ###

# create_and_save_hh_mb_attr_dicts('../../data/dataset/edge', '../static/household_attributes.pkl', '../static/member_attributes.pkl')

# evaluate_fg_level_distribution(
#     file_path='./result/hierarchical_clusters_k3.xlsx',
#     attributes_dict_path='../static/household_attributes.pkl'
# )

# analyze_cluster_attributes(
#     cluster_file='./result/hierarchical_clusters_k3.xlsx',
#     hh_member_dict_file='../static/hh_member_dict.pkl',
#     household_attributes_file='../static/household_attributes.pkl',
#     member_attributes_file='../static/member_attributes.pkl'
# )