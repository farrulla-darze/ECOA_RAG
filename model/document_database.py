from typing import List
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os
from model.database import Database
from dotenv import load_dotenv
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")

class DocumentDatabase(Database):
  
    def format_docs(self, docs: List[Document]):
        return "\n\n".join(doc.page_content for doc in docs)
    

    def _initialize(self, load=True, file_path="data/pdfs", text_splitter=None, loader=None):
        if os.path.exists("./chroma_db") and load:
        
            self.vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=OpenAIEmbeddings()
            )
        else:

            print("Loading documents from PDFs")
            documents_paths = []
            splits = []
            
            # load all pdfs in the directory and subdirectories
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    if file.endswith(".pdf"):
                        file_path = os.path.join(root, file)
                        documents_paths.append(file_path)

            print(f"Found {len(documents_paths)} PDFs")
            i = 0
            for document_path in documents_paths:
                print(f"Processing document {i+1}/{len(documents_paths)}")
                loader = PDFPlumberLoader(file_path=document_path)
                docs = loader.load()

                if text_splitter is None:
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

                splits.extend(text_splitter.split_documents(docs))

                i += 1
            self.vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(), persist_directory="./chroma_db")            
    
    def _setup_rag(self, *args, **kwargs):
        if len(args) > 0:
            chain_params = args[0]
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": chain_params["retriever_k"]}
        )
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

    def ask_rag(self, query, debug=False, *args) -> dict:
        print("args = ",args)
        # kwargs = len(args) > 0
        chain_params = {}
        output_format = "string"
        if len(args) > 0:
            chain_params = args[0]
            if len(args) > 1:
                output_format = args[1]
        rag_chain = self._setup_rag(chain_params)
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=openai_key)
        if debug:
            fake_docs = [Document(page_content="CONTEXT", metadata={"source":"SOURCE"+str(i)}) for i in range(1, chain_params["retriever_k"]+1)]
            responses = {"query": query, "llm": "LLM ANSWER", "rag": {"answer":"RAG ANSWER", "context": fake_docs}} 
            return responses
        if output_format == "stream":
            # Get sources
            # print(rag_chain.invoke(query))
            # sources = rag_chain.invoke(query).metadata["source"]
            sources = []
            context = rag_chain.invoke(query)["context"]
            answer_chain = rag_chain.pick("answer")
            for i in range(len(context)):
                print("Context: ",context[i].metadata)
                sources.append(context[i].metadata["source"])
                if "page" in context[i].metadata:
                    sources[i] += "\n\n Pagina " + str(context[i].metadata["page"])
            responses = {"query": query, "llm_stream": llm.stream(query), "rag_stream": answer_chain.stream(query), "sources": sources}
        else:
            responses = {"query": query, "llm": llm.invoke(query).content, "rag": rag_chain.invoke(query)}
        return responses

