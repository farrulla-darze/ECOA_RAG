import os
import streamlit as st
from streamlit_chat import message
# from model.database import ask_rag

def _generate_context(prompt, context_data='generated'):
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

def _get_text():
    input_text = st.text_input("Ask away", "", key="input")
    return input_text

# if 'user_input' not in st.session_state:


class ChatView():

    def __init__(self):
        st.title("Simple Chat Interface")
        self.data_source = st.selectbox(
        'Source of data:',
        ('Simple text', 'URL'))

        col1, col2 = st.columns([2, 1])

        with col2:
            self.another_placeholder = st.empty()
            self.third_placeholder = st.empty()
        with col1:
            self.placeholder = st.empty()

        self.key:int=0
        
        self.user_input = st.text_input("Type your message here:", "")

        st.session_state['user_input'] = []
        st.session_state['generated'] = []
        st.session_state['rag_generated'] = []
        st.session_state['source'] = None

    def _generate_context(self, prompt, context_data='generated'):
        context = []
        # If any history exists
        if st.session_state['generated']:
            # Add the last three exchanges
            EXCHANGE_LIMIT = 3
            size = len(st.session_state['generated'])
            for i in range(max(size-EXCHANGE_LIMIT, 0), size):
                context.append(
                    {'role': 'user', 'content': st.session_state['user_input'][i]}
                )
                context.append(
                    {'role': 'assistant', 'content': st.session_state[context_data][i]}
                )
        # Add the latest user prompt
        context.append({'role': 'user', 'content': str(prompt)})
        return context

    def get_text(self):
        return self.user_input

    def display(self, responses=None):
        if self.user_input:
            if self.data_source == 'Movies Database':
                pass
            elif self.data_source == 'Simple text':
                st.session_state['user_input'].append(self.user_input)
                # Ask RAG
                # responses = ask_rag(self.user_input)
                # responses = {"query": self.user_input, "llm": "LLM ANSWER", "rag": {"question":self.user_input,"answer":"RAG ANSWER","context":[{"metadata":{"source":"Simple text"}}]}}

                # print(responses['rag'])
                st.session_state['generated'].append(responses['llm'])
                st.session_state['rag_generated'].append(responses['rag']['answer'])
                st.session_state['source'] = responses['rag']["context"][0].metadata["source"]
                # pass

            else:
                pass
            
        # Message placeholder
        with self.placeholder.container():
            if st.session_state['generated']:
                size = len(st.session_state['generated'])
                # Display only the last two exchanges
                for i in range(max(size-2, 0), size):
                    print(str(i),"User input: ", st.session_state['user_input'][i])
                    message(st.session_state['user_input'][i],
                            is_user=True,key=str(self.key) + '_user')
                    message(st.session_state["generated"][i], avatar_style="bottts",key=str(self.key)+"_generated")
                    message(st.session_state["rag_generated"][i], avatar_style="bottts-neutral",key=str(self.key)+"_rag")
                
                    self.key+=1

        # Generated Cypher statements
        with self.another_placeholder.container():
            if st.session_state['source']:
                st.text_area("Source",
                            st.session_state['source'],key=self.key, height=240)
                

# if __name__ == "__main__":
#     view = ChatView()
#     view.display()
#     # setup_view()