import streamlit as st
from utils import get_study_response, get_mcqs

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Smart Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# Session State Initialization
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "show_history" not in st.session_state:
    st.session_state.show_history = False

if "mcqs" not in st.session_state:
    st.session_state.mcqs = None

# ---------------------------
# Sidebar: Level & Response Style
# ---------------------------
st.sidebar.title("⚙️ Settings")

subject = "General"

difficulty = st.sidebar.selectbox(
    "📊 Select Level",
    ["Beginner", "Intermediate", "Advanced", "Deeper"],
    index=0
)

response_style = st.sidebar.selectbox(
    "📝 Response Style",
    ["Normal", "Short Answer", "Bullet Points", "Exam Mode"],
    index=0
)

# Toggle chat history visibility
if st.sidebar.button("📜 Chat History"):
    st.session_state.show_history = not st.session_state.show_history

# ---------------------------
# Header Section
# ---------------------------
st.markdown(
    "<h1 style='text-align:center; color:#4B0082;'>🎓 Smart Study Assistant</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:gray;'>Get clear, concise, and exam-ready answers instantly!</p>", 
    unsafe_allow_html=True
)
st.markdown("---")

# ---------------------------
# Input Section
# ---------------------------
st.markdown("**Enter your question:**")
st.text_area("", key="q_input", height=100, placeholder="Type your question here...")
st.button("🚀 Generate Answer", on_click=lambda: ask_question())

# ---------------------------
# Function: Ask Question
# ---------------------------
def ask_question():
    q = st.session_state.q_input.strip()
    if not q:
        return

    # Move current chat to history if exists
    if st.session_state.current_chat:
        st.session_state.chat_history.append(st.session_state.current_chat)

    st.session_state.pending_question = q
    st.session_state.q_input = ""
    st.session_state.mcqs = None  # Reset MCQs for new question

# ---------------------------
# Function: Display Messages
# ---------------------------
def display_message(role, text, style="Normal"):
    """
    Display chat messages in colored boxes
    role: 'user' or 'assistant'
    style: For bullet points rendering
    """
    if style == "Bullet Points":
        # Replace '-' with bullet symbol
        text = text.replace("- ", "• ")

    if role == "user":
        st.markdown(
            f"<div style='background-color:#D1E8FF; padding:10px; border-radius:8px;'>**You:** {text}</div>", 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='background-color:#FFF2CC; padding:10px; border-radius:8px;'>**Smart Study Assistant:** {text}</div>", 
            unsafe_allow_html=True
        )

# ---------------------------
# Model Call
# ---------------------------
if st.session_state.pending_question:
    with st.spinner("Thinking..."):
        try:
            answer = get_study_response(
                st.session_state.pending_question,
                subject,
                difficulty,
                response_style
            )

            # Fix bullet points formatting
            if response_style == "Bullet Points":
                lines = answer.splitlines()
                formatted = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("-"):
                        line = "- " + line
                    formatted.append(line)
                answer = "\n".join(formatted)

            st.session_state.current_chat = {
                "question": st.session_state.pending_question,
                "answer": answer,
                "subject": subject,
                "difficulty": difficulty,
                "response_style": response_style
            }

        except Exception:
            st.error("Something went wrong while generating the answer.")

        finally:
            st.session_state.pending_question = None

# ---------------------------
# Display Current Chat
# ---------------------------
if st.session_state.current_chat and not st.session_state.show_history:
    display_message("user", st.session_state.current_chat["question"])
    display_message(
        "assistant", 
        st.session_state.current_chat["answer"], 
        style=st.session_state.current_chat["response_style"]
    )

# ---------------------------
# MCQ Generator
# ---------------------------
if st.session_state.current_chat and not st.session_state.show_history:
    if st.button("📝 Generate MCQs"):
        with st.spinner("Generating MCQs..."):
            try:
                st.session_state.mcqs = get_mcqs(
                    st.session_state.current_chat["question"],
                    st.session_state.current_chat["difficulty"]
                )
            except Exception:
                st.error("Failed to generate MCQs.")

# Display MCQs
if st.session_state.mcqs:
    st.markdown("<h3 style='color:#4B0082;'>🧪 Practice MCQs</h3>", unsafe_allow_html=True)
    st.markdown(
        "<div style='background-color:#F0F8FF; padding:10px; border-radius:8px;'>"
        + st.session_state.mcqs.replace("- ", "• ")
        + "</div>",
        unsafe_allow_html=True
    )

# ---------------------------
# Chat History View
# ---------------------------
if st.session_state.show_history:
    st.subheader("📜 Chat History")

    if st.button("🧹 Clear History"):
        st.session_state.chat_history.clear()
        st.success("Chat history cleared!")

    if not st.session_state.chat_history:
        st.info("No previous chats yet.")
    else:
        for chat in reversed(st.session_state.chat_history):
            display_message("user", chat["question"])
            display_message(
                "assistant", 
                chat["answer"], 
                style=chat["response_style"]
            )
            st.markdown("---")
