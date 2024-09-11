from typing import List
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import SeleniumURLLoader 
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os
from database import Database
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

mock_urls = ["https://pt.wikipedia.org/wiki/Javier_Milei",
        "https://www.cbsnews.com/news/super-bowl-winners-list-history/",
        "https://ge.globo.com/futebol/times/corinthians/noticia/2024/02/16/corinthians-anuncia-a-contratacao-do-lateral-direito-matheuzinho.ghtml",
        "https://ge.globo.com/futebol/times/botafogo/noticia/2024/02/16/luiz-henrique-do-botafogo-tem-lesao-na-panturrilha.ghtml",
        "https://ge.globo.com/futebol/times/fluminense/noticia/2024/02/16/escalacao-do-fluminense-diniz-escala-reservas-contra-madureira-mas-tera-john-kennedy-e-douglas-costa.ghtml",
    "https://www.lemonde.fr/football/article/2024/02/25/ligue-1-le-psg-arrache-le-nul-de-justesse-contre-rennes-monaco-remonte-sur-le-podium_6218528_1616938.html",
    "https://ge.globo.com/futebol/futebol-internacional/futebol-frances/copa-da-franca/noticia/2024/02/27/perri-e-heroi-nos-penaltis-e-lyon-avanca-de-fase-na-copa-da-franca.ghtml",
    "https://ge.globo.com/tenis/noticia/2024/02/27/joao-fonseca-sofre-com-condicoes-ruins-da-quadra-no-atp-santiago-e-e-eliminado.ghtml",   
]

class WebDatabase(Database):

    _instance = None

    @property
    def vectorstore(self) -> Chroma:
        return self.vectorstore

    def __init__(self, load=True, urls=mock_urls) -> None:
        if os.path.exists("./chroma_db") and load:
        
            self.vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=OpenAIEmbeddings()
            )
        else:
            loader = SeleniumURLLoader(urls=urls)
            docs = loader.load()

            print("Loaded documents")

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            splits = text_splitter.split_documents(docs)

            print("Splitted documents")

            self.vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="./chroma_db")


    def format_docs(self, docs: List[Document]):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def _setup_rag(self):
        # super()
        retriever = self.vectorstore.as_retriever()
        prompt = hub.pull("rlm/rag-prompt")
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=openai_key)

        rag_chain_from_docs = ( RunnablePassthrough.assign(
            context=(lambda x: self.format_docs(x["context"])))
            | prompt
            | llm
            | StrOutputParser()
        )

        rag_chain_with_source = RunnableParallel(
            {"context": retriever, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)

        return rag_chain_with_source

    def ask_rag(self, query,debug=False):
        rag = self._setup_rag()
        print("key", openai_key)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=openai_key)
        if debug:
            responses = {"query": query, "llm": "LLM ANSWER", "rag": "RAG ANSWER"}
            print(responses)
            return responses
        responses = {"query": query, "llm": llm.invoke(query).content, "rag": rag.invoke(query)}
        return responses

