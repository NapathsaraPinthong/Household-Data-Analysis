import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from time import perf_counter

def perform_kmeans_clustering(file_path, k, output_excel_path, output_json_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Convert 'value' into a 128-dimensional vector
    df['value'] = df['value'].apply(ast.literal_eval)  # Ensure stringified lists are converted to Python list

    # Filter out only rows where node_target is 'household'
    household_df = df[df['node_target'] == 'household'].copy()
    node_ids = household_df['node_id'].tolist()

    # Get the 128-dimensional embeddings for households
    household_embeddings = np.array(household_df['value'].tolist())

    # Normalize the embeddings using StandardScaler
    scaler = StandardScaler()
    household_embeddings_scaled = scaler.fit_transform(household_embeddings)

    t_start = perf_counter()

    # Apply KMeans clustering on scaled data
    kmeans = KMeans(n_clusters=k, random_state=42)
    household_df['cluster'] = kmeans.fit_predict(household_embeddings_scaled)

    t_stop = perf_counter()
    print("Elapsed time during the clustering in seconds:", t_stop-t_start)

    # Prepare the results for export
    cluster_df = household_df[['node_id', 'cluster']]
    cluster_df.to_excel(output_excel_path, index=False)
    print(f"Household's cluster label by KMeans saved to '{output_excel_path}'")

    # Dimensionality reduction with TSNE for visualization
    tsne = TSNE(n_components=2, random_state=42)
    node_embeddings_2d = tsne.fit_transform(household_embeddings_scaled)

    # Create the plot
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=node_embeddings_2d[:, 0],
        y=node_embeddings_2d[:, 1],
        mode='markers',
        marker=dict(
            color=household_df['cluster'],  # Use cluster labels directly for color
            colorscale='Viridis',
            opacity=0.8,
            colorbar=dict(title='Clusters')
        ),
        text=node_ids,
        hoverinfo='text'
    ))

    fig.update_layout(
        title={
            'text': f"K-Means clustering (k={k})",
            'x': 0.5,
            'xanchor': 'center'
        },
        width=880,
        height=660,
        plot_bgcolor='#E5ECF6',
        paper_bgcolor='white'
    )

    # Convert all NumPy arrays to lists in plot_data
    plot_data = fig.to_plotly_json()
    for trace in plot_data['data']:
        trace['x'] = [float(value) for value in trace['x']]  # Convert to float
        trace['y'] = [float(value) for value in trace['y']]  # Convert to float
        if 'marker' in trace and isinstance(trace['marker'].get('color'), np.ndarray):
            trace['marker']['color'] = [float(value) for value in trace['marker']['color']]  # Convert to float
    plot_data['layout'] = json.loads(json.dumps(
        plot_data['layout'],
        default=lambda o: o.tolist() if isinstance(o, np.ndarray) else o
    ))

    # Save the plot's data and layout to a JSON file
    with open(output_json_path, 'w') as f:
        json.dump(plot_data, f)

    print(f"Plot data saved to '{output_json_path}'")

# Example usage:
k = 6  # Define the number of clusters
perform_kmeans_clustering(
    file_path='../../main/result/node_embeddings_70_10_128.xlsx',
    k=k,
    output_excel_path='./result/kmeans_clusters_k6_128.xlsx',  # Adjust file name based on k
    output_json_path='../../pages/clustering_plot/kmeans_plot_k6_128.json'  # Adjust file name based on k
)
