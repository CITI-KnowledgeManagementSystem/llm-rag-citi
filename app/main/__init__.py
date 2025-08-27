from flask import Flask
from flask_cors import CORS
from pymilvus import connections
from llama_index.core import Settings
# from langchain_openai import ChatOpenAI
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.langchain import LangchainEmbedding
from .util.embedding import CustomAPIEmbeddings
from llama_index.agent.openai import OpenAIAgent
# from llama_index.core.agent.workflow import FunctionAgent
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
import threading

from .config import config_by_name
from .constant.document import EMBEDDING_MODEL
from .constant.llm import TEMPERATURE, MODEL, N_HYDE_INSTANCE, HYDE_LLM_URL, LLM_URL, MAX_TOKENS

# embedding_model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True, device='cuda' if torch.cuda.is_available() else 'cpu')

EMBEDDING_MODEL = "Alibaba-NLP/gte-large-en-v1.5"

EMBEDDING_API_URL = "http://140.118.101.181:1234/embed"

langchain_embedding_model = CustomAPIEmbeddings(api_url=EMBEDDING_API_URL)

llama_index_embedding_model = LangchainEmbedding(langchain_embedding_model)


# Settings.embed_model = llama_index_embedding_model
# Settings.llm = generation_llm

# embedding_model = SentenceTransformer(
#     EMBEDDING_MODEL,
#     device= "cuda",
#     trust_remote_code=True,
# )

# hyde_llm_old = ChatOpenAI(
#     openai_api_base = HYDE_LLM_URL,
#     model_name = MODEL,
#     n=N_HYDE_INSTANCE,
#     temperature=TEMPERATURE,
#     openai_api_key="None",
# )

hyde_llm = OpenAI(
    api_base = HYDE_LLM_URL,
    model = MODEL,
    # n=N_HYDE_INSTANCE,
    temperature=TEMPERATURE,
    api_key="None",
)

# hyde_llm = Ollama(
#     base_url = HYDE_LLM_URL,
#     model = MODEL,
#     # n=N_HYDE_INSTANCE,
#     # temperature=TEMPERATURE,
#     # api_key="None",
# )

semaphore = threading.Semaphore(2)

# generation_llm = ChatOpenAI(
#     openai_api_base = LLM_URL,
#     model_name=MODEL,
#     temperature=TEMPERATURE,
#     openai_api_key="test",
#     max_tokens=MAX_TOKENS,
# )

# gaudi_generation_llm = ChatOpenAI(
#     openai_api_base = LLM_URL,
#     model_name=MODEL,
#     temperature=TEMPERATURE,
#     openai_api_key="test",
#     max_tokens=MAX_TOKENS,
# )

generation_llm = OpenAI(
    api_base = LLM_URL,
    model=MODEL,
    temperature=TEMPERATURE,
    api_key="test",
    max_tokens=MAX_TOKENS,
)

ddg_spec = DuckDuckGoSearchToolSpec()

# Kita bikin agent-nya.
# Dia punya otak (llm) dan tangan (tools) buat kerja.
# verbose=True biar kita bisa liat di console agent-nya lagi ngapain, bagus buat debugging.
agent = OpenAIAgent.from_tools(
    tools=ddg_spec.to_tool_list(),
    llm=generation_llm,
    verbose=True
)

# generation_llm = Ollama(
#     base_url = LLM_URL,
#     model=MODEL,
#     temperature=TEMPERATURE,
#     # api_key="test",
#     # max_tokens=MAX_TOKENS,
# )

gaudi_generation_llm = OpenAI(
    api_base = LLM_URL,
    model=MODEL,
    temperature=TEMPERATURE,
    api_key="test",
    max_tokens=MAX_TOKENS,
)

# gaudi_generation_llm = Ollama(
#     base_url = LLM_URL,
#     model=MODEL,
#     temperature=TEMPERATURE,
#     # api_key="test",
#     # max_tokens=MAX_TOKENS,
# )

def create_app(config_name:str):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    CORS(app=app)


    # connect to milvus
    connections.connect(
        uri=config_by_name[config_name].MILVUS_URI,
        user=config_by_name[config_name].MILVUS_USER,
        password=config_by_name[config_name].MILVUS_PASSWORD,
        db_name=config_by_name[config_name].MILVUS_DB_NAME
    )

    # register blueprints
    # routes need to be imported inside to avoid conflict
    from .route import document_route, llm_route, tts_route
    app.register_blueprint(document_route.blueprint)
    app.register_blueprint(llm_route.blueprint)
    app.register_blueprint(tts_route.blueprint)

    print(f"The app is running in {config_name} environment")

    return app
