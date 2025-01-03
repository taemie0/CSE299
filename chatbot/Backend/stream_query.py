import argparse
import yaml
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms.ollama import Ollama
from langchain.memory import ConversationBufferMemory 
from langchain_community.chat_message_histories import ChatMessageHistory
from get_embeddings import get_embedding_function

CHROMA_PATH = "E:/CSE299/chatbot/vectorDB"

from Prompt import NEW_COT_PROMPT_WITH_HISTORY 

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def query_rag_streaming(query_text: str, memory: ConversationBufferMemory, session_name=None):
    """Run the retrieval chain with memory and stream the response."""
    config = load_config()
    model_name = config.get('model_name', 'gemma2:2b')

    # Initialize the embedding function and vector store
    embedding_function = get_embedding_function()
    vector_db_path = config.get('embedding_vector_db_path', CHROMA_PATH)

    vectorstore = Chroma(
        persist_directory=vector_db_path,
        embedding_function=embedding_function
    )
    context = vectorstore.similarity_search_with_score(query_text, k=6)

    # Print out the retrieved context for verification
    # print("Retrieved Context:")
    # for doc in context:
    #     print(doc)

    # Load conversation history from memory
    conversation_history = memory.load_memory_variables({}).get("history", "")

    print("conversation_history: ", conversation_history)
    print("query_text: ", query_text)
    print("context: ", context)

    # Prepare the inputs for the prompt template
    inputs = {
        "context": context,
        "question": query_text,
        "history": conversation_history
    }

    # Create the prompt template and the model
    prompt_template = ChatPromptTemplate.from_template(NEW_COT_PROMPT_WITH_HISTORY)
    model = Ollama(model=model_name)

    # Build the retrieval chain using RunnablePassthrough
    retrieval_chain = (
        RunnablePassthrough()  # Pass the inputs directly through
        | prompt_template  # Format the prompt with the inputs
        | model  # Invoke the model with the formatted prompt
        | StrOutputParser()  # Parse the model's output into a string
    )

    # Stream response chunks
    try:
        for chunk in retrieval_chain.stream(inputs):
            # print(f"Chunk: {chunk}")
            print(f"Chunk: {chunk}")    
            yield chunk
    except Exception as e:
        yield f"Error occurred while streaming response: {e}"



def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    parser.add_argument("--chat_history", type=str, help="The chat history to pass to the model.")
    parser.add_argument("--session_name", type=str, help="The session name.")
    
    args = parser.parse_args()
    
    # Prepare the input values
    query_text = args.query_text
    memory = eval(args.chat_history) if args.chat_history else ConversationBufferMemory()  # Initialize memory if not provided
    session_name = args.session_name
    
    # Call the main query function
    # query_rag(query_text, memory, session_name)

if __name__ == "__main__":
    main()
