import argparse
import yaml
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms.ollama import Ollama
from langchain_community.chat_message_histories import ChatMessageHistory
from get_embeddings import get_embedding_function
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# CHROMA_PATH = "E:/CSE299/chatbot/vectorDB"

from Prompt import PROMPT_HISTORY_SUMMARY, COT_PROMPT_WITH_HISTORY2, COT_PROMPT_WITH_HISTORY3


def determine_query_type(query_text: str) -> str:
    """
    Determine whether the query is conceptual or numerical with enhanced detection.

    Args:
    - query_text (str): The input query.

    Returns:
    - str: Either "conceptual" or "numerical".
    """
    # Lowercase the query to simplify matching
    query_text = query_text.lower()

    # Define sets of keywords related to numerical and conceptual queries
    numerical_keywords = {
        "calculate", "solve", "find", "value", "speed", "distance", "mass", "time", "acceleration", 
        "force", "temperature", "velocity", "pressure", "area", "volume", "rate", "amount", "percent",
        "sum", "difference", "product", "quotient", "integrate", "derivative", "slope", "equation", "formula"
    }

    conceptual_keywords = {
        "define", "explain", "describe", "interpret", "what", "why", "how", "discuss", "elaborate", 
        "purpose", "meaning", "principle", "theory", "cause", "concept", "idea", "overview", "background",
        "distinguish", "compare", "contrast", "impact", "importance", "role", "analysis", "perspective", "application"
    }

    # Check if any numerical-related keywords exist in the query
    if any(keyword in query_text for keyword in numerical_keywords):
        # Further check for presence of numbers or mathematical symbols
        if re.search(r'\d+(\.\d+)?|\+|\-|\*|\/|\=|\^|\%|!', query_text):
            return "numerical"
    
    # Check if any conceptual-related keywords exist in the query
    elif any(keyword in query_text for keyword in conceptual_keywords):
        return "conceptual"
    
    # Check for specific mathematical expressions or patterns that suggest a numerical query
    mathematical_patterns = [
        r"\d+\s?[+-/*=^%]\s?\d+",   # simple math operations like 3 + 4 or 2*5
        r"\d+\s?[\.,]\s?\d+",         # decimal numbers like 3.14 or 5,000
        r"(\d+\s?[-+]?\s?[\d\.,]+)",  # range or multiple numbers like 1-2 or 10,000-20,000
        r"\b(\d+)\s?(\w+)\b"          # units like 5 m, 20 kg
    ]
    if any(re.search(pattern, query_text) for pattern in mathematical_patterns):
        return "numerical"
    
    # If no clear numerical query found, return conceptual
    return "conceptual"


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)



def query_rag_streaming(query_text: str, conversation_history: list, summary: str):
    """Run the retrieval chain and stream the response in chunks with dynamic temperature adjustment."""
    config = load_config()
    model_name = config.get('model_name')

    # Initialize the embedding function and vector store
    embedding_function = get_embedding_function()
    vector_db_path = config.get('embedding_vector_db_path')

    vectorstore = Chroma(
        persist_directory=vector_db_path,
        embedding_function=embedding_function
    )
    context = vectorstore.similarity_search_with_score(query_text, k=6)

    # Get the last four messages to include in the context
    last_four_messages = conversation_history[-4:] if len(conversation_history) >= 4 else conversation_history

    # Determine the query type and set the temperature
    query_type = determine_query_type(query_text)
    temperature = 0.1 if query_type == "numerical" else 0.7
    
    print(f"Query type: {query_type}, Temperature: {temperature}")

    # Prepare the inputs with context, query, and history
    inputs = {
        "summary_of_the_conversation": summary,
        "context": context,
        "question": query_text,
        "history": last_four_messages
    }
    
    print(inputs)
    # Create the prompt template and the model
    prompt_template = ChatPromptTemplate.from_template(PROMPT_HISTORY_SUMMARY)
    model = Ollama(model=model_name, temperature=temperature)  # Pass the dynamic temperature

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
            yield chunk
    except Exception as e:
        yield f"Error occurred while streaming response: {e}"



