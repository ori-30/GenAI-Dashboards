import streamlit as st
from streamlit_chat import message
import streamlit.components.v1 as components  # Import Streamlit
import requests
import json

st.set_page_config(
    page_title="GenAI dashboards",
    page_icon=":heart:"
)


with st.sidebar:

	st.header("Chatbot")
	#st.markdown("dashboards")

	if 'generated' not in st.session_state:
	    st.session_state['generated'] = []

	if 'past' not in st.session_state:
	    st.session_state['past'] = []


	def get_text():
	    input_text = st.text_input("You: ","", key="input")
	    return input_text 


	user_input = get_text()

	if user_input:
	    output = "Esto es una respuesta"
	    st.session_state.past.append(user_input)
	    st.session_state.generated.append(output)

	if st.session_state['generated']:

	    for i in range(len(st.session_state['generated'])-1, -1, -1):
	        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
	        message(st.session_state["generated"][i], key=str(i))

container= st.container()

def get_JSON():
	dominios ='{"Dominios": [{ "titulo": "Dominio 1", "tablas": ["tabla1","tabla2"] }, { "titulo": "Dominio 2", "tablas": ["tabla3","tabla4"] }, { "titulo": "Dominio 3", "tablas": ["tabla1","tabla2"] }, { "titulo": "Dominio 4", "tablas": ["tabla1","tabla2"] }]}'
	return json.loads(dominios)

def tables(alltables):
	r=""
	for table in alltables:
		r+= """<p class="card-text">%s</p>""" % str(table)
	return r
def create_card(title, alltables):

	card="""
			<div class="card m-2" style="width: 18rem;">
			  <div class="card-body bg-light">
			    <h3 class="card-title">Dominio:%s</h3>
	""" % str(title)
	card+=tables(alltables)

	card+=""" 			  
				</div>
			</div>
		"""
	st.markdown(card, unsafe_allow_html= True)

def create_domains(dominios):
	c0, c1, c2= container.columns(3)
	i=0
	for dominio in dominios:
		if i==0:
			with c0:
				create_card(dominio["titulo"], dominio["tablas"])
		if i==1:
			with c1:
				create_card(dominio["titulo"], dominio["tablas"])
		if i==2:
			with c2:
				create_card(dominio["titulo"], dominio["tablas"])
		i=(++i)%3



with container:
	_bootstrap="""<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">"""
	st.markdown(_bootstrap, unsafe_allow_html= True)
	dominios=get_JSON()
	create_domains(dominios["Dominios"])

		

