import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(base_dir, '.env'))


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    DEBUG = False


class DevelopmentConfig(Config):
    # using milvus database
    DEBUG = True
    MILVUS_URI = os.getenv('MILVUS_URI_DEV')


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MILVUS_URI = os.getenv('MILVUS_URI_TEST')


class ProductionConfig(Config):
    DEBUG = False
    MILVUS_URI = os.getenv('MILVUS_URI_PROD')


config_by_name = dict(
    dev = DevelopmentConfig,
    test=TestingConfig,
    prod = ProductionConfig
)


key = Config.SECRET_KEY