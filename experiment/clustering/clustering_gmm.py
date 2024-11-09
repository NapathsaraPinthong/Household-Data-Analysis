import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.mixture import GaussianMixture

def perform_gmm_clustering(file_path, k, output_excel_path, output_json_path):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Split 'value' into separate 'x' and 'y' columns
    df['value'] = df['value'].apply(ast.literal_eval)
    df[['x', 'y']] = pd.DataFrame(df['value'].tolist(), index=df.index)

    # Filter out only rows where node_target is 'household'
    household_df = df[df['node_target'] == 'household'].copy()

    # Get the relevant data
    node_ids = household_df['node_id'].tolist()
    node_embeddings_2d = household_df[['x', 'y']].values.tolist()  # Convert to list

    # Apply Gaussian Mixture Models (GMM)
    gmm = GaussianMixture(n_components=k, random_state=42)
    household_df['cluster'] = gmm.fit_predict(node_embeddings_2d)

    # Prepare the results for export
    cluster_df = household_df[['node_id', 'cluster']]
    cluster_df.to_excel(output_excel_path, index=False)
    print(f"Household's cluster label by GMM saved to '{output_excel_path}'")

    # Create the scatter plot using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scattergl(
        x=[point[0] for point in node_embeddings_2d],  # Convert list of lists to separate lists
        y=[point[1] for point in node_embeddings_2d],
        mode='markers',
        marker=dict(
            color=household_df['cluster'],  # Use cluster labels directly for color
            colorscale='Viridis',  # Use the same color scale as before
            opacity=0.8,
            colorbar=dict(title='Clusters')
        ),
        text=node_ids,
        hoverinfo='text'
    ))
    
    fig.update_layout(
        title={
            'text': "Gaussian Mixture Models (GMM) clustering",
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

    print(f"GMM plot data saved to '{output_json_path}'")

# Example usage:
k = 6  # Define the number of clusters
perform_gmm_clustering(
    file_path='../../main/result/node_embeddings_70_10.xlsx',
    k=k,
    output_excel_path='./result/gmm_clusters_k6.xlsx',  # Adjust file name based on components
    output_json_path='../../pages/clustering_plot/gmm_plot_k6.json'  # Adjust file name based on components
)