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

