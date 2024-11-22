import tkinter as tk
from tkinter import messagebox
import os
import time
import hashlib


class Authentication:
    def __init__(self):
        self.salt = "salt and pepper"  # Static salt for simplicity, could be more sophisticated

    def encrypt_password(self, password):
        return hashlib.sha256((password + self.salt).encode()).hexdigest()

    def encrypt_payment_info(self, card_info):
        # Simple encryption for demonstration (hashing card info)
        return hashlib.sha256((card_info + self.salt).encode()).hexdigest()


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
    def __init__(self, order_id, customer):
        self.order_id = order_id
        self.customer = customer
        self.burgers = []
        self.status = 'Pending'

    def confirm_order(self):
        # Confirm the order
        self.status = 'Confirmed'
    
    def add_burger(self, burger):
        self.burgers.append(burger)

    def get_total_order_price(self):
        total_price = sum(burger.get_total_price() for burger in self.burgers)
        return total_price

    def store_order(self, filename, payment_info=None):
        # Store the order in a text file
        with open(filename, 'w') as file:
            file.write(f"Burger Order for Customer ID {self.customer.user_id}\n")
            for idx, burger in enumerate(self.burgers, start=1):
                file.write(f"\nBurger {idx}:\n")
                file.write(f"Bun: {burger.bun}\n")
                file.write(f"Cheese: {burger.cheese}\n")
                file.write(f"Patties: {burger.patty}\n")
                file.write(f"Grilled Onion: {burger.griled_onion}\n")
                file.write(f"Raw Onion: {burger.raw_onion}\n")
                file.write(f"Pickle: {burger.pickle}\n")
                file.write(f"Lettuce: {burger.lettuce}\n")
                file.write(f"Spread: {burger.spread}\n")
                file.write(f"Tomato: {burger.tomato}\n")
                file.write(f"Price: ${burger.get_total_price():.2f}\n")
            file.write(f"\nTotal Order Price: ${self.get_total_order_price():.2f}\n")
            if payment_info:
                file.write(f"\nPayment Info (Encrypted): {payment_info}\n")


class Payment:
    def __init__(self, root, kiosk_app, order, authentication):
        self.root = root
        self.kiosk_app = kiosk_app
        self.order = order
        self.authentication = authentication
        self.create_payment_page()

    def create_payment_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Enter Card Information:").grid(row=0, column=0, columnspan=2)

        tk.Label(self.root, text="Cardholder Name:").grid(row=1, column=0)
        self.card_name_entry = tk.Entry(self.root)
        self.card_name_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Card Number:").grid(row=2, column=0)
        self.card_number_entry = tk.Entry(self.root)
        self.card_number_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Security Number:").grid(row=3, column=0)
        self.card_security_entry = tk.Entry(self.root)
        self.card_security_entry.grid(row=3, column=1)

        tk.Button(self.root, text="Pay and Place Order", command=self.confirm_order).grid(row=4, column=0, columnspan=2)
        tk.Button(self.root, text="Back", command=self.kiosk_app.create_customize_widgets).grid(row=5, column=0, columnspan=2)

    def confirm_order(self):
        card_name = self.card_name_entry.get()
        card_number = self.card_number_entry.get()
        security_number = self.card_security_entry.get()

        if len(card_number) != 16 or not card_number.isdigit() or len(security_number) != 3 or not security_number.isdigit():
            messagebox.showerror("Error", "Invalid card details. Please check again.")
            return

        payment_info = f"Card Name: {card_name}, Card Number: {card_number}, Security Number: {security_number}"
        encrypted_payment_info = self.authentication.encrypt_payment_info(payment_info)

        filename = f"{time.strftime('%Y%m%d%H%M%S')}_{self.order.customer.user_id}.txt"
        
        self.order.confirm_order()
        self.order.store_order(filename, encrypted_payment_info)

        messagebox.showinfo("Order Confirmed", f"Your order number {self.order.order_id} has been confirmed successfully!")
        self.kiosk_app.increment_order_number()  # Increment order number
        self.kiosk_app.burger = None
        self.kiosk_app.burgers = None
        self.kiosk_app.create_order_widgets()


