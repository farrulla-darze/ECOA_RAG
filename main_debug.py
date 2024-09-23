# from model import Database
from model import WebDatabase, DocumentDatabase
from view import *
from controller import ChatController


if __name__ == "__main__":
    # Initialize MVC components
    model = DocumentDatabase()
    view = ChatView()
    controller = ChatController(model, view)

    # Run the chat interface
    controller.run(debug=True)
    # view.display()