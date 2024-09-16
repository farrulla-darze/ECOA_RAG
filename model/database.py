from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, SeleniumURLLoader, PDFPlumberLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


from abc import ABC, abstractmethod

import os
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

# urls = ["https://pt.wikipedia.org/wiki/Javier_Milei",
#         "https://www.cbsnews.com/news/super-bowl-winners-list-history/",
#         "https://ge.globo.com/futebol/times/corinthians/noticia/2024/02/16/corinthians-anuncia-a-contratacao-do-lateral-direito-matheuzinho.ghtml",
#         "https://ge.globo.com/futebol/times/botafogo/noticia/2024/02/16/luiz-henrique-do-botafogo-tem-lesao-na-panturrilha.ghtml",
#         "https://ge.globo.com/futebol/times/fluminense/noticia/2024/02/16/escalacao-do-fluminense-diniz-escala-reservas-contra-madureira-mas-tera-john-kennedy-e-douglas-costa.ghtml",
#     "https://www.lemonde.fr/football/article/2024/02/25/ligue-1-le-psg-arrache-le-nul-de-justesse-contre-rennes-monaco-remonte-sur-le-podium_6218528_1616938.html",
#     "https://ge.globo.com/futebol/futebol-internacional/futebol-frances/copa-da-franca/noticia/2024/02/27/perri-e-heroi-nos-penaltis-e-lyon-avanca-de-fase-na-copa-da-franca.ghtml",
#     "https://ge.globo.com/tenis/noticia/2024/02/27/joao-fonseca-sofre-com-condicoes-ruins-da-quadra-no-atp-santiago-e-e-eliminado.ghtml",   
# ]

class Database(ABC):
    _instance = None

    # Flag to track if the instance has been initialized
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if not type(self)._initialized:
            # Only initialize once
            self._initialize(*args, **kwargs)
            type(self)._initialized = True

    @abstractmethod
    def _initialize(self,*args, **kwargs):
        """Method for initialization logic, must be implemented by the subclass."""
        pass

    # @staticmethod
    # def GetInstance():
    #     if Database._instance is None:
    #         print("Creating new instance")
    #         Database._instance = Database()
    #     return Database._instance

    @abstractmethod
    def _setup_rag(self):
        raise NotImplementedError

    @abstractmethod
    def ask_rag(self, query, debug=False):
        raise NotImplementedError