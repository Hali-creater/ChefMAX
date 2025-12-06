import json

class ChefMAX:
    def __init__(self, menu_file, restaurant_name="The Golden Spoon"):
        self.restaurant_name = restaurant_name
        self.menu = self.load_menu(menu_file)
        self.order = []
        self.conversation_state = "welcoming"

    def load_menu(self, menu_file):
        """Loads the menu from a JSON file."""
        try:
            with open(menu_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def greet(self):
        """Greets the customer and asks about their dining preference."""
        self.conversation_state = "welcoming"
        return (f"Welcome to {self.restaurant_name}! I'm ChefMAX, your dining assistant. "
                "I'm here to help you explore our menu and craft your perfect order. "
                "Are you dining in with us today, or planning a pickup/delivery?")

    def _find_item(self, item_name):
        """Finds an item in the menu by name."""
        for category in self.menu.values():
            for item in category:
                if item['name'].lower() == item_name.lower():
                    return item
        return None

    def suggest_pairing(self, item_name):
        """Suggests a drink pairing for a given item."""
        item = self._find_item(item_name)
        if not item:
            return "I'm sorry, I couldn't find that item."

        # Find a drink that pairs with this item
        for drink in self.menu.get("drinks", []):
            if item_name in drink.get("pairings", []):
                return (f"The {item_name} pairs beautifully with our {drink['name']}. "
                        f"The {drink['description']} would be an excellent complement. Shall I add one to your order?")
        return "While we don't have a specific pairing for that, our sommelier recommends a versatile wine."


    def get_dietary_options(self, dietary_need):
        """Returns a list of menu items that meet a specific dietary need."""
        options = []
        for category in self.menu.values():
            for item in category:
                if dietary_need.lower() in item.get("dietary", []):
                    options.append(item['name'])
        if options:
            return f"For {dietary_need} options, we have: {', '.join(options)}."
        return f"I'm sorry, we don't have any specific {dietary_need} options listed."

    def handle_input(self, user_input):
        """Handles the user's input based on the conversation state."""
        user_input = user_input.lower()
        if self.conversation_state == "welcoming":
            self.conversation_state = "discovery"
            return "Excellent! Do you have any dietary preferences I should know about, or are you ready to explore the menu?"

        elif self.conversation_state == "discovery":
            if "gluten-free" in user_input or "gluten free" in user_input:
                return self.get_dietary_options("gluten_free")
            elif "vegetarian" in user_input:
                return self.get_dietary_options("vegetarian")
            elif "margherita pizza" in user_input: # example of ordering an item
                self.order.append("Margherita Pizza")
                self.conversation_state = "upsell"
                return self.suggest_pairing("Margherita Pizza")
            else:
                return "Our most beloved dishes are the Margherita Pizza and the Grilled Salmon. Can I tell you more about either?"

        elif self.conversation_state == "upsell":
             if "yes" in user_input:
                # In a real scenario, we'd find out which drink was suggested and add it.
                self.order.append("Red Wine")
                self.conversation_state = "closing"
                return "Excellent choice! Is there anything else I can get for you?"
             else:
                self.conversation_state = "closing"
                return "No problem. Will there be anything else?"

        else:
            return "I'm still learning. How about we start over?"

def main():
    """A simple command-line interface for ChefMAX."""
    agent = ChefMAX("chefmax_agent/menu.json")
    print(agent.greet())

    while True:
        user_input = input("> ")
        if user_input.lower() in ["exit", "quit"]:
            print("Thank you for visiting!")
            break
        response = agent.handle_input(user_input)
        print(response)

if __name__ == "__main__":
    main()
