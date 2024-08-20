import os
import streamlit as st
from streamlit_chat import message

st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title("Aplicando IA em Chatbots")

# WARNING: This will PERMANENTLY delete the entire database
# if ONLY_NEW_CONTENT:
# if st.button("Delete database"):
    
query_mode = st.checkbox("QUERY MODE", True)

data_source = st.selectbox(
    'Source of data:',
    ('Movies Database','Simple text', 'URL'))

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
if 'database_results' not in st.session_state:
    st.session_state['database_results'] = []
# User input
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []
# Generated Cypher statements
if 'cypher' not in st.session_state:
    st.session_state['cypher'] = []
# Graph    
if 'graph' not in st.session_state:
    st.session_state['graph'] = []

def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
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
        # webpage = st.toggle("Load url", False)
        # Hardcoded UserID
        USER_ID = "Tomaz"

        # On the first execution, we have to create a user node in the database.
        # movies_gds_db.query_database("""MERGE (u:User {id: $userId})""", {'userId': USER_ID})

        # cypher = generate_cypher(generate_context(user_input, 'database_results'))
        # cypher = movies_gds_db.construct_cypher(user_input)
        pass
    elif data_source == 'Simple text':
        pass

    else:
        pass

# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        size = len(st.session_state['generated'])
        # Display only the last three exchanges
        for i in range(max(size-3, 0), size):
            message(st.session_state['user_input'][i],
                    is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['cypher']:
        st.text_area("Latest generated Cypher statement",
                     st.session_state['cypher'][-1], height=240)

with third_placeholder.container():
    if st.session_state['database_results']:
        # Try to place the graph here
        try:
            st.pyplot(nx.draw(st.session_state['graph'][-1][0], with_labels=True, labels=st.session_state['graph'][-1][1]))
        except:
            # Error gif
            st.image("https://cdn.pixabay.com/animation/2023/01/07/11/02/11-02-30-972_512.gif")
            