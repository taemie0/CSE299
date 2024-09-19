from langchain_community.embeddings.ollama import OllamaEmbeddings
import yaml

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

# from langchain_community.embeddings.bedrock import BedrockEmbeddings [online]
## (We need to use better embedding function)

def get_embedding_function():
    # embeddings = BedrockEmbeddings(
    #     credentials_profile_name="default", region_name="us-east-1"
    # )
    config = load_config()
    model_name = config.get("model_name", "gemma2:2b")  # Default to "gemma2:2b" if not set
    embeddings = OllamaEmbeddings(model=model_name)
    return embeddings