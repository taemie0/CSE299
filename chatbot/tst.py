import uuid
from datetime import datetime
from chatbot.agents.agents import run_agent  # Import your run_agent function from agents.py
import langchain
import langchain_community

# Sample chat history
chat_history = [
    {"role": "user", "content": "What is gravitational force?"},
    {"role": "bot", "content": "Gravitational force is the force of attraction between two masses..."}
]

# Function to simulate a user query and retrieve the bot response
def debug_chatbot():
    print("LangChain Version:", langchain.__version__)
    print("LangChain Community Version:", langchain_community.__version__)
    try:
        # Simulate a user input
        user_input = "My name is Mehar."
        
        # Print current chat history for debugging
        print("Current Chat History:")
        for entry in chat_history:
            print(f"{entry['role']}: {entry['content']}")
        
        # Run the agent with user input and the current chat history
        response = run_agent(user_input, chat_history)
        
        # Print the response from the agent
        print("\nResponse from the chatbot:")
        print(response)
    
    except Exception as e:
        # Print any exceptions that occur during the process
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Call the debug function to test the chatbot
    debug_chatbot()
