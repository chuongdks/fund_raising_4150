import tkinter as tk
from tkinter import messagebox
from FundRaiseLIB import LIB_donor
from .GUI_core import MainWindow

class DonorDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = LIB_donor.DonorManager() # LIB initialization
        
        tk.Label(self, text="Donor Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Make a New Donation", font=("Arial", 14, "underline")).pack(pady=10)
        
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # Fund Selection setup 
        tk.Label(form_frame, text="Select Fund:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.funds_data = []
        self.fund_descriptions = []
        self.fund_id_map = {}
        
        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Active Funds...")

        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Active Funds...'])
        self.fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Donation Amount
        tk.Label(form_frame, text="Donation Amount ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # Anonymity Option
        tk.Label(form_frame, text="Donate Anonymously:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.is_anonymous_var = tk.BooleanVar(self)
        tk.Checkbutton(form_frame, variable=self.is_anonymous_var).grid(row=2, column=1, padx=5, pady=5, sticky='w')
        tk.Button(form_frame, text="Submit Donation", command=self.submit_donation, bg='blue', fg='white').grid(row=3, columnspan=2, pady=15)
        
        self.load_funds()

    def load_funds(self):
        """Fetches and populates the fund selection dropdown using LIB."""
        self.funds_data = self.manager.get_active_funds_list() # LIB call
        self.fund_descriptions = [data[1] for data in self.funds_data]
        self.fund_id_map = {data[1]: data[0] for data in self.funds_data}

        menu = self.fund_menu.children['menu']
        menu.delete(0, "end")

        if not self.fund_descriptions:
            self.fund_var.set("No Active Funds Available")
            menu.add_command(label="No Active Funds Available")
            return
            
        for fund_desc in self.fund_descriptions:
            menu.add_command(label=fund_desc, command=tk._setit(self.fund_var, fund_desc))

        self.fund_var.set(self.fund_descriptions[0])        

    def submit_donation(self):
        if not self.user_id:
            messagebox.showerror("Error", "Donor ID is missing. Please log in again.")
            return

        fund_description = self.fund_var.get()
        donation_amount_str = self.amount_entry.get()
        is_anonymous = self.is_anonymous_var.get()
        donor_user_id = self.user_id
        
        # DELEGATE to LIB layer
        success, message = self.manager.submit_donation(
            fund_description, donation_amount_str, is_anonymous, self.fund_id_map, self.user_id
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.amount_entry.delete(0, tk.END)
            self.is_anonymous_var.set(False)
            self.controller.show_frame(MainWindow)
        else:
            messagebox.showerror("Error", message)