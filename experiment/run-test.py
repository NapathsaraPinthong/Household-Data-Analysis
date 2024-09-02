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
