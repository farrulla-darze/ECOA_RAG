from model import Database
from view import *
from controller import ChatController


if __name__ == "__main__":
    # Initialize MVC components
    model = Database()
    view = ChatView()
    controller = ChatController(model, view)

    # Run the chat interface
    controller.run()
    # view.display()