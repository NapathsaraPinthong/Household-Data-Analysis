import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.cluster import DBSCAN
import json

# Read the Excel file
file_path = '../result/node_embeddings_70_10.xlsx'
df = pd.read_excel(file_path)

fg_level_file_path = '../../data/dataset/edge/hh-fg_level.xlsx'
fg_level_df = pd.read_excel(fg_level_file_path, header=None, names=["hh", "fg_level"])
fg_level_df['node_id'] = 'hh' + fg_level_df['hh'].astype(str)

# Split 'value' into separate 'x' and 'y' columns
df['value'] = df['value'].apply(ast.literal_eval)
df[['x', 'y']] = pd.DataFrame(df['value'].tolist(), index=df.index)

# Filter out only rows where node_target is 'household' (filter out fragile level -1)
household_df = df[(df['node_target'] == 'household') & 
                  (~df['node_id'].isin(['hh5845890286', 'hh5899737356']))]

# Get the relevant data
node_ids = household_df['node_id'].tolist()
node_embeddings_2d = household_df[['x', 'y']].values.tolist()  # Convert to list

# Apply DBSCAN clustering to the filtered household data
dbscan = DBSCAN(eps=0.5, min_samples=3)
household_df['cluster'] = dbscan.fit_predict(node_embeddings_2d)

# Define colors for clusters
clusters = household_df['cluster'].tolist()
unique_clusters = np.unique(clusters)
label_map = {cluster: i for i, cluster in enumerate(unique_clusters)}
cluster_colors = [label_map[cluster] for cluster in clusters]

cluster_df = household_df[['node_id', 'cluster']]
cluster_df = pd.merge(cluster_df, fg_level_df.drop(columns=['hh']), on='node_id', how='inner')
cluster_df.to_excel('./dbscan_clusters.xlsx',index=False)
print("Household's cluster label by DBSCAN saved to './dbscan_clusters.xlsx'")

# Create the scatter plot using Plotly
fig = go.Figure()

fig.add_trace(go.Scattergl(
    x=[point[0] for point in node_embeddings_2d],  # Convert list of lists to separate lists
    y=[point[1] for point in node_embeddings_2d],
    mode='markers',
    marker=dict(
        color=cluster_colors,
        colorscale='Viridis',
        opacity=0.8,
        colorbar=dict(title='Clusters')
    ),
    text=node_ids,
    hoverinfo='text'
))

fig.update_layout(
    title={
        'text': "DBSCAN clustering",
        'x': 0.5,
        'xanchor': 'center'
    },
    xaxis_title="X",
    yaxis_title="Y",
    width=880,
    height=660,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0.05)'
)

# Save the plot's data and layout to a Python file
plot_data = {
    'data': fig.to_plotly_json()['data'],
    'layout': fig.to_plotly_json()['layout']
}

# Ensure the data and layout are serializable
for trace in plot_data['data']:
    trace['x'] = list(trace['x'])  # Convert to list
    trace['y'] = list(trace['y'])  # Convert to list

with open('../../pages/clustering_plot/dbscan_plot.json', 'w') as f:
    json.dump(plot_data, f)

print("DBSCAN plot data saved to '../../pages/clustering_plot/dbscan_plot.json'")