class AdminPanel:
    def __init__(self, root, kiosk_app):
        self.root = root
        self.kiosk_app = kiosk_app
        self.create_admin_widgets()

    def create_admin_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Admin Panel: Order List").grid(row=0, column=0, columnspan=2)
        
        # Create a scrollable frame for the order list
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        for file in os.listdir():
            if file.endswith('.txt') and file[:14].isdigit() and not file.startswith('preferred_'):
                tk.Label(scrollable_frame, text=file).grid(row=row, column=0, sticky="w")
                tk.Button(scrollable_frame, text="View", command=lambda f=file: self.view_order(f)).grid(row=row, column=1)
                row += 1

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def view_order(self, filename):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a scrollable frame for the order details
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        with open(filename, 'r') as file:
            order_details = file.read()
        tk.Label(scrollable_frame, text=order_details).pack(pady=10)
        tk.Button(scrollable_frame, text="Confirm", command=lambda: self.confirm_accept_order(filename)).pack(pady=10)
        tk.Button(scrollable_frame, text="Back", command=self.create_admin_widgets).pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def confirm_accept_order(self, filename):
        os.remove(filename)
        messagebox.showinfo("Order Accepted", f"Order {filename} has been accepted and removed.")
        self.create_admin_widgets()


class Customer:
    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password


class KioskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("In-N-Out Kiosk System")
        self.burger = None
        self.customer = None
        self.order_number = 1
        self.order = None
        self.authentication = Authentication()
        self.create_login_widgets()
        

    # Authentication(sign in, sign up)
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
        tk.Button(self.root, text="Back", command=self.create_login_widgets).grid(row=5, column=0, columnspan=2)

    def sign_up(self):
        user_id = self.signup_user_id_entry.get()
        password = self.signup_password_entry.get()
        confirm_password = self.signup_confirm_password_entry.get()

        if "+" in user_id:
            self.signup_error_label.config(text="User ID cannot contain '+' character.")
            return

        if password != confirm_password:
            self.signup_error_label.config(text="Passwords do not match.")
            return

        # Check if user already exists
        if os.path.exists(f"{user_id}.txt"):
            self.signup_error_label.config(text="User ID already exists. Please choose a different ID.")
            return

        # Save user credentials (encrypted)
        encrypted_password = self.authentication.encrypt_password(password)
        with open(f"{user_id}.txt", 'w') as file:
            file.write(encrypted_password)

        messagebox.showinfo("Sign Up Successful", "Account created successfully!")
        self.create_login_widgets()

    def sign_in(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()

        if user_id == "admin" and password == "admin":
            AdminPanel(self.root, self)
            return

        if not os.path.exists(f"{user_id}.txt"):
            messagebox.showerror("Error", "User ID not found.")
            return

        with open(f"{user_id}.txt", 'r') as file:
            stored_password = file.read().strip()

        if self.authentication.encrypt_password(password) != stored_password:
            messagebox.showerror("Error", "Incorrect password.")
            return

        self.customer = Customer(user_id, password)
        self.order = Order(order_id=self.order_number, customer=self.customer)
        self.create_order_widgets()

    # 1. Selection Customize or Load Preferred Order        
    def create_order_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Button(self.root, text="Customize Burger", command=self.create_customize_widgets).grid(row=0, column=0, columnspan=2)
        tk.Button(self.root, text="Load Preferred Order", command=self.load_prefer_order).grid(row=1, column=0, columnspan=2)
        tk.Button(self.root, text="Back", command=self.create_login_widgets).grid(row=2, column=0, columnspan=2)

    def load_prefer_order(self):
        prefer_filename = f"{self.customer.user_id}_prefer.txt"
        if os.path.exists(prefer_filename):
            with open(prefer_filename, 'r') as file:
                config = eval(file.read())
            self.create_customize_widgets()
            self.apply_preset(config)
        else:
            messagebox.showerror("Error", "No preferred order found.")

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
            ("Tomato:", 'tomato', list(range(0, 6)), tk.IntVar(value=1))
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
            ("Ham Burger", {'bun': 'medium', 'cheese': 0, 'patty': 1, 'pickle': 3, 'lettuce': 3, 'spread': 3, 'griled_onion': 0, 'raw_onion': 1, 'tomato': 1}),
            ("Double Double", {'bun': 'medium', 'cheese': 2, 'patty': 2, 'pickle': 3, 'lettuce': 3, 'spread': 3, 'griled_onion': 0, 'raw_onion': 1, 'tomato': 1}),
            ("Cheese Burger", {'bun': 'medium', 'cheese': 1, 'patty': 1, 'pickle': 3, 'lettuce': 3, 'spread': 3, 'griled_onion': 0, 'raw_onion': 1, 'tomato': 1})
        ]

        for preset, config in presets:
            btn = tk.Button(preset_frame, text=preset, command=lambda c=config: self.apply_preset(c),
                            bg='red', fg='white', activebackground='yellow', activeforeground='red')
            btn.pack(fill=tk.X, pady=5)
            
        # Order button
        tk.Button(self.root, text="Order", command=self.display_order_summary).grid(row=len(ingredients), column=0, columnspan=2)
        tk.Button(self.root, text="Back", command=self.reset_and_back_to_order_widgets).grid(row=len(ingredients) + 1, column=0, columnspan=2)
        tk.Button(self.root, text="Save Preferred Order", command=self.save_preferred_order).grid(row=len(ingredients) + 2, column=0, columnspan=2)
    
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
        setattr(self.burger, var_name, value)
        self.update_button_color(frame, value)

    def update_button_color(self, frame, selected_value):
        for widget in frame.winfo_children():
            if widget.cget('text') == str(selected_value):
                widget.config(bg='lightblue')
            else:
                widget.config(bg='lightgray')

    def reset_and_back_to_order_widgets(self):
        self.burger = None
        self.create_order_widgets()

    def save_preferred_order(self):
        config = {
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
        prefer_filename = f"{self.customer.user_id}_prefer.txt"
        # Append to the existing preferences file or create a new one if it doesn't exist
        if os.path.exists(prefer_filename):
            with open(prefer_filename, 'r') as file:
                existing_config = eval(file.read())
                existing_config.update(config)
            with open(prefer_filename, 'w') as file:
                file.write(str(existing_config))
        else:
            with open(prefer_filename, 'w') as file:
                file.write(str(config))
        messagebox.showinfo("Preferred Order Saved", "Your preferred order has been saved successfully!")

    def display_order_summary(self):
        self.order.add_burger(self.burger)  # Add current burger to the order
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a scrollable frame for the order summary
        canvas = tk.Canvas(self.root)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Display the summary of all burgers in the order
        summary_text = "Burger Order Summary:\n\n"
        for idx, burger in enumerate(self.order.burgers, start=1):
            summary_text += f"Burger {idx}:\n"
            attributes = [
                ("Bun", burger.bun),
                ("Cheese", burger.cheese),
                ("Patties", burger.patty),
                ("Grilled Onion", burger.griled_onion),
                ("Raw Onion", burger.raw_onion),
                ("Pickle", burger.pickle),
                ("Lettuce", burger.lettuce),
                ("Spread", burger.spread),
                ("Tomato", burger.tomato)
            ]
            for attr_name, attr_value in attributes:
                summary_text += f"{attr_name}: {attr_value}\n"
            summary_text += f"Total Price: ${burger.get_total_price():.2f}\n\n"

        summary_text += f"Total Order Price: ${self.order.get_total_order_price() * 1.1:.2f}\n"

        tk.Label(scrollable_frame, text=summary_text).pack(pady=10)

        # Add button to order more burgers
        tk.Button(scrollable_frame, text="Order More", command=self.create_customize_widgets).pack(pady=10)
        # Confirm button
        tk.Button(scrollable_frame, text="Confirm Order", command=lambda: Payment(self.root, self, self.order, self.authentication)).pack(pady=10)
        # Back button
        tk.Button(scrollable_frame, text="Back", command=self.reset_and_back_to_order_widgets).pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Order Number
    def get_order_number(self):
        if not os.path.exists("order_number.txt"):
            with open("order_number.txt", 'w') as file:
                file.write("1\n")
            return 1
        else:
            with open("order_number.txt", 'r') as file:
                return int(file.readlines()[-1].strip())

    def increment_order_number(self):
        self.order_number += 1
        with open("order_number.txt", 'a') as file:
            file.write(f"{self.order_number}\n")


# Run the GUI application
if __name__ == "__main__":
    root = tk.Tk()
    app = KioskApp(root)
    root.mainloop()
