import streamlit as st
from conversation import get_conversation, memory

st.set_page_config(
    page_title="QuantumLeap GPT",
    page_icon="✨",
    layout="wide"
)

# --- Modern, Dark, Fancy CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

body { font-family: 'Inter', sans-serif; }
.stApp {
    background-color: #0e1117;
    background-image: radial-gradient(circle at top right, rgba(138, 43, 226, 0.15), transparent 40%),
                      radial-gradient(circle at bottom left, rgba(74, 0, 224, 0.15), transparent 40%);
    color: #f0f2f6;
}
.chat-container { max-width: 800px; margin: 0 auto; padding: 2rem 0 5rem 0; }
.user-bubble, .bot-bubble {
    display: inline-block; padding: 14px 22px; border-radius: 24px; margin: 8px 0;
    max-width: 80%; font-size: 1.05rem; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    animation: fadeInUp 0.4s ease-out; word-wrap: break-word; line-height: 1.5;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.user-bubble { background: linear-gradient(135deg, #8A2BE2 0%, #4A00E0 100%); color: #fff; float: right; border-bottom-right-radius: 6px; }
.bot-bubble { background: #262730; color: #f0f2f6; float: left; border-bottom-left-radius: 6px; }
.clearfix { clear: both; }

.chat-title {
    text-align: center; font-size: 2.5rem; font-weight: 800; margin-bottom: 2rem;
    background: -webkit-linear-gradient(45deg, #8A2BE2, #4fc3f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 15px rgba(138, 43, 226, 0.2);
}

[data-testid="stSidebar"] { background: rgba(38, 39, 48, 0.6); backdrop-filter: blur(10px); border-right: 1px solid rgba(255, 255, 255, 0.1); }
.stSidebar h2, .stSidebar h3, .stSidebar .stMarkdown { color: #f0f2f6; }
.stSidebar .stButton>button { background-color: transparent; border: 1px solid #8A2BE2; color: #f0f2f6; border-radius: 12px; transition: all 0.2s ease; }
.stSidebar .stButton>button:hover { background-color: #8A2BE2; color: #fff; border-color: #8A2BE2; box-shadow: 0 0 15px rgba(138, 43, 226, 0.5); }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1 class='chat-title'>✨ QuantumLeap GPT</h1>", unsafe_allow_html=True)

# --- Session state initialization ---
if "history_store" not in st.session_state: st.session_state.history_store = []
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]
if "selected_model" not in st.session_state: st.session_state.selected_model = "openai/gpt-4.1"

# --- Sidebar ---
with st.sidebar:
    st.subheader("⚙️ Model Selection")
    st.session_state.selected_model = st.selectbox(
        "Choose an LLM model:",
        ["openai/gpt-4o-mini", "google/gemini-2.0-flash-001", "openai/gpt-4.1"],
        index=["openai/gpt-4o-mini", "google/gemini-2.0-flash-001", "openai/gpt-4.1"].index(st.session_state.selected_model),
        label_visibility="collapsed"
    )

    st.subheader("📜 Chat History")
    if st.session_state.history_store:
        for i, chat in enumerate(st.session_state.history_store):
            preview = chat[1]["content"] if len(chat) > 1 else "Empty Chat"
            if st.button(f"Chat {i+1}: {preview[:30]}...", key=f"history_{i}"):
                st.session_state.messages = chat

    if st.button("🧹 Clear & Start New Chat"):
        if st.session_state.messages and len(st.session_state.messages) > 1:
            st.session_state.history_store.append(st.session_state.messages)
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]
        memory.clear()
        st.rerun()

# --- Get conversation chain for selected model (memory-enabled) ---
conversation = get_conversation(st.session_state.selected_model)

# --- Chat UI ---
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.write(f"🙋 You: {message['content']}")
    else:
        st.markdown(f"<div class='bot-bubble'><b>🤖 Bot:</b> {message['content']}</div><div class='clearfix'></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- User Input ---
if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# --- LLM Response (memory-enabled) ---
if st.session_state.messages[-1]["role"] == "user":
    user_message = st.session_state.messages[-1]["content"]
    with st.spinner("Thinking..."):
        # Use conversation chain with memory
        response = conversation.predict(input=user_message)

        # Display bot bubble
        st.markdown(f"<div class='bot-bubble'><b>🤖 Bot:</b> {response}</div><div class='clearfix'></div>", unsafe_allow_html=True)

        # Save response in session and memory
        st.session_state.messages.append({"role": "assistant", "content": response})
        memory.save_context({"input": user_message}, {"output": response})
