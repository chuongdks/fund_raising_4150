import tkinter as tk
from tkinter import messagebox
from FundRaiseLIB import LIB_core


class ProfileWindow(tk.Frame):
    """
    A unified GUI frame for users (Admin, Recipient, Donor, Service)
    to view and edit their common and role-specific profile information.
    """
    def __init__(self, master, controller, user_id=None):
        super().__init__(master)
        self.controller = controller
        # user_id and user_role are set/updated when the frame is raised (in load_profile)
        self.user_id = user_id
        self.user_role = None
        self.pm = LIB_core.ProfileManager() # Profile Manager from BLL

        tk.Label(self, text="👤 Edit Profile", font=("Arial", 18, "bold")).pack(pady=8)

        # --- Top Buttons ---
        top_frame = tk.Frame(self)
        top_frame.pack(pady=6)
        tk.Button(top_frame, text="Save", command=self.save_profile, bg='green', fg='white').pack(side=tk.LEFT, padx=6)
        tk.Button(top_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=6)
        tk.Button(top_frame, text="Logout", command=controller.logout).pack(side=tk.LEFT, padx=6)

        # --- General User Form ---
        form = tk.LabelFrame(self, text="General Information", padx=10, pady=10)
        form.pack(padx=20, pady=10, fill='x')

        tk.Label(form, text="User ID:").grid(row=0, column=0, sticky='e')
        self.user_id_label = tk.Label(form, text="", width=40, anchor='w')
        self.user_id_label.grid(row=0, column=1, sticky='w')

        tk.Label(form, text="Role:").grid(row=1, column=0, sticky='e')
        self.user_role_label = tk.Label(form, text="", width=40, anchor='w')
        self.user_role_label.grid(row=1, column=1, sticky='w')

        tk.Label(form, text="Email (Not Editable):").grid(row=2, column=0, sticky='e')
        self.email_label = tk.Label(form, text="", width=40, anchor='w')
        self.email_label.grid(row=2, column=1, sticky='w')

        tk.Label(form, text="Full Name:").grid(row=3, column=0, sticky='e')
        self.name_entry = tk.Entry(form, width=40)
        self.name_entry.grid(row=3, column=1, sticky='w')

        tk.Label(form, text="Phone Number:").grid(row=4, column=0, sticky='e')
        self.phone_entry = tk.Entry(form, width=40)
        self.phone_entry.grid(row=4, column=1, sticky='w')

        tk.Label(form, text="Address:").grid(row=5, column=0, sticky='e')
        self.address_entry = tk.Entry(form, width=40)
        self.address_entry.grid(row=5, column=1, sticky='w')

        # --- Role-Specific Frame ---
        self.role_frame = tk.LabelFrame(self, text="Role Specific Details", padx=10, pady=10)
        self.role_frame.pack(padx=20, pady=10, fill='x')
        
        # Initialize role-specific fields (for easy reference later)
        self.create_role_specific_fields()
        
        # Password Change section
        self.password_frame = tk.LabelFrame(self, text="Change Password", padx=10, pady=10)
        self.password_frame.pack(padx=20, pady=10, fill='x')
        
        tk.Label(self.password_frame, text="New Password:").grid(row=0, column=0, sticky='e')
        self.new_pass_entry = tk.Entry(self.password_frame, width=40, show='*')
        self.new_pass_entry.grid(row=0, column=1, sticky='w')
        
        tk.Label(self.password_frame, text="Confirm New Password:").grid(row=1, column=0, sticky='e')
        self.confirm_pass_entry = tk.Entry(self.password_frame, width=40, show='*')
        self.confirm_pass_entry.grid(row=1, column=1, sticky='w')
        
        tk.Button(self.password_frame, text="Update Password", command=self.update_password, bg='orange', fg='white').grid(row=2, column=1, sticky='w', pady=5)


    def create_role_specific_fields(self):
        """Creates all possible role-specific input widgets, but hides them initially."""
        
        # Recipient Fields
        self.recipient_contact_label = tk.Label(self.role_frame, text="Contact Email:")
        self.recipient_contact_entry = tk.Entry(self.role_frame, width=40)

        # Donor Fields
        self.donor_anon_var = tk.IntVar()
        self.donor_anon_check = tk.Checkbutton(self.role_frame, text="Default to Anonymous Donation", variable=self.donor_anon_var)
        
        # Service Fields
        self.service_name_label = tk.Label(self.role_frame, text="Service Name:")
        self.service_name_entry = tk.Entry(self.role_frame, width=40)
        self.service_desc_label = tk.Label(self.role_frame, text="Service Description:")
        self.service_desc_entry = tk.Entry(self.role_frame, width=40)
        self.service_tax_label = tk.Label(self.role_frame, text="Tax ID Number:")
        self.service_tax_entry = tk.Entry(self.role_frame, width=40)


    def load_profile(self, user_id, user_role):
        """
        Called when the frame is raised to load the current user's data.
        """
        self.user_id = user_id
        self.user_role = user_role
        
        # Reset general form
        self.user_id_label.config(text=str(user_id))
        self.user_role_label.config(text=user_role)
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)
        self.confirm_pass_entry.delete(0, tk.END)

        # Fetch and populate general info
        user_info, role_info = self.pm.fetch_profile(user_id, user_role)
        
        if user_info:
            self.email_label.config(text=user_info.get('email', ''))
            self.name_entry.insert(0, user_info.get('name', ''))
            self.phone_entry.insert(0, user_info.get('phone_number', ''))
            self.address_entry.insert(0, user_info.get('address', ''))

        # Clear and populate role-specific fields
        self.update_role_fields(role_info)


    def update_role_fields(self, role_specific_profile):
        """Hides previous role fields and displays/populates the current ones."""
        
        # Clear all role_frame children (hide previous role)
        for w in self.role_frame.winfo_children():
            w.grid_forget()

        role = self.user_role
        sp = role_specific_profile # Alias for brevity

        if role == 'Recipient':
            self.recipient_contact_label.grid(row=0, column=0, sticky='e', padx=5, pady=2)
            self.recipient_contact_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            self.recipient_contact_entry.delete(0, tk.END)
            self.recipient_contact_entry.insert(0, sp.get('contact_email', '') if sp else '')

        elif role == 'Donor':
            self.donor_anon_check.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=2)
            # Set the checkbox state
            default_anon = sp.get('is_anonymous_default', False) if sp else False
            self.donor_anon_var.set(1 if default_anon else 0)

        elif role == 'Service':
            self.service_name_label.grid(row=0, column=0, sticky='e', padx=5, pady=2)
            self.service_name_entry.grid(row=0, column=1, sticky='w', padx=5, pady=2)
            self.service_desc_label.grid(row=1, column=0, sticky='e', padx=5, pady=2)
            self.service_desc_entry.grid(row=1, column=1, sticky='w', padx=5, pady=2)
            self.service_tax_label.grid(row=2, column=0, sticky='e', padx=5, pady=2)
            self.service_tax_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)
            
            self.service_name_entry.delete(0, tk.END)
            self.service_name_entry.insert(0, sp.get('service_name', '') if sp else '')
            self.service_desc_entry.delete(0, tk.END)
            self.service_desc_entry.insert(0, sp.get('service_description', '') if sp else '')
            self.service_tax_entry.delete(0, tk.END)
            self.service_tax_entry.insert(0, sp.get('tax_id_number', '') if sp else '')


    def save_profile(self):
        """Gathers data and delegates profile update to the Business Logic Layer."""
        if not self.user_id:
            messagebox.showerror("Error", "No user logged in.")
            return

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()

        role = self.user_role
        role_data = {}
        if role == 'Recipient':
            role_data['contact_email'] = self.recipient_contact_entry.get().strip()
        elif role == 'Donor':
            role_data['is_anonymous_default'] = bool(self.donor_anon_var.get())
        elif role == 'Service':
            role_data['service_name'] = self.service_name_entry.get().strip()
            role_data['service_description'] = self.service_desc_entry.get().strip()
            role_data['tax_id_number'] = self.service_tax_entry.get().strip()

        ok, msg = self.pm.update_profile(
            self.user_id, 
            self.user_role, 
            name=name,
            phone=phone,
            address=address,
            role_data=role_data
        )

        if ok:
            messagebox.showinfo("Success", "Profile updated successfully!")
            self.cancel()
        else:
            messagebox.showerror("Update Failed", msg)

    def update_password(self):
        """Handles the password change request."""
        new_pass = self.new_pass_entry.get()
        confirm_pass = self.confirm_pass_entry.get()

        if not new_pass:
            messagebox.showerror("Error", "Please enter a new password.")
            return
        
        if new_pass != confirm_pass:
            messagebox.showerror("Error", "New password and confirmation do not match.")
            return

        ok, msg = self.pm.update_password(self.user_id, new_pass)
        
        if ok:
            messagebox.showinfo("Success", "Password updated successfully!")
            self.new_pass_entry.delete(0, tk.END)
            self.confirm_pass_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Update Failed", msg)


    def cancel(self):
        """Returns to the user's previous dashboard without saving."""
        # This function relies on the controller knowing the role to switch back
        if self.user_role == 'Admin':
            from FundRaiseGUI.GUI_admin import AdminDashboard
            self.controller.show_frame(AdminDashboard)
        elif self.user_role == 'Recipient':
            from FundRaiseGUI.GUI_recipient import RecipientDashboard
            self.controller.show_frame(RecipientDashboard)
        elif self.user_role == 'Donor':
            from FundRaiseGUI.GUI_donor import DonorDashboard
            self.controller.show_frame(DonorDashboard)
        elif self.user_role == 'Service':
            from FundRaiseGUI.GUI_service import ServiceDashboard
            self.controller.show_frame(ServiceDashboard)
        else:
            # Fallback if somehow role is lost
            from FundRaiseGUI.GUI_core import MainWindow
            self.controller.show_frame(MainWindow)