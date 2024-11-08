import json
import numpy as np
import pandas as pd
import ast
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

file_path = '../main/result/node_embeddings_70_10.xlsx'
df = pd.read_excel(file_path)

df['value'] = df['value'].apply(ast.literal_eval)
df[['x', 'y']] = pd.DataFrame(df['value'].tolist(), index=df.index)
household_df = df[(df['node_target'] == 'household') & 
                (~df['node_id'].isin(['hh5845890286', 'hh5899737356']))]
node_embeddings_2d = household_df[['x', 'y']].values

intra_distances = []
inter_distances = []
silhouette_scores = []
wss = []
k_values = range(2, 21) # Experiment with K from 2 to 20 (silhouette analysis requires at least 2 clusters)

########intra/inter distance##########
def calculate_distances(node_embeddings, k):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(node_embeddings)
    centroids = kmeans.cluster_centers_

    # Calculate intra-cluster distance
    intra_dist = np.mean([
        np.mean(cdist(node_embeddings[labels == i], [centroids[i]], 'euclidean')) 
        for i in range(k)
    ])

    # Calculate inter-cluster distance if k > 1
    if k > 1:
        inter_dist = np.mean(cdist(centroids, centroids, 'euclidean'))
    else:
        inter_dist = 0  # Only one cluster, so no inter-cluster distance
    
    return intra_dist, inter_dist

print("K\tIntra-cluster Distance\tInter-cluster Distance")
for k in k_values:
    intra, inter = calculate_distances(node_embeddings_2d, k)
    intra_distances.append(intra)
    inter_distances.append(inter)
    print(f"{k}\t{intra:.4f}\t\t\t{inter:.4f}")


########silhouette analysis##########
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(node_embeddings_2d)
    score = silhouette_score(node_embeddings_2d, labels)
    silhouette_scores.append(score)

# Plot silhouette scores
plt.figure(figsize=(10, 5))
plt.plot(k_values, silhouette_scores, marker='o')
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Analysis for Optimal K')
plt.show()


##########elbow method###########
# Calculate WSS (inertia) for each K
for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(node_embeddings_2d)
    wss.append(kmeans.inertia_)  # Inertia is the WSS for the given K

# Plot the Elbow Curve
plt.figure(figsize=(10, 5))
plt.plot(k_values, wss, marker='o')
plt.xticks(range(1, 21))
plt.xlabel('Number of Clusters (K)')
plt.ylabel('Within-Cluster Sum of Squares (WSS)')
plt.title('Elbow Method for Optimal K')
plt.show()