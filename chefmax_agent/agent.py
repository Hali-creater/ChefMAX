import json
import os
import random
import streamlit as st

class ChefMAX:
    def __init__(self, menu_file, questions_file, restaurant_name="The Golden Spoon"):
        self.restaurant_name = restaurant_name
        self.menu = self.load_json(menu_file)
        self.questions = self.load_json(questions_file)
        self.order = []
        self.conversation_state = "GREETING"
        self.current_item = None

    def load_json(self, file_path):
        """Loads data from a JSON file."""
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(dir_path, file_path), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def greet(self):
        """Greets the customer and asks about their party size."""
        self.conversation_state = "GREETING"
        return f"Welcome to {self.restaurant_name}! {self._get_question('ARRIVAL & SEATING')}"

    def _get_question(self, category):
        """Gets a random question from the specified category."""
        if category in self.questions and self.questions[category]:
            return random.choice(self.questions[category])
        return "What else can I get for you?"

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
            if item.get("mods"):
                formatted_order += f" ({', '.join(item['mods'])})\n"
            else:
                formatted_order += "\n"
        return formatted_order

    def handle_input(self, user_input):
        """Handles the user's input based on a more flexible conversation state."""
        user_input = user_input.lower()
        response = ""

        if self.conversation_state == "GREETING":
            # Acknowledge the user's response and ask about allergies.
            self.conversation_state = "ALLERGY_CHECK"
            response = f"Perfect, thank you. {self._get_question('ALLERGY_CHECK')}"

        elif self.conversation_state == "ALLERGY_CHECK":
            # Acknowledge the allergy information and ask for drinks/starters.
            self.conversation_state = "TAKING_ORDER"
            response = f"Thank you for letting me know. {self._get_question('DRINKS & STARTERS')}"

        elif self.conversation_state == "TAKING_ORDER":
            if "that's all" in user_input or "that is all" in user_input:
                if not self.order:
                    response = "Of course. Are you ready to order your main course whenever you are?"
                else:
                    self.conversation_state = "CONFIRMING_ORDER"
                    response = self._format_order() + "\nDoes this look correct?"
            else:
                item = self._find_item(user_input)
                if item:
                    self.current_item = item
                    self.order.append({"name": item["name"], "mods": []})
                    if item.get("questions"):
                        self.conversation_state = "CUSTOMIZING_ITEM"
                        response = item["questions"][0]
                    else:
                        self.conversation_state = "CONFIRMING_ITEM_ADD"
                        response = f"Excellent choice. The {item['name']} is superb. Would you like to add that to your order?"
                else:
                    response = f"I'm sorry, I couldn't find '{user_input}' on the menu. {self._get_question('MAIN ORDER')}"

        elif self.conversation_state == "CUSTOMIZING_ITEM":
            self.order[-1]["mods"].append(user_input)
            current_question_index = len(self.order[-1]["mods"])
            if self.current_item and current_question_index < len(self.current_item.get("questions", [])):
                response = self.current_item["questions"][current_question_index]
            else:
                self.conversation_state = "CONFIRMING_ITEM_ADD"
                mods = ', '.join(self.order[-1]['mods'])
                response = f"Got it. So that's the {self.current_item['name']} with {mods}. Shall I add that to your order?"

        elif self.conversation_state == "CONFIRMING_ITEM_ADD":
            if "yes" in user_input:
                self.conversation_state = "TAKING_ORDER"
                response = f"Item added. {self._get_question('MAIN ORDER')}"
            else:
                self.order.pop()
                self.conversation_state = "TAKING_ORDER"
                response = f"No problem. Let's try something else. What can I get for you?"

        elif self.conversation_state == "CONFIRMING_ORDER":
            if "yes" in user_input or "that's correct" in user_input:
                self.conversation_state = "ORDER_COMPLETE"
                response = f"Excellent. I'll get that order in. {self._get_question('MEAL SERVICE')}"
            else:
                # For simplicity, we'll restart the order if it's wrong.
                self.order = []
                self.conversation_state = "TAKING_ORDER"
                response = "My apologies. Let's correct that. What would you like to order?"

        elif self.conversation_state == "ORDER_COMPLETE":
            self.conversation_state = "DESSERT"
            response = self._get_question("DESSERT & AFTER")

        elif self.conversation_state == "DESSERT":
            self.conversation_state = "PAYMENT"
            response = self._get_question("PAYMENT & CLOSING")

        elif self.conversation_state == "PAYMENT":
            self.conversation_state = "END"
            response = "Thank you for dining with us! Have a wonderful day."

        else:
            # Fallback for any unknown state
            self.conversation_state = "GREETING"
            response = "I seem to have gotten confused. Let's start over. Welcome!"

        return response


st.set_page_config(page_title="ChefMAX - Your Personal Dining Assistant")
st.title("ChefMAX - Your Personal Dining Assistant")

# Initialize the agent and conversation history in the session state
if 'agent' not in st.session_state:
    st.session_state.agent = ChefMAX(menu_file="menu.json", questions_file="questions.json")
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
