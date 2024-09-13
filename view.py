import os
import streamlit as st
from streamlit_chat import message
from database import ask_rag

st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title("Aplicando IA em Chatbots")

# WARNING: This will PERMANENTLY delete the entire database
# if ONLY_NEW_CONTENT:
# if st.button("Delete database"):

data_source = st.selectbox(
    'Source of data:',
    ('Simple text', 'URL'))

def generate_context(prompt, context_data='generated'):
    context = []
    # If any history exists
    if st.session_state['generated']:
        # Add the last three exchanges
        EXCHANGE_LIMIT = 3
        size = len(st.session_state['generated'])
        for i in range(max(size-EXCHANGE_LIMIT, 0), size):
            context.append(
                {'role': 'user', 'content': st.session_state['user_input'][i]})
            context.append(
                {'role': 'assistant', 'content': st.session_state[context_data][i]})
    # Add the latest user prompt
    context.append({'role': 'user', 'content': str(prompt)})
    return context


# Generated natural language
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
# Neo4j database results
if 'rag_generated' not in st.session_state:
    st.session_state['rag_generated'] = []

if "source" not in st.session_state:
    st.session_state["source"] = None

if 'database_results' not in st.session_state:
    st.session_state['database_results'] = []
# User input
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []

def get_text():
    input_text = st.text_input("Ask away", "", key="input")
    return input_text


# Define columns
col1, col2 = st.columns([2, 1])

with col2:
    another_placeholder = st.empty()
    third_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()


if user_input:
    if data_source == 'Movies Database':
        pass
    elif data_source == 'Simple text':
        st.session_state['user_input'].append(user_input)
        # Ask RAG
        responses = ask_rag(user_input, source="pdf")

        print(responses['rag'])
        st.session_state['generated'].append(responses['llm'])
        st.session_state['rag_generated'].append(responses['rag']['answer'])
        st.session_state['source'] = responses['rag']["context"][0].metadata["source"]
        # pass

    else:
        pass

# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        size = len(st.session_state['generated'])
        # Display only the last two exchanges
        for i in range(max(size-2, 0), size):
            message(st.session_state['user_input'][i],
                    is_user=True,key=str(i) + '_user')
            message(st.session_state["generated"][i], avatar_style="bottts",key=str(i)+"_generated")
            message(st.session_state["rag_generated"][i], avatar_style="bottts-neutral",key=str(i)+"_rag")

# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['source']:
        st.text_area("Source",
                     st.session_state['source'], height=240)
