import streamlit as st

# ========== Utility Functions ==========

def load_css():
    """Load external CSS from a file"""
    with open('/frontend/static/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def delete_session(session_name):
    """Delete a session"""
    if session_name in st.session_state.sessions:
        st.session_state.sessions.remove(session_name)
        if st.session_state.current_session == session_name:
            st.session_state.current_session = st.session_state.sessions[0] if st.session_state.sessions else None
        st.experimental_rerun()

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

# ========== UI Functions ==========

def session_management_ui():
    """Sidebar layout for session management"""
    st.sidebar.subheader("Current Session")
    st.sidebar.markdown(f"<div class='current-session' style = 'padding:2px; font-size:14px;font-weight: normal'>🗂 {st.session_state.current_session}</div>", unsafe_allow_html=True)

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
    icons = {"right": "👧", "left": "🤖"}  # User and bot icons
    for msg in st.session_state.chat_history:
        align = 'right' if msg.startswith("You:") else 'left'
        msg_cleaned = msg.split(": ", 1)[-1].strip()  # Remove prefix and clean message
        
        st.markdown(f"""
            <div style='text-align: {align}; margin-bottom: 15px;'>
                <span style='padding-right: 8px;'>{icons[align]}</span>
                <span style='background-color: {'#2C2E3B' if align == 'right' else 'transparent'};
                             color: white; padding: 10px 15px; border-radius: {'15px 15px 0 15px' if align == 'right' else '0'};'>
                    {msg_cleaned}
                </span>
            </div>
        """, unsafe_allow_html=True)



def handle_user_input():
    """Handle user input and append it to the chat"""
    user_input = st.session_state.user_input.strip()
    if user_input:
        st.session_state.chat_history.append(f"You: {user_input}")
        st.session_state.chat_history.append("Bot: This is a response.")
        st.session_state.user_input = ""

def main():
    load_css()
    init_session_state()

    with st.sidebar:
        col1, col2 = st.columns([1, 3])
        if col1.button("➕", key="new_session"):
            create_new_session()
        selected_model = col2.selectbox("Choose a Model:", ['LLaMA', 'GPT-4', 'Mistral', 'Gemma2:2b'])
        session_management_ui()

    st.title("Physics ChatBot")
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    display_chat()
    st.markdown('</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Say something")
    if prompt:
        st.session_state.chat_history.append(f"You: {prompt}")
        st.session_state.chat_history.append("Bot: This is a response.")

if __name__ == "__main__":
    main()
