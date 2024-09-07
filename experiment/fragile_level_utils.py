import pandas as pd
import numpy as np
import ast

# Function to get a 10% sample group from each province and save to a static file
def get_sample_group_with_embeddings_and_fg_level(province_codes, embedding_df, sample_percentage=0.1):
    file_path = "../data/dataset/edge/hh-province_code.xlsx"
    column_names = ["hh_id", "province_code"]
    df = pd.read_excel(file_path, header=None, names=column_names)

    fg_level_file = "../data/dataset/edge/hh-fg_level.xlsx"
    fg_level_column_names = ["hh_id", "fragile_level"]
    fg_level_df = pd.read_excel(fg_level_file, header=None, names=fg_level_column_names)
    
    sample_groups = pd.DataFrame()

    for province in province_codes:
        province_df = df[df["province_code"] == province]
        sample_size = int(len(province_df) * sample_percentage)
        sample = province_df.sample(n=sample_size, random_state=42)  
        sample_groups = pd.concat([sample_groups, sample])

    # Add embedding values for each sampled node
    sample_groups["node_id"] = "hh" + sample_groups["hh_id"].astype(str)
    merged_sample = pd.merge(sample_groups, embedding_df, how="left", on="node_id")
    merged_sample = merged_sample[["hh_id", "value"]]

    #Add fragile level for each sampled node
    fg_merged_sample = pd.merge(merged_sample, fg_level_df, how="left", on="hh_id")
    fg_merged_sample = fg_merged_sample[["hh_id", "value", "fragile_level"]]

    # Save the sample group with embeddings to a file
    save_path = "./static/sample_group_with_embeddings.csv"
    fg_merged_sample.to_csv(save_path, index=False)
    print(f"Sample group with embeddings saved to {save_path}")

# Function to get node IDs in a specific fragile level
def get_embeddings_dict_in_fragile_level(fg_level, file_path="./static/sample_group_with_embeddings.csv"):
    df = pd.read_csv(file_path)
    filtered_df = df[df["fragile_level"] == fg_level]
    
    # Return the embeddings for those node IDs as a dictionary for further use
    embeddings_dict = dict(zip(filtered_df["hh_id"], filtered_df["value"].apply(eval)))  
    
    return embeddings_dict

# Function to calculate Euclidean distance within nodes in the same fragile level (Intra distance)
def calculate_distance_in_fragile_level(fg_level, file_path="./static/sample_group_with_embeddings.csv"):
    
    # Retrieve the embedding values for the nodes in the same fragile level
    embeddings_dict = get_embeddings_dict_in_fragile_level(fg_level, file_path) 
    embeddings = list(embeddings_dict.values())
    
    # Calculate the Euclidean distances between all pairs of embeddings
    distances = []
    
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            # Calculate Euclidean distance
            distance = np.linalg.norm(np.array(embeddings[i]) - np.array(embeddings[j]))
            distances.append(distance)
    
    # Calculate and return the average distance
    if distances:
        average_distance = round(np.mean(distances), 5)
    else:
        average_distance = 0.0

    return average_distance

# Function to calculate the centroid of nodes in a given fragile level
def calculate_centroid(fg_level, file_path="./static/sample_group_with_embeddings.csv"):
    embeddings_dict = get_embeddings_dict_in_fragile_level(fg_level, file_path)
    embeddings = list(embeddings_dict.values())
    
    if embeddings:
        # Calculate the centroid by averaging all vectors
        centroid = np.mean(embeddings, axis=0)
    else:
        centroid = None

    return centroid

# Function to calculate the distance between centroids of all pairs (Inter distance)
def calculate_all_centroid_distances(file_path="./static/sample_group_with_embeddings.csv"):
    df = pd.read_csv(file_path)
    valid_levels = [-1, 0, 1, 2, 3]
    df_filtered = df[df["fragile_level"].isin(valid_levels)]
    fragile_levels = df_filtered["fragile_level"].unique()
    
    # Calculate centroids for each fragile level
    centroids = {}
    for fg_level in fragile_levels:
        centroids[fg_level] = calculate_centroid(fg_level, file_path)

    # Calculate the distance between centroids for each pair of fragile levels
    levels = list(centroids.keys())
    distances = {}
    
    for i in range(len(levels)):
        for j in range(i + 1, len(levels)):
            fg_level_1 = levels[i]
            fg_level_2 = levels[j]
            
            centroid_1 = centroids[fg_level_1]
            centroid_2 = centroids[fg_level_2]
            
            if centroid_1 is not None and centroid_2 is not None:
                # Calculate Euclidean distance between two centroids
                distance = np.linalg.norm(centroid_1 - centroid_2)
                distances[(fg_level_1, fg_level_2)] = round(distance, 5)
            else:
                distances[(fg_level_1, fg_level_2)] = None  # Handle missing centroids

    return distances

