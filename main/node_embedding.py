import pandas as pd
from sklearn.manifold import TSNE
import os
from stellargraph.data import UniformRandomMetaPathWalk
from gensim.models import Word2Vec
from MSO import MSO

os.environ["LOKY_MAX_CPU_COUNT"] = "4" 
transform = TSNE  # PCA

dataset = MSO()
g = dataset.load()
print(
    "Number of nodes {} and number of edges {} in graph.".format(
        g.number_of_nodes(), g.number_of_edges()
    )
)

walk_length = 50  # maximum length of a random walk to use throughout this notebook

# specify the metapath schemas as a list of lists of node types.
metapaths = [
    ["member", "household", "member"],
    ["household", "income", "household"],
    ["household", "house_solid", "household"],
    ["household", "member", "age", "member", "household"],
    ["household", "member", "disabled", "member", "household"],
    ["household", "member", "prop_health", "member", "household"],
    ["household", "member", "prop_family", "member", "household"]
]

# Create the random walker
rw = UniformRandomMetaPathWalk(g)

walks = rw.run(
    nodes=list(g.nodes()),  # root nodes
    length=walk_length,  # maximum length of a random walk
    n=1,  # number of random walks per root node
    metapaths=metapaths,  # the metapaths
)

print("Number of random walks: {}".format(len(walks)))

model = Word2Vec(walks, vector_size=128, window=5, min_count=0, sg=1, workers=2, epochs=1)

# Retrieve node embeddings and corresponding subjects
node_ids = model.wv.index_to_key  # list of node IDs
node_embeddings = (
    model.wv.vectors
)  # numpy.ndarray of size number of nodes times embeddings dimensionality
node_targets = [g.node_type(node_id) for node_id in node_ids]

trans = transform(n_components=2)
node_embeddings_2d = trans.fit_transform(node_embeddings)

# Export a DataFrame of node embeddings to an Excel file
df = pd.DataFrame({
    'node_id': node_ids,
    'value': node_embeddings_2d.tolist(),
    'node_target': node_targets
})

df.to_excel('./node_embeddings.xlsx', index=False)