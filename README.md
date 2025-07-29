# llm-rag-citi


## How to Run
Step 1. Create an `.env` file in the root folder and follow the format in the `.env.example` file.

```.env
FLASK_SECRET_KEY=[PUT WHATEVER]


# LLM
LLM_URL=[YOUR LLM ENDPOINT/URI]
#5f86d2_LLM_URL=[YOUR HYDE LLM ENDPOINT/URI]


# MILVUS
MILVUS_URI_DEV=[YOUR MILVUS DEVELOPMENT URI]
MILVUS_USERNAME=[YOUR MILVUS USERNAME]
MILVUS_PASSWORD=[YOUR MILVUS PASSWORD]
MILVUS_DB_NAME=[YOUR MILVUS DATABASE]
MILVUS_URI_TEST=[YOUR MILVUS TEST URI]
MILVUS_URI_PROD=[YOUR MILVUS PRODUCTION URI]


# FILE DIRECTORY
DOCUMENT_DIR=[ABSOLUTE PATH OF WHERE THE FILES ARE LOCATED]
```

Step 2. You can use a python virtual environment and install all the dependencies needed:

```bash
pip install -r requierements.txt
```

Step 3. Run the `create_db.py` script in `script/` folder to create a database. Here's the command to do that:

```bash
python scripts/create_db.py [dev FOR DEVELOPMENT ENV prod FOR PROD ENV] [DATABASE NAME]
```

Step 4. Run the program using:

```bash
python runner.py
```
