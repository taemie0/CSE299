from langchain.tools import Tool
from langchain.agents import create_react_agent
from langchain_community.llms.ollama import Ollama
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.prompts import ChatPromptTemplate
from chatbot.Server.Backend.query_Prompt import query_rag


# Custom conversation template for the assistant
CUSTOM_CONVERSATION_TEMPLATE = """
The following is a conversation with a helpful assistant. The assistant is intelligent, knowledgeable, and tries to help the user in the best possible way.

Current Conversation:
{history}

Tools available:
{tools}

Tool names:
{tool_names}

Agent Scratchpad:
{agent_scratchpad}

User: {input}

Assistant:"""

# Tool 1: Physics Knowledge from RAG (retrieval using ChromaDB)
def fetch_from_rag(query: str):
    return query_rag(query)

rag_tool = Tool(
    name="Physics Retrieval",
    func=fetch_from_rag,
    description="Fetch physics-related information from RAG using the local vector database."
)

# Tool 2: Calculation Tool (Simple calculator using Python's eval)
def physics_calculator(expression: str):
    try:
        return eval(expression)
    except Exception as e:
        return str(e)

calc_tool = Tool(
    name="Physics Calculator",
    func=physics_calculator,
    description="Perform calculations relevant to physics problems."
)

# Tool 3: Conversation Memory Tool
def conversation_memory(query: str, chat_history: list):
    # Fetch previous memory for the session from MongoDB
    # conversation_history = fetch_history(session_name)
    return query_rag(query, chat_history) if chat_history else None

memory_tool = Tool(
    name="Conversation Memory",
    func=conversation_memory,
    description="Hold conversation with memory."
)

# Initialize your LLM (Ollama, in this case)
llm = Ollama(model="gemma2:2b")

# Create a list of tools to pass to the agent
tools = [rag_tool, calc_tool, memory_tool]

# Extract tool names for the prompt
tool_names = [tool.name for tool in tools]

# Use create_react_agent for initializing the agent
agent = create_react_agent(
    tools=tools,
    llm=llm,
    prompt=ChatPromptTemplate.from_template(CUSTOM_CONVERSATION_TEMPLATE),
)

def run_agent(query: str, chat_history: list):
    # Load previous memory into the agent's memory if available
    # conversation_history = fetch_history(session_name)
    
    # Update the conversation history in the prompt
    if chat_history:
        formatted_history = "\n".join(
            f"{entry['role']}: {entry['content']}" for entry in chat_history
        )
    else:
        formatted_history = ""

    memory_input = f"{formatted_history}\nUser: {query}\nAssistant:"
    # Prepare the agent scratchpad (you can customize this based on your logic)
    agent_scratchpad = ""  # Initialize or load your scratchpad data if needed

    # Run the agent with the user query
    result = agent.invoke({
        "input": query,
        "history": memory_input,
        "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
        "tool_names": ", ".join(tool_names),
        "agent_scratchpad": agent_scratchpad,
    })
    return result
