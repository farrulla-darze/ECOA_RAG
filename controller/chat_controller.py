from model.database import Database
from view import ChatView

class ChatController:
    def __init__(self, db: Database, view: ChatView):
        self.db = db
        self.view = view

    def run(self):
        print("Running chat controller")
        last_input = None
        while True:
            user_input = self.view.get_text()
            if user_input != last_input:
                # self.db.add_user_input(user_input)
                responses = self.db.ask_rag(user_input)
                last_input = user_input
                self.view.display(responses=responses)
            else:
                break