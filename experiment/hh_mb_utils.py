import pandas as pd
import numpy as np
import ast

# Extract the node IDs based on the input household id
def get_node_id_in_household(hh_id):
    file_path = "../data/dataset/edge/mb-hh.xlsx"
    column_names = ["mb_id", "hh_id"]

    df = pd.read_excel(file_path, header=None, names=column_names)
    filtered_df = df[df["hh_id"] == hh_id]
    node_ids = filtered_df["mb_id"].tolist()

    return node_ids

# Convert a string representation of a list to an actual list of floats
def parse_vector(vector_str):
    return np.array(ast.literal_eval(vector_str))

# Calculate Euclidean distance between all member nodes and their household
def calculate_distance_in_household(hh_id, embedding_df):
    # Get the coordinates of the household node
    hh_coord_str = embedding_df.loc[embedding_df["node_id"] == "hh" + str(hh_id), "value"].values[0]
    node_list = get_node_id_in_household(hh_id)

    distances = []

    for node in node_list:
        # Get the coordinates of the current member node
        node_coord_str = embedding_df.loc[embedding_df["node_id"] == "mb" + str(node), "value"].values[0]

        hh_coord = parse_vector(hh_coord_str)
        node_coord = parse_vector(node_coord_str)

        # Calculate the Euclidean distance between the member node and the household node
        distance = np.linalg.norm(node_coord - hh_coord)
        distances.append(distance)

    if distances:
        # Calculate the average distance
        average_distance = round(np.mean(distances), 5)
    else:
        average_distance = 0

    return average_distance
