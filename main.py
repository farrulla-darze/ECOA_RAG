# from model import Database
from view import *
# from controller import Controller


if __name__ == "__main__":
    # Initialize MVC components
    # model = Model()
    view = ChatView()
    # controller = Controller(model, view)

    # Run the chat interface
    # controller.run()
    view.display()