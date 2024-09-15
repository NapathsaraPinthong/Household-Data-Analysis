import pandas as pd
from fragile_level_utils import *
from hh_mb_utils import *

file_path = "../main/result/node_embeddings_50_25.xlsx"
column_names = ["node_id", "value", "node_target"]
embedding_df = pd.read_excel(file_path, header=0, names=column_names)

sampled_hh_ids = load_sampled_households('./static/sampled_households.csv')
embedding_dict = create_embedding_dict(embedding_df)
hh_member_dict = load_hh_member_dict('./static/hh_member_dict.pkl')

# -------- Usage -------- #
# distance_lv_minus_1 = calculate_distance_in_fragile_level(-1, embedding_df)
# distance_lv0 = calculate_distance_in_fragile_level(0, embedding_df)
# distance_lv1 = calculate_distance_in_fragile_level(1, embedding_df)
# distance_lv2 = calculate_distance_in_fragile_level(2, embedding_df)
# distance_lv3 = calculate_distance_in_fragile_level(3, embedding_df)

# print(f"Level -1: {distance_lv_minus_1}")
# print(f"Level 0: {distance_lv0}")
# print(f"Level 1: {distance_lv1}")
# print(f"Level 2: {distance_lv2}")
# print(f"Level 3: {distance_lv3}")

overall_avg_distance = calculate_distance_for_households(sampled_hh_ids, embedding_dict, hh_member_dict)
print(f"Overall Average Distance: {overall_avg_distance}")