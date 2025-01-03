from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate

PROMPT = """
Current Summary:
{current_summary}
recent conversation:
{conversation_text}
Generate an updated summary for the conversation:
"""

# Function to generate a new summary using the Ollama model
def generate_new_summary(current_summary, recent_conversation):
    """
    Generates a new summary by combining the current summary and recent conversation using an Ollama model.
    
    Parameters:
    current_summary (str): The existing summary of the conversation.
    recent_conversation (list): The most recent conversation history as a list of message objects.
    
    Returns:
    str: The newly generated summary.
    """
    # Prepare the input for the model
    conversation_text = "\n".join([f"{entry['role']}: {entry['content']}" for entry in recent_conversation])
    combined_input = ChatPromptTemplate.from_template(PROMPT).format(current_summary=current_summary, conversation_text=conversation_text)

    # Initialize the Ollama model (use the specific model name you have available)
    model_name = "qwen:0.5b"  # Replace with the actual model name
    model = Ollama(model=model_name)

    # Generate the summary
    response = model.invoke(input=combined_input)  # Use the 'input' argument here to pass the prompt
    
    print(f"Generated Summary: {response}")
    # Return the response (new summary)
    return response
