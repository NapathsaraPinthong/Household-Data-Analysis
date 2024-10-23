import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ast
from sklearn.manifold import TSNE
import plotly.io as pio

pio.renderers.default = 'browser'
transform = TSNE  # PCA

# Read the Excel file
file_path = './result/node_embeddings_70_10.xlsx'
df = pd.read_excel(file_path)

# Split 'value' into separate 'x' and 'y' columns
df['value'] = df['value'].apply(ast.literal_eval)
df[['x', 'y']] = pd.DataFrame(df['value'].tolist(), index=df.index)

# Assuming columns: 'node_id', 'x', 'y', 'node_target'
node_ids = df['node_id'].tolist()
node_embeddings_2d = df[['x', 'y']].values
node_targets = df['node_target'].tolist()

# Assuming label_map, node_colours, and color_codes are already defined as in your original code
label_map = {l: i for i, l in enumerate(np.unique(node_targets))}
node_colours = [label_map[target] for target in node_targets]

# Create the scatter plot using Plotly
fig = go.Figure()

# Adding a trace for the node embeddings
fig.add_trace(go.Scattergl(
    x=node_embeddings_2d[:, 0],
    y=node_embeddings_2d[:, 1],
    mode='markers',
    marker=dict(
        color=node_colours,
        colorscale='Viridis',  # Use the same color scale as in Matplotlib
        opacity=0.3,
        colorbar=dict(title='Node Types')
    ),
    text=node_ids,  # Add tooltips using node_ids
    hoverinfo='text'
))

fig.update_traces(marker=dict(size=8, line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))

# Get the name of the transform class
transform_name = transform.__name__

# Set the title and layout
fig.update_layout(
    title=f"{transform_name} visualization of node embeddings",
    xaxis_title="X",
    yaxis_title="Y",
    width=800,
    height=600,
    legend=dict(
        x=1.02,  # Position the legend to the right of the plot
        y=-0.2,   # Align the legend vertically to the center
        xanchor='left',  # Anchor the legend box to the left
        yanchor='middle',  # Anchor the legend box to the middle
    ),
    coloraxis_colorbar=dict(
        title="Node Types",
        x=1.2  # Move the color bar further to the right to avoid overlap
    )
)

# Show the plot
fig.show()