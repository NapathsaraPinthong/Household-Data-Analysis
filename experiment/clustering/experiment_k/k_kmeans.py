import pandas as pd
import ast
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from time import perf_counter

# Load the data
file_path = '../../../main/result/node_embeddings_70_10.xlsx'
df = pd.read_excel(file_path)

# Parse the 'value' column into 128-dimensional embeddings
df['value'] = df['value'].apply(ast.literal_eval)
dimension_columns = [f'dim_{i}' for i in range(128)]
new_columns = pd.DataFrame(df['value'].tolist(), columns=dimension_columns)
df = pd.concat([df, new_columns], axis=1)
df = df.drop(columns=['value'])

# Filter the household nodes, excluding specific IDs
household_df = df[df['node_target'] == 'household']

# Extract 128-dimensional node embeddings for households
node_embeddings = household_df[dimension_columns].values

# Normalize the data using StandardScaler
scaler = StandardScaler()
node_embeddings_scaled = scaler.fit_transform(node_embeddings)

# Silhouette Analysis for K = 2 to 10
k_values = range(2, 11)  # Adjusted K range
silhouette_scores = []

for k in k_values:
    t_start = perf_counter()

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(node_embeddings_scaled)
    score = silhouette_score(node_embeddings_scaled, labels)
    silhouette_scores.append(score)

    t_stop = perf_counter()
    elapsed_time = t_stop - t_start

    print(f"K={k}, Silhouette Score={score:.4f}, Time Taken={elapsed_time:.2f} seconds")

# Plot Silhouette Scores
plt.figure(figsize=(10, 5))
plt.plot(k_values, silhouette_scores, marker='o')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Analysis for Optimal K')

# Save the plot
plot_path = './silhouette_K-means.png'
plt.savefig(plot_path)
plt.show()

print(f"Silhouette plot saved at {plot_path}")
