import os
import streamlit as st
from view.view import View
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


class ChatURLView(View):

    def __init__(self):
        st.title("Compliance Assistant")
        # self.values = st.slider("Buscar em quantos documentos", 1, 10)
        self.link_url = st.text_input("Insira o link da noticia", "Link")
        self.link_upload_button = st.button("Enviar link")
        self.retriever_k = 1


        col1, col2 = st.columns([2, 1])

        self.key:int=0

        with col2:
            self.another_placeholder = st.empty()
            self.third_placeholder = st.empty()
        with col1:
            self.human_message = st.chat_message("user")
            self.llm_message = st.chat_message("gpt" )
            self.rag_message = st.chat_message("rag" )

        
        self.user_input = st.text_input("Type your message here:", "")

        st.session_state['user_input'] = []
        st.session_state['generated_stream'] = None
        st.session_state['generated'] = []
        st.session_state['rag_stream'] = None
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
        self.retriever_k = self.values
        return self.user_input

    def display(self, responses=None):
        if self.user_input:        
            st.session_state['user_input'].append(self.user_input)
            st.session_state['generated'].append(responses['llm'])
            st.session_state['rag_generated'].append(responses['rag']['answer'])
            sources = ""
            for i in range(len(responses['rag']['context'])):
                print("Context: ",responses['rag']['context'][i].metadata["source"])
                sources+=responses['rag']['context'][i].metadata["source"]+"\n"
            st.session_state['source'] = sources
            if "llm_stream" in responses:
                st.session_state['generated_stream'] = responses['llm_stream']
            if "rag_stream" in responses:
                st.session_state['rag_stream'] = responses['rag_stream']

        # # Message placeholder
        # with self.placeholder.container():
        #     if st.session_state['generated']:
                
        #         size = len(st.session_state['generated'])
        #         # Display only the last two exchanges
        #         for i in range(max(size-2, 0), size):
        #             print(str(i),"User input: ", st.session_state['user_input'][i])
        #             message(st.session_state['user_input'][i],
        #                     is_user=True,key=str(self.key) + '_user')
        #             message(st.session_state["generated"][i], avatar_style="bottts",key=str(self.key)+"_generated")
        #             message(st.session_state["rag_generated"][i], avatar_style="bottts-neutral",key=str(self.key)+"_rag")
                
        with self.human_message.container():
            if st.session_state['user_input']:
                self.human_message.text(st.session_state['user_input'][-1])
        
        with self.llm_message.container():
            if st.session_state['generated_stream']:
                st.write_stream(st.session_state['llm_stream'])
            elif st.session_state['generated']:
                self.llm_message.text(st.session_state['generated'][-1])
            
        with self.rag_message.container():
            if st.session_state['rag_stream']:
                st.write_stream(st.session_state['rag_stream'])
            elif st.session_state['rag_generated']:
                self.rag_message.text(st.session_state['rag_generated'][-1])

        # Generated Cypher statements
        with self.another_placeholder.container():
            if st.session_state['source']:
                st.text_area("Source",
                            st.session_state['source'],key=self.key, height=240)
        
        self.key += 1
                

# if __name__ == "__main__":
#     view = ChatView()
#     view.display()
#     # setup_view()