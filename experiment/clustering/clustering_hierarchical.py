import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.cluster import AgglomerativeClustering
from joblib import Parallel, delayed
import json

os.environ["LOKY_MAX_CPU_COUNT"] = "8" 

def perform_hierarchical_clustering(file_path, k, output_excel_path, output_json_path):
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

    # Define function to perform clustering on a subset of data
    def cluster_subset(data_subset):
        hierarchical = AgglomerativeClustering(n_clusters=k)
        return hierarchical.fit_predict(data_subset)

    # Split the data into chunks for parallel processing
    chunk_size = 10000  # Adjust based on available memory and performance
    node_embeddings_chunks = [node_embeddings_2d[i:i + chunk_size] for i in range(0, len(node_embeddings_2d), chunk_size)]

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
    # fig = go.Figure()
    # unique_clusters = np.unique(clusters)
    # label_map = {cluster: i for i, cluster in enumerate(unique_clusters)}
    # cluster_colors = [label_map[cluster] for cluster in clusters]

    # fig.add_trace(go.Scattergl(
    #     x=[point[0] for point in node_embeddings_2d],
    #     y=[point[1] for point in node_embeddings_2d],
    #     mode='markers',
    #     marker=dict(
    #         color=cluster_colors,
    #         colorscale='Viridis',
    #         opacity=0.8,
    #         colorbar=dict(title='Clusters')
    #     ),
    #     text=node_ids,
    #     hoverinfo='text'
    # ))

    # fig.update_layout(
    #     title={
    #         'text': "Hierarchical Clustering",
    #         'x': 0.5,
    #         'xanchor': 'center'
    #     },
    #     xaxis_title="X",
    #     yaxis_title="Y",
    #     width=880,
    #     height=660,
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     paper_bgcolor='rgba(0,0,0,0.05)'
    # )

    # # Save the plot's data and layout to a JSON file
    # plot_data = {
    #     'data': fig.to_plotly_json()['data'],
    #     'layout': fig.to_plotly_json()['layout']
    # }

    # # Ensure the data and layout are serializable
    # for trace in plot_data['data']:
    #     trace['x'] = list(trace['x'])  # Convert to list
    #     trace['y'] = list(trace['y'])  # Convert to list

    # with open(output_json_path, 'w') as f:
    #     json.dump(plot_data, f)

    # print(f"Hierarchical Clustering plot data saved to '{output_json_path}'")

# Example usage
if __name__ == "__main__":
    file_path='../../main/result/node_embeddings_70_10.xlsx'
    k = 3
    output_excel_path = './result/hierarchical_clusters_k3.xlsx' # Adjust file name based on k
    output_json_path = '../../pages/clustering_plot/hierarchical_plot_k3.json' # Adjust file name based on k

    perform_hierarchical_clustering(file_path, k, output_excel_path, output_json_path)