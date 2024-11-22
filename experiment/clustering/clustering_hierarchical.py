import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.cluster import AgglomerativeClustering
from sklearn.manifold import TSNE
from joblib import Parallel, delayed
import json

os.environ["LOKY_MAX_CPU_COUNT"] = "8" 

def perform_hierarchical_clustering(file_path, k, output_excel_path, output_json_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Split 'value' into separate columns, assume it's a 128D embedding (e.g., in a string format)
    df['value'] = df['value'].apply(ast.literal_eval)

    # Filter out only rows where node_target is 'household'
    household_df = df[df['node_target'] == 'household'].copy()
    node_ids = household_df['node_id'].tolist()
    
    # Get the 128-dimensional embeddings for households
    household_embeddings = np.array(household_df['value'].tolist())

    # Apply t-SNE to reduce the dimensionality of the embeddings to 2D for visualization
    tsne = TSNE(n_components=2, random_state=42)
    node_embeddings_2d = tsne.fit_transform(household_embeddings)  # Reduce to 2D for plotting

    # Define function to perform clustering on a subset of data
    def cluster_subset(data_subset):
        hierarchical = AgglomerativeClustering(n_clusters=k)
        return hierarchical.fit_predict(data_subset)

    # Split the data into chunks for parallel processing
    chunk_size = 10000  # Adjust based on available memory and performance
    node_embeddings_chunks = [household_embeddings.tolist()[i:i + chunk_size] for i in range(0, len(household_embeddings), chunk_size)]

    # Perform clustering in parallel using all available cores
    cluster_results = Parallel(n_jobs=8)(delayed(cluster_subset)(chunk) for chunk in node_embeddings_chunks)

    # Combine the cluster results into one list
    clusters = np.concatenate(cluster_results)

    # Add the clustering results back to the dataframe
    household_df['cluster'] = clusters

    # Prepare the cluster DataFrame for output
    cluster_df = household_df[['node_id', 'cluster']]
    cluster_df.to_excel(output_excel_path, index=False)
    print(f"Household's cluster label by Hierarchical saved to '{output_excel_path}'")

    # Create the scatter plot using Plotly
    fig = go.Figure()
    unique_clusters = np.unique(clusters)
    label_map = {cluster: i for i, cluster in enumerate(unique_clusters)}
    cluster_colors = [label_map[cluster] for cluster in clusters]

    fig.add_trace(go.Scattergl(
        x=node_embeddings_2d[:, 0],  # Use the reduced 2D coordinates
        y=node_embeddings_2d[:, 1],
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
            'text': f"Hierarchical Clustering (k={k})",
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

    print(f"Hierarchical Clustering plot data saved to '{output_json_path}'")

# Example usage
if __name__ == "__main__":
    file_path = '../../main/result/node_embeddings_70_10_128.xlsx'
    k = 5
    output_excel_path = './result/hierarchical_clusters_k5_128.xlsx'  # Adjust file name based on k
    output_json_path = '../../pages/clustering_plot/hierarchical_plot_k5_128.json'  # Adjust file name based on k

    perform_hierarchical_clustering(file_path, k, output_excel_path, output_json_path)
