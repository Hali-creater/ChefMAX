import streamlit as st
from chefmax_agent.agent import ChefMAX

st.set_page_config(page_title="ChefMAX - Your Personal Dining Assistant")
st.title("ChefMAX - Your Personal Dining Assistant")

# Initialize the agent and conversation history in the session state
if 'agent' not in st.session_state:
    st.session_state.agent = ChefMAX(menu_file="menu.json")
    st.session_state.messages = []
    # Start the conversation with the agent's greeting
    greeting = st.session_state.agent.greet()
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Display the conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("What can I get for you?"):
    # Add user message to the conversation history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get the agent's response
    response = st.session_state.agent.handle_input(prompt)

    # Add the agent's response to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
