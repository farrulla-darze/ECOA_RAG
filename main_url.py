# from model import Database
from model import WebDatabase
from view import *
from controller import ChatController


if __name__ == "__main__":
    # Initialize MVC components
    model = WebDatabase()
    view = ChatURLView()
    controller = ChatController(model, view)

    # Run the chat interface
    controller.run()
    # view.display()