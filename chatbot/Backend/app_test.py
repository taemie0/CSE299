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
    """Run the retrieval chain and stream the response in chunks with advanced follow-up handling."""

    config = load_config()
    model_name = config.get('model_name')

    # Initialize the embedding function and vector store for book knowledge
    embedding_function = get_embedding_function()
    vector_db_path = config.get('embedding_vector_db_path')

    vectorstore = Chroma(
        persist_directory=vector_db_path,
        embedding_function=embedding_function
    )

    context = vectorstore.similarity_search_with_score(query_text, k=6)

    # # Step 1: Retrieve relevant book information based on the query
    # k = 6 if len(query_text.split()) < 10 else 10  # More complex queries retrieve more context
    # book_context = vectorstore.similarity_search_with_score(query_text, k=k)

    # print(f"Book Context:{book_context}")
    # # Extract just the document (text) from the book context tuples
    # book_context_text = [doc[0] for doc in book_context]  # Assuming each item is a tuple (text, score)

    # print(f"Book Context Text:{book_context_text}")
    # Step 2: Retrieve the last few messages from chat history to keep context
    last_four_messages = conversation_history[-4:] if len(conversation_history) >= 4 else conversation_history
    
    print(f"Last Four Messages:{last_four_messages}")

    # Step 3: Use Semantic Embeddings to dynamically rank the conversation history
    conversation_embeddings = [embedding_function.embed_query(message) for message in last_four_messages]
    query_embedding = embedding_function.embed_query(query_text)

    # Calculate similarity between the query and each previous message
    similarities = [cosine_similarity([query_embedding], [embedding])[0][0] for embedding in conversation_embeddings]

    # Select the top N most relevant previous messages based on similarity
    sorted_indices = np.argsort(similarities)[::-1]  
    relevant_history = [last_four_messages[i] for i in sorted_indices[:3]]
    
    print(f"Relevant History:{relevant_history}")

    # Step 4: Determine query type and adjust temperature
    query_type = determine_query_type(query_text)
    temperature = 0.1 if query_type == "numerical" else 0.7 

    # Step 5: Handle follow-up clarification and elaboration
    is_follow_up = len(conversation_history) > 1  # If more than one message exists, consider it a follow-up
    if is_follow_up and ("explain" in query_text.lower() or "elaborate" in query_text.lower()):
        relevant_history = [relevant_history[0]] 

    # Step 6: Adjusting history relevance (optional)
    if is_follow_up:
        recent_context = conversation_history[-2:] 
        relevant_history = recent_context + relevant_history  
    
    print(f"Relevant History:{relevant_history}")

    # book_context_text = [str(doc) for doc in book_context_text]  # Convert each doc to a string
    relevant_history = [str(message) for message in relevant_history]  # Convert each history message to a string

 
    inputs = {
    "summary_of_the_conversation": str(summary),  # Ensure it's a string
    "context": "\n".join(context),  # Ensure it's a string (concatenated context)
    "question": str(query_text),  # Ensure the question is a string
    "history": "\n".join(relevant_history),  # Ensure it's a string
    "is_follow_up": is_follow_up  # Ensure it’s a boolean or string
    }

    print(f"Before inputs:{inputs}")


    # Step 8: Create the model instance with dynamic temperature adjustment
    model = Ollama(model=model_name, temperature=temperature)

    # Step 9: Build the retrieval chain using RunnablePassthrough
    retrieval_chain = (
        RunnablePassthrough()  # Pass the inputs directly through
        | ChatPromptTemplate.from_template(COT_PROMPT_WITH_HISTORY3)  # Format the prompt with inputs
        | model  # Invoke the model with the formatted prompt
        | StrOutputParser()  # Parse the output into a string
    )

    # Step 10: Stream the response chunks
    try:
        for chunk in retrieval_chain.stream(inputs):
            yield chunk
    except Exception as e:
        yield f"Error occurred while streaming response: {e}"



