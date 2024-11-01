import pandas as pd

# Load the data
node_embeddings = pd.read_excel('../main/result/node_embeddings_70_10.xlsx')
hh_fg_level = pd.read_excel('../data/dataset/edge/hh-fg_level.xlsx', header=None, names=['id', 'fg_level'])

# Filter rows where node_target == 'household'
household_nodes = node_embeddings[node_embeddings['node_target'] == 'household'].copy()

# Split 'value' into 'x' and 'y' coordinates
household_nodes[['x', 'y']] = household_nodes['value'].str.strip('[]').str.split(',', expand=True).astype(float)

# Remove 'hh' prefix from 'node_id' for matching and convert to integer
household_nodes['id'] = household_nodes['node_id'].str.replace('hh', '').astype(int)

# Merge with hh_fg_level on 'id'
merged_data = pd.merge(household_nodes, hh_fg_level, on='id', how='inner')

# Select the required columns
final_data = merged_data[['node_id', 'x', 'y', 'fg_level']]

# Save to a new Excel file
final_data.to_excel('./preprocessed_data.xlsx', index=False)