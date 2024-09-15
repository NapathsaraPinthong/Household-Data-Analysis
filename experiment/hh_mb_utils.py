import pickle
import random
import pandas as pd
import numpy as np
import ast

# Function to sample 700 household IDs and save to a CSV file
def sample_and_save_households(hh_file_path, output_file, sample_size=7000):
    hh_df = pd.read_excel(hh_file_path, header=None, names=["mb_id", "hh_id"])
    
    # Drop duplicates and keep only unique household IDs with members
    unique_hh_ids = hh_df["hh_id"].unique()
    
    # Check if we have enough households with members to sample
    if len(unique_hh_ids) < sample_size:
        raise ValueError("Not enough households with members to sample the desired number.")
    
    # Randomly sample the household IDs and save it to a CSV file
    sampled_hh_ids = random.sample(list(unique_hh_ids), sample_size)
    pd.DataFrame(sampled_hh_ids, columns=["hh_id"]).to_csv(output_file, index=False)
    print(f"Sampled households saved to {output_file}")

def load_sampled_households(sample_file):
    sampled_hh_df = pd.read_csv(sample_file)
    return sampled_hh_df["hh_id"].tolist()

def create_and_save_hh_member_dict(mb_hh_file_path, output_file):
    # Load the data
    mb_hh_df = pd.read_excel(mb_hh_file_path, header=None, names=["mb_id", "hh_id"])

    # Create a dictionary to store household-member mappings
    hh_member_dict = {}

    # Populate the hh_member_dict
    for _, row in mb_hh_df.iterrows():
        hh_id = row['hh_id']
        mb_id = row['mb_id']
        
        if hh_id not in hh_member_dict:
            hh_member_dict[hh_id] = []
        hh_member_dict[hh_id].append(mb_id)

    # Save the hh_member_dict to a file using pickle
    with open(output_file, 'wb') as file:
        pickle.dump(hh_member_dict, file)
    
    print(f"hh_member_dict saved to {output_file}")

def load_hh_member_dict(filename):
    with open(filename, 'rb') as file:
        hh_member_dict = pickle.load(file)
    return hh_member_dict

# Create a dictionary to store node embeddings
def create_embedding_dict(embedding_df):
    embedding_dict = {}
    for _, row in embedding_df.iterrows():
        node_id = row["node_id"]
        embedding_value = parse_vector(row["value"])
        embedding_dict[node_id] = embedding_value
    return embedding_dict

# Convert a string representation of a list to an actual list of floats
def parse_vector(vector_str):
    return np.array(ast.literal_eval(vector_str))

# Calculate Euclidean distance between all member nodes and their household and return average distance of all
def calculate_distance_for_households(hh_id_list, embedding_dict, hh_member_dict):
    all_avg_distances = []

    for hh_id in hh_id_list:
        # Check if the hh_id exists in the hh_member_dict
        if hh_id not in hh_member_dict:
            print(f"Household ID {hh_id} not found in hh_member_dict.")
            continue
        
        hh_coord = embedding_dict.get("hh" + str(hh_id), None)
        if hh_coord is None:
            print(f"No coordinates found for household ID {hh_id} in embedding_dict.")
            continue
        
        node_list = hh_member_dict[hh_id]
        distances = []

        for node in node_list:
            node_coord = embedding_dict.get("mb" + str(node), None)
            if node_coord is None:
                print(f"No coordinates found for member ID {node} in embedding_dict.")
                continue
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(node_coord - hh_coord)
            distances.append(distance)
        
        if distances:
            # Calculate average distance for this household
            average_distance = np.mean(distances)
            all_avg_distances.append(average_distance)
    
    if all_avg_distances:
        # Calculate overall average distance
        overall_average_distance = round(np.mean(all_avg_distances), 5)
    else:
        overall_average_distance = 0

    return overall_average_distance

# -------- Call this function to sample households once and save the result -------- #
# sample_and_save_households("../data/dataset/edge/mb-hh.xlsx", "./static/sampled_households.csv")

# -------- Re-create a household-member dictionary if dataset has changed -------- #
# create_and_save_hh_member_dict('../data/dataset/edge/mb-hh.xlsx', './static/hh_member_dict.pkl')