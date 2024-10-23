import pandas as pd

# Read the Excel file
file_path = './hierarchical_clusters.xlsx'
cluster_df = pd.read_excel(file_path)

# Calculate the count of each fg_level within each cluster
fg_level_distribution = cluster_df.groupby(['cluster', 'fg_level']).size().unstack(fill_value=0)

# Calculate the percentage distribution of fg_level in each cluster
fg_level_percentage = fg_level_distribution.div(fg_level_distribution.sum(axis=1), axis=0) * 100

# Display the percentage distribution
print("Percentage distribution of fg_level within each cluster using " + file_path)
print(fg_level_percentage)
