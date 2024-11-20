import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.cluster import KMeans

def perform_kmeans_clustering(file_path, k, output_excel_path, output_json_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Split 'value' into separate 'x' and 'y' columns
    df['value'] = df['value'].apply(ast.literal_eval)
    df[['x', 'y']] = pd.DataFrame(df['value'].tolist(), index=df.index)

    # Filter out only rows where node_target is 'household'
    household_df = df[df['node_target'] == 'household'].copy()

    # Get the relevant data
    node_ids = household_df['node_id'].tolist()
    node_embeddings_2d = household_df[['x', 'y']].values

    # Apply KMeans clustering to the filtered household data
    kmeans = KMeans(n_clusters=k, random_state=42)
    household_df['cluster'] = kmeans.fit_predict(node_embeddings_2d)

    # Prepare the results for export
    cluster_df = household_df[['node_id', 'cluster']]
    cluster_df.to_excel(output_excel_path, index=False)
    print(f"Household's cluster label by KMeans saved to '{output_excel_path}'")

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
        xaxis_title="X",
        yaxis_title="Y",
        width=880,
        height=660,
        plot_bgcolor='#E5ECF6',
        paper_bgcolor='white'
    )

    # Convert all NumPy arrays to lists in plot_data
    plot_data = fig.to_plotly_json()
    for trace in plot_data['data']:
        trace['x'] = list(trace['x'])
        trace['y'] = list(trace['y'])
        if 'marker' in trace and isinstance(trace['marker'].get('color'), np.ndarray):
            trace['marker']['color'] = trace['marker']['color'].tolist()
    plot_data['layout'] = json.loads(json.dumps(plot_data['layout'], default=lambda o: o.tolist() if isinstance(o, np.ndarray) else o))

    # Save the plot's data and layout to a JSON file
    with open(output_json_path, 'w') as f:
        json.dump(plot_data, f)

    print(f"Plot data saved to '{output_json_path}'")

# Example usage:
k = 20  # Define the number of clusters
perform_kmeans_clustering(
    file_path='../../main/result/node_embeddings_70_10.xlsx',
    k=k,
    output_excel_path='./result/kmeans_clusters_k20.xlsx',  # Adjust file name based on k
    output_json_path='../../pages/clustering_plot/kmeans_plot_k20.json'  # Adjust file name based on k
)
