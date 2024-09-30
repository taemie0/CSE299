import streamlit as st
import requests
import time

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
    """Delete a session"""
    if session_name in st.session_state.sessions:
        st.session_state.sessions.remove(session_name)
        if st.session_state.current_session == session_name:
            st.session_state.current_session = st.session_state.sessions[0] if st.session_state.sessions else None
        # st.experimental_rerun()

def create_new_session():
    """Create a new session"""
    new_session_name = f"Session {len(st.session_state.sessions) + 1}"
    st.session_state.sessions.append(new_session_name)
    st.session_state.current_session = new_session_name

def init_session_state():
    """Initialize session state for sessions, chat history, and user input"""
    st.session_state.setdefault('sessions', ["Session 1", "Session 2", "Session 3"])
    st.session_state.setdefault('current_session', st.session_state.sessions[0])
    st.session_state.setdefault('chat_history', [])
    st.session_state.setdefault('user_input', "")
    st.session_state.setdefault('selected_model', 'gemma2:2b') 
    st.session_state.setdefault('disabled', False)

# ========== UI Functions ==========

def session_management_ui():
    """Sidebar layout for session management"""
    st.sidebar.subheader("Current Session")
    st.sidebar.markdown(f"<div class='current-session' style='padding:2px; font-size:14px;font-weight: normal'>🗂 {st.session_state.current_session}</div>", unsafe_allow_html=True)

    st.sidebar.subheader("Previous Sessions")
    for session in st.session_state.sessions:
        if session != st.session_state.current_session:
            col1, col2 = st.sidebar.columns([5, 1])
            with col1:
                st.markdown(f"<div class='session-name'>{session}</div>", unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"delete_{session}"):
                    delete_session(session)

def display_chat():
    """Display chat messages in the main section"""
    icons = {"user": "👧", "bot": "🤖"}  
    
    for msg in st.session_state.chat_history:
        role, content = msg['role'], msg['content']
        align = 'right' if role == 'user' else 'left'
        content_cleaned = content.replace("</span>", "").strip()
        st.markdown(f"""
            <div style='text-align: {align}; margin-bottom: 15px;'>
                <span style='padding-right: 8px;'>{icons[role]}</span>
                <span style='background-color: {'#2C2E3B' if align == 'right' else 'transparent'};
                             color: white; padding: 10px 15px; border-radius: {'15px 15px 0 15px' if align == 'right' else '0'};'>
                    {content_cleaned}
                </span>
            </div>
        """, unsafe_allow_html=True)

def handle_user_input(user_input):
    """Handle user input and send it to the backend"""

    if user_input:
        st.session_state.disabled = True
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        display_chat()
        
        
        # Prepare data for the API request
        api_url = 'http://127.0.0.1:5000/'  
        data = {
            'message': user_input,
            'currentModel': st.session_state.selected_model  # Pass the current model from session state
        }

        st.session_state.user_input = ""  # Clear user input

        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            bot_response = response.json().get('message', 'Error: No response from server')
        else:
            bot_response = 'Error: Failed to connect to backend'

        st.session_state.chat_history.append({'role': 'bot', 'content': bot_response})
        st.session_state.disabled = False
  
        display_chat()

# ========== Main App ==========

def main():
    load_css()
    init_session_state()

    with st.sidebar:
        col1, col2 = st.columns([1, 3])
        if col1.button("➕", key="new_session"):
            create_new_session()
        # st.session_state.selected_model = col2.selectbox("Choose a Model:", ['LLaMA', 'GPT-4', 'Mistral', 'Gemma2:2b'])
        selected_model = col2.selectbox("Choose a Model:", ['gemma2:2b','mistral:latest','llama3.1:latest'])

        if selected_model:
            response = requests.post("http://127.0.0.1:5000/update_model", json={"model_name": selected_model})
        if response.status_code == 200:
            success_message = st.empty()  # Create an empty placeholder
            success_message.success("Model updated in config.yaml!")
            st.session_state.selected_model = selected_model
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


    user_input = st.chat_input(placeholder="Type your message...", disabled=st.session_state.disabled , on_change=disable)
    if user_input:
        handle_user_input(user_input)
    
if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

def disable():
    st.session_state["disabled"] = True

if __name__ == "__main__":
    main()
