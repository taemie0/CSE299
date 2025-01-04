from transformers import AutoModel
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
import yaml

def load_config():
    """Load the configuration from the config.yaml file."""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_embedding_model(model_name, model_kwargs, path):
    """Initialize HuggingFaceEmbeddings with the given parameters."""
    encode_kwargs = {'normalize_embeddings': True}
    hf = HuggingFaceEmbeddings(
        model_name=model_name, 
        model_kwargs=model_kwargs, 
        encode_kwargs=encode_kwargs, 
        cache_folder=path)
    return hf

def get_embedding_function():
    """Determine and return the appropriate embedding function."""
    config = load_config()
    embedding_model_name = config.get('embedding_model_name')
    embedding_model_save_path = config.get('embedding_model_save_path')
    if embedding_model_name and embedding_model_save_path:
        model_kwargs = {'device': 'cpu', 'trust_remote_code': True}
        embeddings = get_embedding_model(
            model_name=embedding_model_name, 
            model_kwargs=model_kwargs, 
            path=embedding_model_save_path)
    else:
        model_name = config.get('model_name', 'gemma2:2b')
        embeddings = OllamaEmbeddings(model=model_name)
    return embeddings