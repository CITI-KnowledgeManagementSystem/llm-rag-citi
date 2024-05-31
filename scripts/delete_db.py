import sys
import os
from dotenv import load_dotenv

from pymilvus import connections, db, utility


base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

if len(sys.argv) < 2:
    raise Exception("Please provide a database name")

connections.connect(
    uri=os.getenv('MILVUS_URI_DEV' if sys.argv[1] == 'dev' else 'MILVUS_URI_PROD'),
    user=os.getenv('MILVUS_USERNAME'),
    password=os.getenv('MILVUS_PASSWORD'),
)

db_name = sys.argv[2]

db.using_database(db_name=db_name)

print(f"Deleting '{db_name}' database...")

# delete the collections
collections = utility.list_collections()

for collection in collections:
    utility.drop_collection(collection)

db.drop_database(db_name=db_name)

print(f"Database has been deleted successfully")
print(db.list_database())
