import streamlit as st
import requests
import time
from datetime import datetime
import uuid


st.set_page_config(
    page_title="Physics ChatBot",
    page_icon="icons/physics_96px.png",
)

# ========== Utility Functions ==========

def load_css():
    """Load external CSS from a file"""
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def delete_session(session_name):
    try:
        response = requests.delete(f"http://127.0.0.1:5000/delete_session/{session_name}")
        if response.status_code == 200:
            
            # Remove the session from the state after successful deletion
            st.session_state.sessions = [s for s in st.session_state.sessions if s['session_name'] != session_name]
            st.session_state.current_session = None  # Clear current session if deleted
            st.session_state.chat_history = []  # Clear chat history
            st.success("Session deleted successfully.")
            st.rerun()
        else:
            st.error("Failed to delete session.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting session: {e}")


def create_new_session():
    """Create a new session and send it to the backend"""
    new_session_name = f"Session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"  # Unique session name with timestamp
    new_session_id = str(uuid.uuid4())  # Generate a unique session ID

    # Create a session object
    new_session = {
        'session_id': new_session_id,
        'session_name': new_session_name,
        'created_at': datetime.now().isoformat(),  
        'chat_history': []  # Initialize with an empty chat history
    }

    # Send the new session to the backend
    try:
        response = requests.post("http://127.0.0.1:5000/create_session", json=new_session)
        if response.status_code == 201:  # Check if the creation was successful
            st.session_state.sessions.append(new_session)  # Add to the session state
            st.session_state.current_session = new_session_name
            
            success_placeholder = st.empty()  
            success_placeholder.success(f"Created new session: {new_session_name}")

            # Wait for a few seconds before clearing the message
            time.sleep(1)  # Wait for 2 seconds
            success_placeholder.empty()  # Clear the message
            st.session_state.chat_history = new_session['chat_history']
            st.rerun()
        else:
            st.error("Failed to create session in the backend.")
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating session: {e}")
    
# Fetch session data from the backend
def fetch_sessions():
    try:
        response = requests.get("http://127.0.0.1:5000/")  # Adjust the URL if necessary
        if response.status_code == 200:
            return response.json().get('session_data', [])
        else:
            st.error("Failed to fetch session data from the backend")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sessions: {e}")
        return []
    
# ========== Session State Management ==========

# Initialize session state for storing session data
if "sessions" not in st.session_state:
    st.session_state.sessions = sorted(fetch_sessions(), key=lambda s: s['created_at'], reverse=True)  # Fetch sessions from the backend

if "current_session" not in st.session_state:
    st.session_state.current_session = st.session_state.sessions[0]['session_name'] if st.session_state.sessions else None  # Default to the first session

# Initialize chat_history with the current session's chat history
if "chat_history" not in st.session_state:
    if st.session_state.current_session: 
        current_session_data = next((session for session in st.session_state.sessions if session['session_name'] == st.session_state.current_session), None)
        st.session_state.chat_history = current_session_data['chat_history'] if current_session_data else []  
    else:
        st.session_state.chat_history = []  # Initialize as empty if no current session

if "disabled" not in st.session_state:
    st.session_state.disabled = False  # For disabling the chat input
if "selected_model" not in st.session_state:        
    st.session_state.selected_model = 'gemma2:2b'  # For storing the selected model
if "previous_model" not in st.session_state:
    st.session_state.previous_model = None  # For storing the previous model selection
if "success_message_visible" not in st.session_state:
    st.session_state.success_message_visible = False

# ========== UI Functions ==========

def session_management_ui():
    """Sidebar layout for session management"""
    st.sidebar.subheader("Current Session")
    if st.session_state.current_session:
        st.sidebar.markdown(f"<div class='current-session' style='padding:2px; font-size:14px;font-weight: normal'>🗂 {st.session_state.current_session}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("<div class='current-session' style='padding:2px;'>No current session</div>", unsafe_allow_html=True)

    st.sidebar.subheader("Previous Sessions")
    
    for session in st.session_state.sessions:
        if session['session_name'] != st.session_state.current_session:
            col1, col2 = st.sidebar.columns([5, 1])
            with col1:
                # Make session name clickable
                if st.button(session['session_name'], key=f"select_{session['session_name']}"):
                    # Update current session and chat history
                    st.session_state.current_session = session['session_name']
                    st.session_state.chat_history = session['chat_history']  # Load chat history for the selected session
                    st.success(f"Selected session: {session['session_name']}")
                    time.sleep(0.5)  # Wait for 0.5 second
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{session['session_name']}"):
                    delete_session(session['session_name'])


def display_chat():
    st.markdown(
        """
        <style>
        .st-emotion-cache-janbn0 {
            flex-direction: row-reverse;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    icons = {"bot": "icons/physics_96px.png", "user": "icons/User_Default_96px.png"}  
    
    for msg in st.session_state.chat_history:
        role, content = msg['role'], msg['content']
        content_cleaned = content.replace("</span>", "").strip()
        with st.chat_message(role, avatar=icons[role]):
            st.markdown(content_cleaned)

def handle_user_input():
    """Handle user input widget"""
    if st.session_state.user_input:
        st.session_state.disabled = True
        st.session_state.chat_history.append({'role': 'user', 'content': st.session_state.user_input})

# ========== Main App ==========
load_css()


with st.sidebar:
    col1, col2 = st.columns([1, 3])
    if col1.button("➕", key="new_session"):
        create_new_session()
    
    selected_model = col2.selectbox("Choose a Model:", ['gemma2:2b','mistral:latest','llama3.1:latest'])

    if selected_model != st.session_state.previous_model:
        response = requests.post("http://127.0.0.1:5000/update_model", json={"model_name": selected_model})
        if response.status_code == 200:
            success_message = st.empty()  # Create an empty placeholder
            success_message.success("Model updated in config.yaml!")
            st.session_state.previous_model = selected_model
            st.session_state.success_message_visible = True
            time.sleep(2)  
            success_message.empty()  
        else:
            st.error("Failed to update model in config.yaml.")
    session_management_ui()

st.markdown("<h4 style='text-align: left; color: white;'>Physics ChatBot</h4>", unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
display_chat()
st.markdown('</div>', unsafe_allow_html=True)


st.chat_input(placeholder="Type your message...",
                key="user_input",
                on_submit=handle_user_input,
                disabled=st.session_state.disabled)


# requesting for response in backend
if st.session_state.user_input:
    time.sleep(2)  # Simulate bot response time
    api_url = 'http://127.0.0.1:5000/query'  
    data = {
        'message': st.session_state.user_input,
        'currentModel': st.session_state.selected_model,
        'currentSession': st.session_state.current_session
    }
    response = requests.post(api_url, json=data)
    if response.status_code == 200:
        bot_response = response.json().get('message', 'Error: No response from server')
        st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
        st.session_state.disabled = False
        st.rerun()
    else:
        bot_response = 'Error: Failed to connect to backend'


