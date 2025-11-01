import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  
import json
from datetime import datetime

# Basic Wallet Class
class BasicWallet:
    def __init__(self):
        self.transactions = []  
        self.balance = 0  
        self.categories = ['Salary', 'Entertainment', 'Food', 'Transport']  

    def add_transaction(self, amount, category, transaction_type, description):
        transaction = {
            'amount': amount,
            'type': transaction_type,
            'category': category,
            'description': description,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.transactions.append(transaction)
        self.balance += amount if transaction_type == 'income' else -amount  # Update balance
        return transaction

    def get_balance(self):
        return self.balance

    def get_transaction_history(self):
        return self.transactions

    def save_to_json(self, filename="wallet_data.json"):
        with open(filename, "w") as file:
            json.dump(self.transactions, file)

    def load_from_json(self, filename="wallet_data.json"):
        with open(filename, "r") as file:
            self.transactions = json.load(file)

# Tkinter Window
class WalletApp:
    def __init__(self, root, wallet):
        self.root = root
        self.wallet = wallet
        self.root.title("Personal Wallet - Basic Version")
        self.root.geometry('600x500')

        # Labels
        self.balance_label = tk.Label(root, text=f"Current Balance: ${self.wallet.get_balance():,.2f}", font=('Arial', 16), bg="#0e4b72", fg="white")
        self.balance_label.pack(fill=tk.X)

        # Add Transaction Section
        self.transaction_frame = tk.LabelFrame(root, text="Add Transaction", font=('Arial', 12))
        self.transaction_frame.pack(fill="both", padx=10, pady=10)

        # Amount entry
        self.amount_label = tk.Label(self.transaction_frame, text="Amount:")
        self.amount_label.grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.transaction_frame, width=30)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Type (Income/Expense)
        self.type_label = tk.Label(self.transaction_frame, text="Type:")
        self.type_label.grid(row=1, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar(value="income")
        self.type_menu = tk.OptionMenu(self.transaction_frame, self.type_var, "income", "expense")
        self.type_menu.grid(row=1, column=1, padx=5, pady=5)

        # Category dropdown
        self.category_label = tk.Label(self.transaction_frame, text="Category:")
        self.category_label.grid(row=2, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar(value=self.wallet.categories[0])
        self.category_menu = tk.OptionMenu(self.transaction_frame, self.category_var, *self.wallet.categories)
        self.category_menu.grid(row=2, column=1, padx=5, pady=5)

        # Description entry
        self.description_label = tk.Label(self.transaction_frame, text="Description:")
        self.description_label.grid(row=3, column=0, padx=5, pady=5)
        self.description_entry = tk.Entry(self.transaction_frame, width=30)
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        # Single Button for both Income and Expense
        self.add_transaction_button = tk.Button(root, text="Add Transaction", bg="blue", fg="white", command=self.add_transaction)
        self.add_transaction_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.clear_button = tk.Button(root, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Transaction History Table
        self.history_label = tk.Label(root, text="Transaction History", font=('Arial', 12))
        self.history_label.pack()

        self.history_frame = tk.Frame(root)
        self.history_frame.pack(fill="both", padx=10, pady=5)

        self.history_tree = self.create_tree_view(self.history_frame)
        self.update_history()

    def create_tree_view(self, parent):
        columns = ('#', 'Amount', 'Type', 'Category', 'Description', 'Date')
        tree = ttk.Treeview(parent, columns=columns, show='headings')  # تغییر از tk.Treeview به ttk.Treeview
        tree.heading('#', text='#')
        tree.heading('Amount', text='Amount')
        tree.heading('Type', text='Type')
        tree.heading('Category', text='Category')
        tree.heading('Description', text='Description')
        tree.heading('Date', text='Date')

        tree.pack(fill="both", expand=True)
        return tree

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            description = self.description_entry.get()
            transaction_type = self.type_var.get()

            if amount == 0:
                messagebox.showerror("Input Error", "Amount cannot be zero!")
                return

            transaction = self.wallet.add_transaction(amount, category, transaction_type, description)
            self.update_balance()
            self.update_history()

            # Clear form
            self.clear_form()

            messagebox.showinfo("Transaction Added", f"{transaction_type.capitalize()} of ${amount:,.2f} added successfully.")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid amount.")

    def update_balance(self):
        self.balance_label.config(text=f"Current Balance: ${self.wallet.get_balance():,.2f}")

    def update_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        for index, transaction in enumerate(self.wallet.get_transaction_history()):
            self.history_tree.insert("", "end", values=(
                index + 1,
                f"{transaction['amount']:+,.2f}",
                transaction['type'],
                transaction['category'],
                transaction['description'] or "No description",
                transaction['date']
            ))

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

# Tkinter Main Loop
def main():
    wallet = BasicWallet()
    root = tk.Tk()
    app = WalletApp(root, wallet)
    root.mainloop()

if __name__ == "__main__":
    main()
