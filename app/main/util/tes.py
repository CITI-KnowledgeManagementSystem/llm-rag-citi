from pymilvus import MilvusClient, connections
from sentence_transformers import SentenceTransformer # or your preferred embedding model

# Connect to Milvus
connections.connect(host='localhost', port='19530')

# Initialize Milvus client
client = MilvusClient(uri="http://localhost:19530")

# Your query sentence
query_sentence = "chou"

# Load your embedding model (example using Sentence-BERT)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embedding for the query
query_embedding = model.encode(query_sentence).tolist()

# Search parameters
search_params = {
    "metric_type": "L2",  # or "IP" for inner product
    "params": {"nprobe": 10}
}

# Perform the search
results = client.search(
    collection_name="public",  # your collection name
    data=[query_embedding],
    # anns_field="embedding_field",  # your vector field name
    param=search_params,
    limit=5,  # number of results to return
    # output_fields=["sentence_field"]  # the field containing the original sentences
)

# Print results
for hits in results:
    for hit in hits:
        print(f"Score: {hit.score}, Sentence: {hit.entity.get('sentence_field')}")