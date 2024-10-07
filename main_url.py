# from model import Database
from model import WebDatabase
from view import *
from controller import ChatController


if __name__ == "__main__":
    # Initialize MVC components
    urls = ["https://ge.globo.com/futebol/times/palmeiras/noticia/2024/09/24/palmeiras-busca-r-150-milhoes-com-novos-patrocinios-e-nao-deve-ter-crefisa-em-2025.ghtml","https://ge.globo.com/futebol/times/sao-paulo/noticia/2024/09/23/stjd-marca-data-para-julgamento-que-pode-anular-fluminense-x-sao-paulo.ghtml","https://ge.globo.com/futebol/futebol-internacional/futebol-ingles/noticia/2024/09/24/manchester-united-revela-detalhes-de-novo-estadio-para-100-mil-pessoas.ghtml"]
    model = WebDatabase(load=False, urls=urls)
    view = ChatView()
    controller = ChatController(model, view)

    # Run the chat interface
    controller.run()
    # view.display()