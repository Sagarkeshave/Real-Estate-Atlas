import streamlit as st
import pandas as pd
# from rag_memory import Chatbot
from rag import get_response
# from langchain.memory import ConversationBufferWindowMemory


# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="🏡 NoBroker Real Estate Assistant", layout="wide")
st.title("🏡 Atlas ")
st.markdown("Your AI campanion to find you; your dream home.!")


# SIDEBAR 
with st.sidebar:
    st.header("💬 Example Queries")
    st.markdown("""
    - Show me flats above 90 Cr in Pune city  
    - Please list me properties near Dehu Road  
    - Give me all projects of Ashwini Builder  
    - I want properties below 2 Cr ready to move near Baner side  
    """)
    st.markdown("---")
    st.caption("Powered by LangChain ⚙️ | Chroma 🧠 | Gemini 2.5 🚀")


# SESSION STATE 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # store tuples of (role, content)

# DISPLAY CHAT 
chat_container = st.container()
with chat_container:
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.chat_message("user").markdown(message)
        else:
            st.chat_message("assistant").markdown(message)

# USER INPUT 
prompt = st.chat_input("Type your property query...")

if prompt:
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append(("user", prompt))

    # Process and get RAG response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching for properties and generating insights..."):
            try:

                # bot = Chatbot() 
                # response, retrieved_docs = st.session_state.bot.get_response(prompt)
                response, retrieved_docs = get_response(prompt)

                num_docs = len(retrieved_docs)

                # st.markdown(f"### 🏠 Summary:")
                st.markdown(response)

                # Store assistant reply in session
                st.session_state.chat_history.append(("assistant", response))
            except Exception as e:
                error_msg = f"⚠️ Error while generating response: {e}"
                st.error(error_msg)
                st.session_state.chat_history.append(("assistant", error_msg))
