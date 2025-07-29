import sys
import os
from dotenv import load_dotenv

from pymilvus import connections, db, utility, Collection, CollectionSchema, FieldSchema, DataType


base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

if len(sys.argv) < 2:
    raise Exception("Please provide a environment name and a database name")

connections.connect(
    uri=os.getenv('MILVUS_URI_DEV' if sys.argv[1] == 'default' else 'MILVUS_URI_PROD'),
    user=os.getenv('MILVUS_USERNAME'),
    password=os.getenv('MILVUS_PASSWORD'),
)

db_name = sys.argv[2]

# create db
db.create_database(db_name=db_name)
db.using_database(db_name=db_name)

# create schema
id = FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=40, is_primary=True)
content = FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096)
vector = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024)
user_id = FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=40)
document_id = FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100)
document_name_field = FieldSchema(name="document_name", dtype=DataType.VARCHAR, max_length=500)
page_number_field = FieldSchema(name="page_number", dtype=DataType.INT64)

schema = CollectionSchema([
    id, content, vector, user_id, document_id, document_name_field, page_number_field
])

# create collections
public_collection = Collection(
    name="public",
    schema=schema
)

private_collection = Collection(
    name="private",
    schema=schema
)

# create index

vector_index = {
    "index_type": "IVF_FLAT",
    "metric_type": "COSINE",
    "params": {
        "nlist": 128
    }
}

# public collection indexes
public_collection.create_index(
    field_name="id"
)

public_collection.create_index(
    field_name="vector",
    index_params=vector_index
)

# private collection indexes
private_collection.create_index(
    field_name="id"
)

private_collection.create_index(
    field_name="vector",
    index_params=vector_index
)

# check everything
print(f"Loading collections...")
public_collection.load()
private_collection.load()

print(f"Checking indexes...")

if not public_collection.has_index(index_name="vector") or not private_collection.has_index(index_name="vector"):
    raise Exception("Public or private indexes are not loaded")

print(utility.list_collections())
print(f"Database has been created successfully")











