import argparse
import yaml
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain.memory import ConversationBufferMemory 

from get_embeddings import get_embedding_function

CHROMA_PATH = "db"

PROMPT_TEMPLATE = """
Answer the question based on the following context:

{context}

---
If context is not found, search in the {history} for the answer to the question.

---

Now, answer the question based on the above context: {question}

---

You are a language model that understands context and can provide informative answers. Please provide a concise and accurate response.
"""


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

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
    query_with_memory(query_text, memory, session_name)

def query_with_memory(query_text: str, memory: ConversationBufferMemory, session_name=None):
    config = load_config()
    model_name = config.get("model_name", "gemma2:2b")  

    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    conversation_history = memory.load_memory_variables({})
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text, history=conversation_history['history'])

    # Generate the bot response
    bot_response = Ollama(model=model_name).invoke(prompt)  

    # Ensure output is not None or an empty string
    output = bot_response if bot_response else ""

    # Save the new conversation turn in memory
    if memory:
        memory.save_context({"input": query_text}, {"output": output})

    # Collect sources from results
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {bot_response}\nSources: {sources}"
    print(formatted_response)
    return bot_response



if __name__ == "__main__":
    main()
