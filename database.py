from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, SeleniumURLLoader, PDFPlumberLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")


urls = ["https://pt.wikipedia.org/wiki/Javier_Milei",
        "https://www.cbsnews.com/news/super-bowl-winners-list-history/",
        "https://ge.globo.com/futebol/times/corinthians/noticia/2024/02/16/corinthians-anuncia-a-contratacao-do-lateral-direito-matheuzinho.ghtml",
        "https://ge.globo.com/futebol/times/botafogo/noticia/2024/02/16/luiz-henrique-do-botafogo-tem-lesao-na-panturrilha.ghtml",
        "https://ge.globo.com/futebol/times/fluminense/noticia/2024/02/16/escalacao-do-fluminense-diniz-escala-reservas-contra-madureira-mas-tera-john-kennedy-e-douglas-costa.ghtml",
    "https://www.lemonde.fr/football/article/2024/02/25/ligue-1-le-psg-arrache-le-nul-de-justesse-contre-rennes-monaco-remonte-sur-le-podium_6218528_1616938.html",
    "https://ge.globo.com/futebol/futebol-internacional/futebol-frances/copa-da-franca/noticia/2024/02/27/perri-e-heroi-nos-penaltis-e-lyon-avanca-de-fase-na-copa-da-franca.ghtml",
    "https://ge.globo.com/tenis/noticia/2024/02/27/joao-fonseca-sofre-com-condicoes-ruins-da-quadra-no-atp-santiago-e-e-eliminado.ghtml", 
]

pdfs = ["data/pdfs/APAJO/APAJO_Manual_do_Jogo_Responsavel.pdf","data/pdfs/Antitruste/40265_145_5.pdf","data/pdfs/Antitruste/Lei n.º 17-2022.pdf","data/pdfs/Antitruste/Lei n.º 93-2021_ de 20 de dezembro_ que estabelece o regime geral de proteção de denunciantes de infrações.pdf","data/pdfs/Antitruste/Lei_19_2012-Lei_da_Concorrencia.pdf","data/pdfs/Antitruste/Lei_2023-2018,_20de_205_20de_20junho_20-_20direito_20a_20indemnização_20por_20infração_20ao_20direito_20da_20concorrência.pdf"]

print("Loading documents")
def create_db(source="url", from_loaded_docs=False):
    # Check if db was already created
    if os.path.exists("./chroma_db") and from_loaded_docs:
        print("Loading created")
        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=OpenAIEmbeddings()
        )
    elif source == "url":
        loader = SeleniumURLLoader(urls=urls)
        docs = loader.load()

        print("Loaded documents")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)

        print("Splitted documents")

        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="./chroma_db")
    else:
        documents = []
        for pdf in pdfs:
            loader = PDFPlumberLoader(file_path=pdf)
            documents.extend(loader.load())

        print("Loaded documents")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(documents)

        print("Splitted documents")

        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="./chroma_db")
    print("Vectorized documents")
    return vectorstore

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def setup_rag(source="url"):
    vectorstore = create_db(source=source)
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=openai_key)

    rag_chain_from_docs = ( RunnablePassthrough.assign(
        context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)

    return rag_chain_with_source
# Ask rag

def ask_rag(query, debug=False, source="url"):
    rag = setup_rag(source=source)
    print("key", openai_key)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=openai_key)
    if debug:
        responses = {"query": query, "llm": "LLM ANSWER", "rag": "RAG ANSWER"}
        print(responses)
        return responses
    responses = {"query": query, "llm": llm.invoke(query).content, "rag": rag.invoke(query)}
    return responses

# query = ["Quem é o atual presidente da Argentina?",
#          "Quem ganhou o Super Bowl 2024?",
#          "Quem é o jogador novo do Corinthians?",
#          "Quem é o jogador Botafoguense que se contundiu recenteente?",
#          "Qual a formação usada no Fluminense no jogo contra o Madureira?",
#          "Quem é o novo reforço do Fluminense?",
#          "Qual a nova resulução sobre 'saidinhas' de presos?",
#          ]
# for idx, q in enumerate(query):
#     print(f"Query {idx+1}: {q}")
#     print(f"    RAG-Answer > {rag_chain_with_source.invoke(q)}\n")
#     print(f"    GPT-Answer > {llm.invoke(q).content}\n")
    