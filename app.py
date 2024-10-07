# app.py

import streamlit as st

class ChatModel:
    def __init__(self):
        # Initialize messages in session state if not already present
        if 'messages' not in st.session_state:
            st.session_state.messages = []

    def add_message(self, user, message):
        st.session_state.messages.append({"user": user, "message": message})

    def get_messages(self):
        return st.session_state.messages




# --- View ---
class ChatView:

    def __init__(self):
        st.title("Simple Chat Interface")
        self.user_input = st.text_input("Type your message here:", "")


    def display_chat(self, messages):

        # Display all messages
        for msg in messages:
            if msg['user'] == 'User':
                print("reading ",msg)
                st.write(f"**You:** {msg['message']}")
            else:
                print("reading ",msg)
                st.write(f"**Bot:** {msg['message']}")

        # Input for the user's message
        # self.user_input = st.text_input("Type your message here:", "")
        return self.user_input

    def get_message(self):
        return self.user_input

# --- Controller ---
class ChatController:
    def __init__(self, model: ChatModel, view: ChatView):
        self.model = model
        self.view = view

    def run(self):
        
        user_input = self.view.get_message()
        print(user_input)
        print("display list of messages", self.model.get_messages())
        if user_input:
            # Update model with user's message
            self.model.add_message("User", user_input)
            print("display list of messages", self.model.get_messages())

            # Simple bot response logic
            bot_response = f"Echo: {user_input}"
            self.model.add_message("Bot", bot_response)

            self.view.display_chat(self.model.get_messages())


if __name__ == "__main__":
    # Initialize MVC components
    model = ChatModel()
    view = ChatView()
    controller = ChatController(model, view)

    # Run the chat interface
    controller.run()
