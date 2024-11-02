import tkinter as tk
from tkinter import messagebox
import os
import time


class Burger:
    def __init__(self):
        self.bun = 'medium'
        self.cheese = 1
        self.patty = 1
        self.griled_onion = 1
        self.raw_onion = 1
        self.pickle = 1
        self.lettuce = 1
        self.spread = 1
        self.tomato = 1
        self.price = 5.00  # Base price

    def customize_burger(self, bun=None, cheese=None, patty=None, onion=None, pickle=None, lettuce=None, spread=None, tomato=None):
        if bun:
            self.bun = bun
        if cheese:
            self.cheese = cheese
        if patty:
            self.patty = patty
        if onion:
            self.onion = onion
        if pickle:
            self.pickle = pickle
        if lettuce:
            self.lettuce = lettuce
        if spread:
            self.spread = spread
        if tomato:
            self.tomato = tomato

    def get_total_price(self):
        # Basic price calculation based on customization
        self.price = 5.00 + (self.patty - 1) * 1.50
        if self.cheese == 'extra':
            self.price += 0.50
        return self.price


class Order:
    def __init__(self, order_id, customer_id, burger):
        self.order_id = order_id
        self.customer_id = customer_id
        self.burger = burger
        self.status = 'Pending'

    def confirm_order(self):
        # Confirm the order
        self.status = 'Confirmed'

    def store_order(self, filename):
        # Store the order in a text file
        with open(filename, 'w') as file:
            file.write(f"Burger Order for Customer ID {self.customer_id}\n")
            file.write(f"Bun: {self.burger.bun}\n")
            file.write(f"Cheese: {self.burger.cheese}\n")
            file.write(f"Patties: {self.burger.patty}\n")
            file.write(f"Grilled Onion: {self.burger.griled_onion}\n")
            file.write(f"Raw Onion: {self.burger.raw_onion}\n")
            file.write(f"Pickle: {self.burger.pickle}\n")
            file.write(f"Lettuce: {self.burger.lettuce}\n")
            file.write(f"Spread: {self.burger.spread}\n")
            file.write(f"Tomato: {self.burger.tomato}\n")
            file.write(f"Total Price: ${self.burger.get_total_price():.2f}\n")


class KioskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("In-N-Out Kiosk System")
        self.burger = None
        self.customer_id = None
        self.create_login_widgets()

    def create_login_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="User ID:").grid(row=0, column=0)
        self.user_id_entry = tk.Entry(self.root)
        self.user_id_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.root, text="Sign In", command=self.sign_in).grid(row=2, column=0, columnspan=2)
        tk.Button(self.root, text="Sign Up", command=self.create_signup_widgets).grid(row=3, column=0, columnspan=2)
    
    def create_signup_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="User ID:").grid(row=0, column=0)
        self.signup_user_id_entry = tk.Entry(self.root)
        self.signup_user_id_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Password:").grid(row=1, column=0)
        self.signup_password_entry = tk.Entry(self.root, show="*")
        self.signup_password_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Confirm Password:").grid(row=2, column=0)
        self.signup_confirm_password_entry = tk.Entry(self.root, show="*")
        self.signup_confirm_password_entry.grid(row=2, column=1)

        self.signup_error_label = tk.Label(self.root, text="", fg="red")
        self.signup_error_label.grid(row=3, column=0, columnspan=2)

        tk.Button(self.root, text="Submit", command=self.sign_up).grid(row=4, column=0, columnspan=2)
   
    def load_previous_order(self):
        self.create_customize_widgets()
        if hasattr(self, 'previous_order_config'):
            self.apply_preset(self.previous_order_config)

    def create_customize_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.burger = Burger()

        # Ingredients customization details
        ingredients = [
            ("Select Bun Toast Level:", 'bun', ['light', 'medium', 'well-toasted'], tk.StringVar(value='medium')),
            ("Cheese:", 'cheese', list(range(0, 6)), tk.IntVar(value=1)),
            ("Number of Patties:", 'patty', list(range(0, 6)), tk.IntVar(value=1)),
            ("Pickles:", 'pickle', list(range(0, 6)), tk.IntVar(value=1)),
            ("Lettuce:", 'lettuce', list(range(0, 6)), tk.IntVar(value=1)),
            ("Spread:", 'spread', list(range(0, 6)), tk.IntVar(value=1)),
            ("Grilled Onion:", 'griled_onion', list(range(0, 6)), tk.IntVar(value=1)),
            ("Raw Onion:", 'raw_onion', list(range(0, 6)), tk.IntVar(value=1)),
        ]

        for idx, (label_text, var_name, options, var) in enumerate(ingredients):
            tk.Label(self.root, text=label_text).grid(row=idx, column=0)
            frame = tk.Frame(self.root)
            frame.grid(row=idx, column=1)
            setattr(self, f"{var_name}_frame", frame)
            setattr(self, f"{var_name}_var", var)
            for option in options:
                tk.Button(frame, text=str(option), command=lambda b=option, v=var_name, f=frame: self.button_click(b, v, f), bg='lightgray', activebackground='lightblue', relief=tk.RAISED).pack(side=tk.LEFT)

        # Preset buttons frame on the right side
        preset_frame = tk.Frame(self.root)
        preset_frame.grid(row=0, column=2, rowspan=len(ingredients), padx=20)

        presets = [
            ("Ham Burger", {'bun': 'medium', 'cheese': 0, 'patty': 1, 'pickle': 3, 'lettuce': 3, 'spread': 3, 'griled_onion': 0, 'raw_onion': 1}),
            ("Double Double", {'bun': 'medium', 'cheese': 2, 'patty': 2, 'pickle': 3, 'lettuce': 3, 'spread': 3, 'griled_onion': 0, 'raw_onion': 1}),
            ("Cheese Burger", {'bun': 'medium', 'cheese': 1, 'patty': 1, 'pickle': 3, 'lettuce': 3, 'spread': 3, 'griled_onion': 0, 'raw_onion': 1})
        ]

        for preset, config in presets:
            btn = tk.Button(preset_frame, text=preset, command=lambda c=config: self.apply_preset(c),
                            bg='red', fg='white', activebackground='yellow', activeforeground='red')
            btn.pack(fill=tk.X, pady=5)
            
        # Order button
        tk.Button(self.root, text="Order", command=self.place_order).grid(row=len(ingredients), column=0, columnspan=2)
    
    def apply_preset(self, config):
        for key, value in config.items():
            setattr(self.burger, key, value)
            var_name = f"{key}_var"
            if hasattr(self, var_name):
                getattr(self, var_name).set(value)
            frame_name = f"{key}_frame"
            if hasattr(self, frame_name):
                self.button_click(value, key, getattr(self, frame_name))

    def button_click(self, value, var_name, frame):
        getattr(self, f"{var_name}_var").set(value)
        self.update_button_color(frame, value)

    def update_button_color(self, frame, selected_value):
        for widget in frame.winfo_children():
            if widget.cget('text') == str(selected_value):
                widget.config(bg='lightblue')
            else:
                widget.config(bg='lightgray')

    def place_order(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.previous_order_config = {
            'bun': self.burger.bun,
            'cheese': self.burger.cheese,
            'patty': self.burger.patty,
            'griled_onion': self.burger.griled_onion,
            'raw_onion': self.burger.raw_onion,
            'pickle': self.burger.pickle,
            'lettuce': self.burger.lettuce,
            'spread': self.burger.spread,
            'tomato': self.burger.tomato
        }

        # Display the customized burger summary using a loop
        summary_text = "Burger Order Summary:\n\n"
        attributes = [
            ("Bun", self.burger.bun),
            ("Cheese", self.burger.cheese),
            ("Patties", self.burger.patty),
            ("Grilled Onion", self.burger.griled_onion),
            ("Raw Onion", self.burger.raw_onion),
            ("Pickle", self.burger.pickle),
            ("Lettuce", self.burger.lettuce),
            ("Spread", self.burger.spread),
            ("Tomato", self.burger.tomato)
        ]
        for attr_name, attr_value in attributes:
            summary_text += f"{attr_name}: {attr_value}\n"
        summary_text += f"\nTotal Price: ${self.burger.get_total_price():.2f}\n"

        tk.Label(self.root, text=summary_text).grid(row=0, column=0, columnspan=2)

        # Confirm button
        tk.Button(self.root, text="Confirm", command=self.confirm_order).grid(row=1, column=0, columnspan=2)

        # Back button to go back to customization
        tk.Button(self.root, text="Back", command=self.load_previous_order).grid(row=2, column=0, sticky="w")

    def confirm_order(self):
        filename = f"{time.strftime('%Y%m%d%H%M%S')}_{self.customer_id}.txt"
        order = Order(order_id=1, customer_id=self.customer_id, burger=self.burger)
        order.confirm_order()
        order.store_order(filename)
        messagebox.showinfo("Order Confirmed", "Your order has been confirmed successfully!")
        self.create_order_widgets()

    def sign_in(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()

        if user_id == "admin" and password == "asmin":
            self.create_admin_widgets()
            return

        if not os.path.exists(f"{user_id}.txt"):
            messagebox.showerror("Error", "User ID not found.")
            return

        with open(f"{user_id}.txt", 'r') as file:
            stored_password = file.read().strip()

        if password != stored_password:
            messagebox.showerror("Error", "Incorrect password.")
            return

        self.customer_id = user_id
        self.create_order_widgets()

    def create_order_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Button(self.root, text="Customize Burger", command=self.create_customize_widgets).grid(row=0, column=0, columnspan=2)
        tk.Button(self.root, text="Load Preferred Order", command=self.load_previous_order).grid(row=1, column=0, columnspan=2)

    def load_preferred_order(self):
        filename = f"preferred_{self.customer_id}.txt"
        if not os.path.exists(filename):
            messagebox.showinfo("No Preferred Order", "No preferred order found. Please create one.")
            self.create_customize_widgets()
            return

        with open(filename, 'r') as file:
            order_details = file.read()
            messagebox.showinfo("Preferred Order Loaded", order_details)
            self.create_order_widgets()

    def create_admin_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Admin Panel: Order List").grid(row=0, column=0, columnspan=2)
        row = 1
        for file in os.listdir():
            if file.startswith(time.strftime('%Y%m%d')) and file.endswith('.txt') and not file.startswith('preferred_'):
                tk.Label(self.root, text=file).grid(row=row, column=0)
                tk.Button(self.root, text="Accept", command=lambda f=file: self.accept_order(f)).grid(row=row, column=1)
                row += 1

    def accept_order(self, filename):
        os.remove(filename)
        messagebox.showinfo("Order Accepted", f"Order {filename} has been accepted and removed.")
        self.create_admin_widgets()


# Run the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = KioskApp(root)
    root.mainloop()
