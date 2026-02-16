import streamlit as st
from weather_agent import weather_agent

st.set_page_config(page_title="Weather Chatbot", page_icon="🌤")

st.title("🌤 Weather Chatbot")
st.write("Ask about weather or tell me where you live.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box
if prompt := st.chat_input("Type your message..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    response = weather_agent(prompt)

    # Show bot response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
