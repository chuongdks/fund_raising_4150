import tkinter as tk
from tkinter import messagebox
import webbrowser
from FundRaiseLIB import LIB_admin
from FundRaiseGUI import GUI_core # For frame switching back to MainWindow

class AdminDashboard(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.admin_manager = LIB_admin.AdminManager() # LIB initialization
        
        tk.Label(self, text="🔑 Admin Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)

        tk.Label(self, text="Funds Verification (Pending Admin Action)", font=("Arial", 14, "underline")).pack(pady=10)

        # Frame for the verification form/list
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # 1. Fund Selection Dropdown
        tk.Label(form_frame, text="Select Fund to Verify:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.funds_data = []
        self.fund_descriptions = []
        self.fund_map = {} 

        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Funds...")

        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Funds...'])
        self.fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # 2. Display Proof of Charge Link (Clickable)
        tk.Label(form_frame, text="Proof for Review:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.proof_label_text = tk.StringVar()
        self.proof_label = tk.Label(form_frame, textvariable=self.proof_label_text, fg='blue', cursor="hand2")
        self.proof_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.proof_label.bind("<Button-1>", self.open_proof_link)

        # 3. Action Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=2, columnspan=2, pady=15)
        tk.Button(button_frame, text="✅ Verify Fund", command=self.verify_fund, bg='green', fg='white').pack(side=tk.LEFT, padx=10)
        
        # 4. Bind selection change to update the displayed proof link
        self.fund_var.trace_add("write", lambda *args: self.load_current_proof())
        self.load_funds()

    def load_funds(self):
        """Fetches and populates the fund selection dropdown using LIB layer."""
        # Call LIB to get the list of unverified funds
        self.funds_data = self.admin_manager.get_pending_funds_list()
        
        self.fund_descriptions = []
        self.fund_map = {}

        menu = self.fund_menu.children['menu']
        menu.delete(0, "end")

        if not self.funds_data:
            self.fund_var.set("No Pending Funds to Verify")
            self.proof_label_text.set("")
            menu.add_command(label="No Pending Funds to Verify")
            return

        for fund_id, recipient_name, service_name, amount_needed, proof_of_charge in self.funds_data:
            description = f"ID {fund_id} for {recipient_name} (Service: {service_name}, ${amount_needed:.2f})"
            self.fund_descriptions.append(description)
            self.fund_map[description] = (fund_id, proof_of_charge if proof_of_charge else 'N/A')
            
        for fund_desc in self.fund_descriptions:
            menu.add_command(label=fund_desc, command=tk._setit(self.fund_var, fund_desc))

        self.fund_var.set(self.fund_descriptions[0])
        self.load_current_proof()
        
    def load_current_proof(self):
        """Loads the proof_of_charge for the currently selected fund into the label."""
        selected_desc = self.fund_var.get()
        if selected_desc in self.fund_map:
            fund_id, current_proof = self.fund_map[selected_desc]
            self.proof_label_text.set(current_proof)
        else:
            self.proof_label_text.set("")
            
    def open_proof_link(self, event):
        """Opens the proof link in the user's default web browser (GUI logic)."""
        link = self.proof_label_text.get()
        if link and link not in ('N/A', 'Loading Funds...', ''):
            try:
                webbrowser.open_new_tab(link)
            except Exception as e:
                messagebox.showerror("Browser Error", f"Could not open link: {link}\nError: {e}")
        elif link == 'N/A':
             messagebox.showinfo("No Proof", "No proof of charge has been provided by the service provider yet.")
             
    def verify_fund(self):
        """Handles user action and delegates to BLL."""
        selected_desc = self.fund_var.get()
        
        if selected_desc not in self.fund_map:
            messagebox.showerror("Error", "Please select a valid fund to verify.")
            return

        fund_id, current_proof = self.fund_map[selected_desc]
        
        if current_proof == 'N/A':
            if not messagebox.askyesno("Confirm Verification", "No proof of charge has been provided for this fund. Do you still wish to verify it?"):
                return
        
        # DELEGATE to LIB for verification transaction
        success, message = self.admin_manager.verify_fund(fund_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_funds()
            self.controller.show_frame(GUI_core.MainWindow)
        else:
            messagebox.showerror("Error", message)