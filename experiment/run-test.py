import pandas as pd
from fragile_level_utils import *
from hh_mb_utils import *

file_path = "../main/node_embeddings.xlsx"
column_names = ["node_id", "value", "node_target"]
embedding_df = pd.read_excel(file_path, header=None, names=column_names)

# -------- Usage -------- #
distance_lv_minus_1 = calculate_distance_in_fragile_level(-1, embedding_df)
distance_lv0 = calculate_distance_in_fragile_level(0, embedding_df)
distance_lv1 = calculate_distance_in_fragile_level(1, embedding_df)
distance_lv2 = calculate_distance_in_fragile_level(2, embedding_df)
distance_lv3 = calculate_distance_in_fragile_level(3, embedding_df)

print(f"Level -1: {distance_lv_minus_1}")
print(f"Level 0: {distance_lv0}")
print(f"Level 1: {distance_lv1}")
print(f"Level 2: {distance_lv2}")
print(f"Level 3: {distance_lv3}")

distance_hh1 = calculate_distance_in_household(5244898460, embedding_df)
distance_hh2 = calculate_distance_in_household(8501888293, embedding_df)
distance_hh3 = calculate_distance_in_household(1873160590, embedding_df)
distance_hh4 = calculate_distance_in_household(5719322689, embedding_df)
distance_hh5 = calculate_distance_in_household(8478917799, embedding_df)

print(f"House 1: {distance_hh1}")
print(f"House 2: {distance_hh2}")
print(f"House 3: {distance_hh3}")
print(f"House 4: {distance_hh4}")
print(f"House 5: {distance_hh5}")

# -------- Calculate Centroids for Each Level -------- #
centroid_lv_minus_1 = calculate_centroid(-1, embedding_df)
centroid_lv0 = calculate_centroid(0, embedding_df)
centroid_lv1 = calculate_centroid(1, embedding_df)
centroid_lv2 = calculate_centroid(2, embedding_df)
centroid_lv3 = calculate_centroid(3, embedding_df)

centroids = {
    -1: centroid_lv_minus_1,
    0: centroid_lv0,
    1: centroid_lv1,
    2: centroid_lv2,
    3: centroid_lv3
}

# Calculate centroid distances
centroid_distances = calculate_all_centroid_distances(centroids)

# Print centroid distances for all combinations
for (level_1, level_2), distance in centroid_distances.items():
    if distance is not None:
        print(f"Distance between Fragile Level {level_1} and {level_2}: {distance}")
    else:
        print(f"Distance between Fragile Level {level_1} and {level_2}: -")