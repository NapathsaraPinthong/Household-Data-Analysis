import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.mixture import GaussianMixture
from sklearn.manifold import TSNE
import json

# Read the Excel file
file_path = './node_embeddings.xlsx'
df = pd.read_excel(file_path)

# Split 'value' into separate 'x' and 'y' columns
df['value'] = df['value'].apply(ast.literal_eval)
df[['x', 'y']] = pd.DataFrame(df['value'].tolist(), index=df.index)

# Filter out only rows where node_target is 'household'
household_df = df[df['node_target'] == 'household']

# Get the relevant data
node_ids = household_df['node_id'].tolist()
node_embeddings_2d = household_df[['x', 'y']].values.tolist()  # Convert to list

# Apply Gaussian Mixture Models (GMM)
gmm = GaussianMixture(n_components=5, random_state=42)  # You can adjust n_components
household_df['gmm_cluster'] = gmm.fit_predict(node_embeddings_2d)

# Define colors for clusters
clusters = household_df['gmm_cluster'].tolist()
unique_clusters = np.unique(clusters)
label_map = {cluster: i for i, cluster in enumerate(unique_clusters)}
cluster_colors = [label_map[cluster] for cluster in clusters]

# Create the scatter plot using Plotly
fig = go.Figure()

fig.add_trace(go.Scattergl(
    x=[point[0] for point in node_embeddings_2d],  # Convert list of lists to separate lists
    y=[point[1] for point in node_embeddings_2d],
    mode='markers',
    marker=dict(
        color=cluster_colors,
        colorscale='Viridis',  # Use the same color scale as before
        opacity=0.8,
        colorbar=dict(title='Clusters')
    ),
    text=node_ids,
    hoverinfo='text'
))

fig.update_traces(marker=dict(size=8, line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))

fig.update_layout(
    title="Gaussian Mixture Models (GMM) Clustering on TSNE Visualization of 'Household' Node Embeddings",
    xaxis_title="X",
    yaxis_title="Y",
    width=800,
    height=600
)

# Save the plot's data and layout to a JSON file
plot_data = {
    'data': fig.to_plotly_json()['data'],
    'layout': fig.to_plotly_json()['layout']
}

# Ensure the data and layout are serializable
for trace in plot_data['data']:
    trace['x'] = list(trace['x'])  # Convert to list
    trace['y'] = list(trace['y'])  # Convert to list

with open('../pages/gmm_plot.json', 'w') as f:
    json.dump(plot_data, f)

print("GMM plot data saved to '../pages/gmm_plot.json'")