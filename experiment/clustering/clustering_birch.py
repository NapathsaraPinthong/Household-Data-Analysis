import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.cluster import Birch
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from time import perf_counter

def perform_birch_clustering(file_path, k, output_excel_path, output_json_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Split 'value' into a 128-dimensional array
    df['value'] = df['value'].apply(ast.literal_eval)
    node_embeddings = np.array(df['value'].tolist())  # Convert to NumPy array

    # Filter out only rows where node_target is 'household'
    household_df = df[df['node_target'] == 'household'].copy()

    # Get the relevant data
    node_ids = household_df['node_id'].tolist()
    household_embeddings = node_embeddings[household_df.index]  # Extract embeddings for 'household'

    # Normalize the embeddings using StandardScaler
    scaler = StandardScaler()
    household_embeddings_scaled = scaler.fit_transform(household_embeddings)

    t_start = perf_counter()

    # Apply BIRCH clustering
    birch = Birch(n_clusters=k, threshold=2.0)
    household_df['cluster'] = birch.fit_predict(household_embeddings_scaled)

    t_stop = perf_counter()
    print("Elapsed time during the clustering in seconds:", t_stop-t_start)

    # Prepare the results for export
    cluster_df = household_df[['node_id', 'cluster']]
    cluster_df.to_excel(output_excel_path, index=False)
    print(f"Household's cluster label by BIRCH saved to '{output_excel_path}'")

    # Use t-SNE for dimensionality reduction to 2D for visualization
    tsne = TSNE(n_components=2, random_state=42)
    node_embeddings_2d = tsne.fit_transform(household_embeddings_scaled)

    # Create the scatter plot using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=node_embeddings_2d[:, 0],  # Use first dimension
        y=node_embeddings_2d[:, 1],  # Use second dimension
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
            'text': f"BIRCH clustering (k={k})",
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

    print(f"BIRCH plot data saved to '{output_json_path}'")

# Example usage:
k = 5  # Define the number of clusters
perform_birch_clustering(
    file_path='../../main/result/node_embeddings_70_10_128.xlsx',
    k=k,
    output_excel_path='./result/birch_clusters_k5_128.xlsx',
    output_json_path='../../pages/clustering_plot/birch_plot_k5_128.json'
)