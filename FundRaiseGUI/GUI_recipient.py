import tkinter as tk
from tkinter import messagebox
from FundRaiseLIB.LIB_recipient import RecipientManager
from .GUI_core import MainWindow

class RecipientDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        self.manager = RecipientManager() # BLL initialization
        
        tk.Label(self, text="Recipient Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Create New Fundraising Goal (Funds Needed)", font=("Arial", 14, "underline")).pack(pady=10)
        
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        tk.Label(form_frame, text="Service Provider:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.services_data = self.manager.get_services_data() # LIB call
        self.service_names = [name for id, name in self.services_data]
        self.service_map = {name: id for id, name in self.services_data}

        self.service_var = tk.StringVar(self)
        if self.service_names:
            self.service_var.set(self.service_names[0])
        else:
            self.service_var.set("No Services Available")

        # Ensure OptionMenu always receives at least one value. If the
        # services list is empty, provide a placeholder option to avoid
        # TypeError from tkinter.OptionMenu
        initial_options = self.service_names if self.service_names else ["No Services Available"]
        service_menu = tk.OptionMenu(form_frame, self.service_var, *initial_options)
        service_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(form_frame, text="Amount Needed ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Label(form_frame, text="Proof of Charge (URL):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.proof_entry = tk.Entry(form_frame, width=20)
        self.proof_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        tk.Button(form_frame, text="Submit Fund Request", command=self.create_fund, bg='green', fg='white').grid(row=3, columnspan=2, pady=15)
        
    def create_fund(self):
        if not self.user_id:
            messagebox.showerror("Error", "Recipient ID is missing. Please log in again.")
            return

        service_name = self.service_var.get()
        amount_needed_str = self.amount_entry.get()
        proof_of_charge = self.proof_entry.get()
        recipient_id = self.user_id
        
        # DELEGATE to LIB layer
        success, message = self.manager.create_fund(
            self.user_id, service_name, amount_needed_str, proof_of_charge, self.service_map
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.amount_entry.delete(0, tk.END)
            self.proof_entry.delete(0, tk.END)
            self.controller.show_frame(MainWindow)
        else:
            # LIB handles identifying Validation vs. Database errors
            messagebox.showerror("Error", message)