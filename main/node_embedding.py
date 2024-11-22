import pandas as pd
from sklearn.manifold import TSNE
import os
from stellargraph.data import UniformRandomMetaPathWalk
from gensim.models import Word2Vec
from MSO import MSO
from time import perf_counter
from tqdm import tqdm  # For progress tracking

os.environ["LOKY_MAX_CPU_COUNT"] = "8" 
transform = TSNE  # PCA

t1_start = perf_counter()
dataset = MSO()
g = dataset.load()
print(
    "Number of nodes {} and number of edges {} in graph.".format(
        g.number_of_nodes(), g.number_of_edges()
    )
)
t1_stop = perf_counter()
print("Elapsed time during loading dataset in seconds:", t1_stop-t1_start)

# ----- Parameter ----- #
walk_length = 10
window_size = 5

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

def run_random_walk_in_batches(nodes, batch_size):
    walks = []
    for i in tqdm(range(0, len(nodes), batch_size)):
        batch_nodes = nodes[i:i + batch_size]
        batch_walks = rw.run(
            nodes=batch_nodes,
            length=walk_length,
            n=1,
            metapaths=metapaths,
        )
        walks.extend(batch_walks)
    return walks


t2_start = perf_counter()
# Create the random walker
rw = UniformRandomMetaPathWalk(g)

batch_size = 10000
walks = run_random_walk_in_batches(list(g.nodes()), batch_size)

print("Number of random walks: {}".format(len(walks)))
t2_stop = perf_counter()
print("Elapsed time during the random walk in seconds:", t2_stop-t2_start)


t3_start = perf_counter()
model = Word2Vec(walks, vector_size=128, window=window_size, min_count=0, sg=1, workers=8, epochs=1)
t3_stop = perf_counter()
print("Elapsed time during the Word2Vec in seconds:", t3_stop-t3_start)

t4_start = perf_counter()
# Retrieve node embeddings and corresponding subjects
node_ids = model.wv.index_to_key  # list of node IDs
node_embeddings = (
    model.wv.vectors
)  
node_targets = [g.node_type(node_id) for node_id in node_ids]

t4_stop = perf_counter()
print("Elapsed time during the TSNE in seconds:", t4_stop-t4_start)


t5_start = perf_counter()
# Export a DataFrame of node embeddings to an Excel file
df = pd.DataFrame({
    'node_id': node_ids,
    'value': node_embeddings.tolist(),
    'node_target': node_targets
})

# note: node_embeddings_10_5 => walk_lenght = 10, window_size = 5
df.to_excel('./result/node_embeddings_l_s.xlsx', index=False)

t5_stop = perf_counter()
print("Elapsed time during exporting dataframe in seconds:", t5_stop-t5_start)
print("Elapsed time during the whole programe in seconds:", t5_stop-t1_start)
