import pandas as pd
import numpy as np
import ast

# Extract the node IDs based on the input fragile level
def get_node_id_in_fragile_level(fg_level):
    file_path = "../data/dataset/edge/hh-fg_level.xlsx"
    column_names = ["hh_id", "fragile_level"]

    df = pd.read_excel(file_path, header=None, names=column_names)
    filtered_df = df[df["fragile_level"] == fg_level]
    node_ids = filtered_df["hh_id"].tolist()

    return node_ids

# Convert a string representation of a list to an actual list of floats
def parse_vector(vector_str):
    return np.array(ast.literal_eval(vector_str))

# Calculate Euclidean distance between all nodes in same Fragile Level
def calculate_distance_in_fragile_level(fg_level, embedding_df):
    node_list = get_node_id_in_fragile_level(fg_level)
    distances = []

    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            # Get the coordinates of the nodes
            coord1_str = embedding_df.loc[
                embedding_df["node_id"] == "hh" + str(node_list[i]), "value"
            ].values[0]
            coord2_str = embedding_df.loc[
                embedding_df["node_id"] == "hh" + str(node_list[j]), "value"
            ].values[0]

            coord1 = parse_vector(coord1_str)
            coord2 = parse_vector(coord2_str)

            # Calculate Euclidean distance
            distance = np.linalg.norm(coord1 - coord2)
            distances.append(distance)

    if distances:
        # Calculate the average distance
        average_distance = round(np.mean(distances), 5)
    else:
        average_distance = 0.0

    return average_distance

# Calculate the centroid of nodes in a given fragile level
def calculate_centroid(fg_level, embedding_df):
    node_list = get_node_id_in_fragile_level(fg_level)
    vectors = []

    for node in node_list:
        # Get the coordinates of the node
        coord_str = embedding_df.loc[
            embedding_df["node_id"] == "hh" + str(node), "value"
        ].values[0]
        coord = parse_vector(coord_str)
        vectors.append(coord)

    if vectors:
        # Calculate the centroid by averaging all vectors
        centroid = np.mean(vectors, axis=0)
    else:
        centroid = None

    return centroid

# Calculate the distance between centroids of all pairs
def calculate_all_centroid_distances(centroids):
    levels = list(centroids.keys())
    distances = {}

    for i in range(len(levels)):
        for j in range(i + 1, len(levels)):
            fg_level_1 = levels[i]
            fg_level_2 = levels[j]

            # Check if both centroids exist before calculating distance
            centroid_1 = centroids[fg_level_1]
            centroid_2 = centroids[fg_level_2]

            if centroid_1 is not None and centroid_2 is not None:
                # Calculate the distance between two centroids
                distance = np.linalg.norm(centroid_1 - centroid_2)
                distances[(fg_level_1, fg_level_2)] = round(distance, 5)
            else:
                # If one or both centroids are None, indicate no valid distance
                distances[(fg_level_1, fg_level_2)] = None

    return distances