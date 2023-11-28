import streamlit as st
from streamlit_chat import message
import streamlit.components.v1 as components  # Import Streamlit
import requests
import json
from openai import OpenAI
from typing import List
from functions import *
st.set_page_config(
    page_title="GenAI domains",
    page_icon=":heart:"
)


#abrir openAI key con streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

#crear modelo por defecto
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

#inizializar chat
if "messages" not in st.session_state:
    st.session_state.messages = []


#creamos la sidebar
with st.sidebar:
	st.header("Chatbot", divider='rainbow')
	prompt = get_text()
	#mostramos el chat de mensajes desde el historial
	for message in st.session_state.messages:
	    with st.chat_message(message["role"]):
	        st.markdown(message["content"])

	# Accept user input
	if prompt:
	    # Add user message to chat history
	    st.session_state.messages.append({"role": "user", "content": prompt})
	    # Display user message in chat message container
	    with st.chat_message("user"):
	        st.markdown(prompt)
	    # Display assistant response in chat message container
	    with st.chat_message("assistant"):
	        message_placeholder = st.empty()
	        full_response = ""
	cl=client.chat.completions.create(model=st.session_state["openai_model"], messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages], stream=True)
	for response in cl:
		full_response +=(response.choices[0].delta.content or "")
		message_placeholder.markdown(full_response + "▌")
	message_placeholder.markdown(full_response)
	st.session_state.messages.append({"role": "assistant", "content": full_response})      


container= st.container()
with container:
	bootstrap()
	create_sql_statment(container)
	dominios=get_JSON()
	create_domains(dominios["Dominios"], container)

		

