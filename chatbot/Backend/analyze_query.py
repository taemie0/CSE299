import argparse
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.llms.ollama import Ollama
from langchain.memory import ConversationBufferMemory 

ANALYZE_PROMPT_TEMPLATE = """
You are a friendly physics assistant for students, helping them learn through clear and engaging explanations. Answer the following question based on the information below, and refer to previous discussions for continuity. Keep responses accurate, accessible, and enjoyable!
Conversation so far: {history}
query: {question}

Analyze which of the following criteria the query falls under:
1. 📘 **Factual Data**: Provide a concise, direct answer, suitable for straightforward facts, definitions, or basic principles. Keep explanations brief and to the point, adding only essential clarification if needed.  

2. 📖 **Conceptual Analysis**: Offer a well-rounded explanation of the concept. Break down complex ideas into simple language and include relevant examples, analogies, or real-world applications to enhance understanding. If appropriate, end with a thought-provoking question to encourage curiosity and further exploration.  

3. 🧮 **Problem-Solving Data**: Start with any necessary theoretical background or formula, and work through a clear, step-by-step solution using LaTeX for mathematical expressions. Highlight the final answer neatly to reinforce clarity and understanding.  

If the query falls under any criteria above, tell the name.

If it doesn't fall under any criteria, tell NO.
"""

def query_analyze(query_text: str, memory: ConversationBufferMemory):
    """Analyze the query using the Ollama model and return the response."""
    
    # Load conversation history from memory
    conversation_history = memory.load_memory_variables({}).get("history", "")

    # Prepare the inputs for the prompt template
    content = {
        "question": query_text,
        "history": conversation_history
    }

    # Create the prompt template and the model
    prompt_template = ChatPromptTemplate.from_template(ANALYZE_PROMPT_TEMPLATE)
    model = Ollama(model="gemma2:2b")  # Assuming "gemma2:2b" as the model name

    # Build the chain using RunnablePassthrough
    analysis_chain = (
        RunnablePassthrough()  # Pass the inputs directly through
        | prompt_template  # Format the prompt with the inputs
        | model  # Invoke the model with the formatted prompt
        | StrOutputParser()  # Parse the model's output into a string
    )

    # Run the chain and get the final response
    response = analysis_chain.invoke(content)

    # Save the new interaction to memory
    memory.save_context({"input": query_text}, {"output": response})

    return response

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    parser.add_argument("--chat_history", type=str, help="The chat history to pass to the model.")
    
    args = parser.parse_args()
    
    # Initialize memory with chat history if provided
    memory = ConversationBufferMemory()
    if args.chat_history:
        memory.chat_memory.add_user_message(args.chat_history)

    # Call the main query function
    response = query_analyze(args.query_text, memory)
    print(response)

if __name__ == "__main__":
    main()
