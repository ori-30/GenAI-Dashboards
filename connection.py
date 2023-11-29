import streamlit as st
from streamlit_chat import message
import streamlit.components.v1 as components  # Import Streamlit
import requests
import json
from openai import OpenAI
from typing import List
from functions import *
# import MetadataExtractor as me
st.set_page_config(
    page_title="GenAI domains",
    page_icon=":heart:",
)

if 'display_result' not in st.session_state:
	st.session_state.display_result = True
if 'reset' not in st.session_state:
    st.session_state.reset = False
if 'area' not in st.session_state:
	st.session_state['area']=""
if 'description' not in st.session_state:
	st.session_state['description']=""

def callback():
	if des:
		st.session_state['area']=area
		st.session_state['description']=des
		st.session_state.display_result=False
		st.session_state.reset=False
	else:
		st.error("Por favor, rellene ambos campos")

if not st.session_state.display_result:
	prompt_metadata = open('promptstartups.txt', 'r').read()
	#abrir openAI key con streamlit secrets
	client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
	prompt_metadata +="El area de la empresa es "+ st.session_state.area + " y la descripción de la empresa es "+ st.session_state.description

	#crear modelo por defecto
	if "openai_model" not in st.session_state:
	    st.session_state["openai_model"] = "gpt-3.5-turbo"

	#inizializar chat
	if "messages" not in st.session_state:
	    st.session_state.messages = [{"role": "system", "content": prompt_metadata}]
	   


	#creamos la sidebar
	with st.sidebar:
		st.header("Chatbot", divider='rainbow')
		# Aceptamos input del usuario
		prompt = get_text()
		#mostramos el chat de mensajes desde el historial
		for message in st.session_state.messages:
			
			if message["role"]!="system":
			    with st.chat_message(message["role"]):
		        	st.markdown(message["content"])
		if prompt:
			#añadimos mensaje del usuario
			st.session_state.messages.append({"role": "user", "content": prompt})
			#mostramos mensaje del usuario
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
		create_domains(dominios["dominios"], container)

if st.session_state.display_result:
	area=get_area()
	des=get_des()
	send=st.button("Generar", disabled=(area is ""), on_click=callback)


