import json
import os
import streamlit as st

class ChefMAX:
    def __init__(self, menu_file, restaurant_name="The Golden Spoon"):
        self.restaurant_name = restaurant_name
        self.menu = self.load_menu(menu_file)
        self.order = []
        self.conversation_state = "GATHERING_PARTY_DETAILS"
        self.current_item = None

    def load_menu(self, menu_file):
        """Loads the menu from a JSON file."""
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, menu_file), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def greet(self):
        """Greets the customer and asks about their party size."""
        self.conversation_state = "GATHERING_PARTY_DETAILS"
        return f"Welcome to {self.restaurant_name}! How many in your party today?"

    def _find_item(self, item_name):
        """Finds an item in the menu by name."""
        for category in self.menu.values():
            for item in category:
                if item['name'].lower() in item_name.lower():
                    return item
        return None

    def _format_order(self):
        if not self.order:
            return "You haven't ordered anything yet."

        formatted_order = "Here is your order so far:\n"
        for item in self.order:
            formatted_order += f"- {item['name']}"
            if item["mods"]:
                formatted_order += f" ({', '.join(item['mods'])})\n"
            else:
                formatted_order += "\n"
        return formatted_order

    def handle_input(self, user_input):
        """Handles the user's input based on the conversation state."""
        user_input = user_input.lower()

        if self.conversation_state == "GATHERING_PARTY_DETAILS":
            self.conversation_state = "TAKING_DRINK_ORDER"
            return "Excellent. Can I start you with something to drink? We have a great selection of red wine and craft beer."

        elif self.conversation_state == "TAKING_DRINK_ORDER":
            self.conversation_state = "ALLERGY_CHECK"
            return "Great choice. Now, before we move on to the food, does anyone in your party have any food allergies or dietary restrictions I should inform the chef about?"

        elif self.conversation_state == "ALLERGY_CHECK":
            self.conversation_state = "MENU_INTRODUCTION"
            return "Thank you for letting me know. Are you familiar with our menu, or shall I highlight some favorites?"

        elif self.conversation_state == "MENU_INTRODUCTION":
            if "that's all" in user_input or "that is all" in user_input:
                self.conversation_state = "CONFIRM_ORDER"
                return self._format_order() + "\nDoes that complete your order, or would you like to add anything else?"

            item = self._find_item(user_input)
            if item:
                self.current_item = item
                self.order.append({"name": item["name"], "mods": []})
                if "questions" in item and item["questions"]:
                    self.conversation_state = "ITEM_CUSTOMIZATION"
                    return item["questions"][0]
                else:
                    self.conversation_state = "CONFIRM_ADD_ITEM"
                    return f"Excellent choice. The {item['name']} is superb. Would you like to add that to your order?"
            else:
                return "I'm sorry, I couldn't find that item. Our most popular dishes are the Margherita Pizza and the New York Strip."

        elif self.conversation_state == "ITEM_CUSTOMIZATION":
            self.order[-1]["mods"].append(user_input)
            current_question_index = len(self.order[-1]["mods"])
            if current_question_index < len(self.current_item["questions"]):
                return self.current_item["questions"][current_question_index]
            else:
                 self.conversation_state = "CONFIRM_ADD_ITEM"
                 return f"Got it. So that's the {self.current_item['name']} with {', '.join(self.order[-1]['mods'])}. Shall I add that to your order?"

        elif self.conversation_state == "CONFIRM_ADD_ITEM":
             if "yes" in user_input:
                self.conversation_state = "MENU_INTRODUCTION"
                return "Item added. What else can I get for you? (Say 'that's all' to finish your order)"
             else:
                self.order.pop()
                self.conversation_state = "MENU_INTRODUCTION"
                return "No problem. Let's try something else."

        elif self.conversation_state == "CONFIRM_ORDER":
            if "yes" in user_input or "that's correct" in user_input:
                self.conversation_state = "CLOSING"
                return "Excellent. Would you like to see our dessert menu?"
            else:
                self.conversation_state = "MENU_INTRODUCTION"
                return "My apologies. Let's correct that. What would you like to change?"

        elif self.conversation_state == "CLOSING":
            return "Thank you for your order! It will be ready shortly."

        else:
            return "I'm still learning. How about we start over?"


st.set_page_config(page_title="ChefMAX - Your Personal Dining Assistant")
st.title("ChefMAX - Your Personal Dining Assistant")

# Initialize the agent and conversation history in the session state
if 'agent' not in st.session_state:
    st.session_state.agent = ChefMAX(menu_file="menu.json")
    st.session_state.messages = []
    # Start the conversation with the agent's greeting
    greeting = st.session_state.agent.greet()
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Display the conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("What can I get for you?"):
    # Add user message to the conversation history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get the agent's response
    response = st.session_state.agent.handle_input(prompt)

    # Add the agent's response to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
