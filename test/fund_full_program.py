import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import webbrowser   # for the admin class to open url link if needed

# --- 1. Database Configuration (Customize this) ---
DB_CONFIG = {
    'user': 'root',             # <--- CHANGE THIS
    'password': 'Chuck!2345',   # <--- AND THIS TOO
    'host': '127.0.0.1',
    'database': 'fundraising_db'
}

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        # NOTE: Using print/sys.stderr here to avoid GUI error before main loop starts
        print(f"Error connecting to MySQL: {err}") 
        return None

# --- PUT UR DATABASE QUERY FUNCTIONS HERE ---

# Fetches key information about all FundsNeeded.
def fetch_funds_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS Recipient,
            s.service_name AS Service,
            f.amount_needed,
            f.amount_raised,
            f.is_fully_funded
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Services s ON f.service_id = s.user_id
        ORDER BY f.fund_id DESC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

# Fetches key information about recent Donations
def fetch_donations_data():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            d.donation_id,
            d.fund_id,
            u_don.name AS Donor,
            d.donation_amount,
            d.donation_date
        FROM Donations d
        LEFT JOIN Donors r ON d.donor_id = r.user_id
        LEFT JOIN Users u_don ON r.user_id = u_don.user_id
        ORDER BY d.donation_date DESC
        LIMIT 10; -- Show 10 recent donations
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

#  Fetches all Service IDs and Names for the dropdown
def fetch_services():

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, service_name FROM Services"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        # Returns a list of (user_id, service_name) tuples
        return data
    return []

# Fetches active (verified and not fully funded) funds for donors.
# Returns list of (fund_id, description, amount_needed, amount_raised, recipient_name).
def fetch_active_funds():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            CONCAT('Fund for ', u_rec.name, ' (ID: ', f.fund_id, ') - Needed: $', (f.amount_needed - f.amount_raised)) AS fund_description,
            f.amount_needed,
            f.amount_raised,
            u_rec.name
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        WHERE f.is_verified = TRUE AND f.is_fully_funded = FALSE
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []


# Fetches all FundsNeeded records associated with the logged-in service provider.
# Returns list of (fund_id, recipient_name, amount_needed, proof_of_charge).
def fetch_service_funds(service_user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS RecipientName,
            f.amount_needed,
            f.proof_of_charge
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        WHERE f.service_id = %s
        ORDER BY f.fund_id DESC;
        """
        cursor.execute(query, (service_user_id,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

# Fetches FundsNeeded records that are not yet verified (is_verified = FALSE).
# Returns list of (fund_id, recipient_name, service_name, amount_needed, proof_of_charge).
def fetch_unverified_funds():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS RecipientName,
            s.service_name AS ServiceName,
            f.amount_needed,
            f.proof_of_charge
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Services s ON f.service_id = s.user_id
        WHERE f.is_verified = FALSE
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

# --- 2. Core Authentication/Role Functions (Simplified Placeholders) ---

def authenticate_user(email, password):
    """Checks credentials and returns (user_id, user_type) if valid."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, user_type FROM Users WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (email, password)) # WARNING: Use proper hashing in production!
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result if result else (None, None)
    return (None, None)

# --- 3. Role-Specific Dashboard Frames (Simplified) ---
# ... (AdminDashboard and RecipientDashboard classes remain the same for now) ...

import webbrowser # <-- Make sure to add this import at the top of your file!

class AdminDashboard(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

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
        self.fund_map = {} # Maps description to (fund_id, current_proof)

        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Funds...")

        # Create OptionMenu
        self.fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Funds...'])
        self.fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # 2. Display Proof of Charge Link (Clickable)
        tk.Label(form_frame, text="Proof for Review:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.proof_label_text = tk.StringVar()
        # Set cursor to indicate link and use blue color
        self.proof_label = tk.Label(form_frame, textvariable=self.proof_label_text, fg='blue', cursor="hand2")
        self.proof_label.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.proof_label.bind("<Button-1>", self.open_proof_link)

        # 3. Action Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=2, columnspan=2, pady=15)
        
        tk.Button(button_frame, text="✅ Verify Fund", command=self.verify_fund, bg='green', fg='white').pack(side=tk.LEFT, padx=10)
        
        # 4. Bind selection change to update the displayed proof link
        self.fund_var.trace_add("write", lambda *args: self.load_current_proof())
        
        # Initial data load (will be triggered again by MainApp.show_frame)
        self.load_funds()

    def load_funds(self):
        """Fetches and populates the fund selection dropdown with unverified funds."""
        self.funds_data = fetch_unverified_funds()
        
        self.fund_descriptions = []
        self.fund_map = {}

        # Reset OptionMenu items 
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
            
        # Repopulate the OptionMenu
        for fund_desc in self.fund_descriptions:
            menu.add_command(label=fund_desc, command=tk._setit(self.fund_var, fund_desc))

        # Set default value and load the initial proof
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
        """Opens the proof link in the user's default web browser."""
        link = self.proof_label_text.get()
        if link and link not in ('N/A', 'Loading Funds...', ''):
            try:
                webbrowser.open_new_tab(link)
            except Exception as e:
                messagebox.showerror("Browser Error", f"Could not open link: {link}\nError: {e}")
        elif link == 'N/A':
             messagebox.showinfo("No Proof", "No proof of charge has been provided by the service provider yet.")

    def verify_fund(self):
        """Updates the selected FundsNeeded record to set is_verified = TRUE."""
        selected_desc = self.fund_var.get()
        
        if selected_desc not in self.fund_map:
            messagebox.showerror("Error", "Please select a valid fund to verify.")
            return

        fund_id, current_proof = self.fund_map[selected_desc]
        
        # Admin can choose to verify even without proof, but we ask for confirmation
        if current_proof == 'N/A':
            if not messagebox.askyesno("Confirm Verification", "No proof of charge has been provided for this fund. Do you still wish to verify it?"):
                return
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Set is_verified = TRUE
                query = "UPDATE FundsNeeded SET is_verified = TRUE WHERE fund_id = %s"
                cursor.execute(query, (fund_id,))
                conn.commit()
                messagebox.showinfo("Success", f"Fund ID {fund_id} has been successfully verified! It is now active for donations.")
                
                # Reload the list to remove the newly verified fund and refresh the main data view
                self.load_funds()
                self.controller.show_frame(MainWindow) 
                
            except mysql.connector.Error as err:
                conn.rollback()
                messagebox.showerror("Database Error", f"Failed to verify fund: {err}")
            finally:
                cursor.close()
                conn.close()

class RecipientDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        
        tk.Label(self, text="💵 Recipient Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Create New Fundraising Goal (Funds Needed)", font=("Arial", 14, "underline")).pack(pady=10)
        
        # Frame for the creation form
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # --- Form Fields ---
        
        # 1. Service Selection
        tk.Label(form_frame, text="Service Provider:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.services_data = fetch_services()
        self.service_names = [name for id, name in self.services_data]
        self.service_map = {name: id for id, name in self.services_data}
        
        self.service_var = tk.StringVar(self)
        if self.service_names:
            self.service_var.set(self.service_names[0]) # Default to the first service
        else:
            self.service_var.set("No Services Available")

        service_menu = tk.OptionMenu(form_frame, self.service_var, *self.service_names)
        service_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # 2. Amount Needed
        tk.Label(form_frame, text="Amount Needed ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # 3. Proof of Charge (Link)
        tk.Label(form_frame, text="Proof of Charge (URL):").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.proof_entry = tk.Entry(form_frame, width=20)
        self.proof_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        # 4. Submission Button
        tk.Button(form_frame, text="Submit Fund Request", command=self.create_fund, bg='green', fg='white').grid(row=3, columnspan=2, pady=15)

    # NOTE: This function is called when the frame is raised, updating the user_id label
    def update_user_label(self):
        # Find and update the user ID label if necessary, though simpler to use the stored self.user_id
        pass 

    def create_fund(self):
        """Inserts a new record into the FundsNeeded table."""
        if not self.user_id:
            messagebox.showerror("Error", "Recipient ID is missing. Please log in again.")
            return

        service_name = self.service_var.get()
        amount_needed = self.amount_entry.get()
        proof_of_charge = self.proof_entry.get()
        
        # --- Validation ---
        if service_name not in self.service_map:
            messagebox.showerror("Validation Error", "Please select a valid service provider.")
            return

        try:
            amount_needed = float(amount_needed)
            if amount_needed <= 0:
                messagebox.showerror("Validation Error", "Amount must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid number for Amount Needed.")
            return

        service_id = self.service_map[service_name]
        recipient_id = self.user_id

        # --- Database Insertion ---
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                query = """
                INSERT INTO FundsNeeded 
                (recipient_id, service_id, amount_needed, proof_of_charge, is_verified) 
                VALUES (%s, %s, %s, %s, FALSE)
                """
                cursor.execute(query, (recipient_id, service_id, amount_needed, proof_of_charge))
                conn.commit()
                messagebox.showinfo("Success", "Fund Request submitted successfully! It is now pending Admin verification.")
                
                # Clear the form after submission
                self.amount_entry.delete(0, tk.END)
                self.proof_entry.delete(0, tk.END)
                
                # Optionally refresh the main window view
                self.controller.show_frame(MainWindow)
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to submit fund request: {err}")
            finally:
                cursor.close()
                conn.close()

# Note: The MainApp __init__ still needs to be updated to handle the new RecipientDashboard constructor correctly.

        
class DonorDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        
        tk.Label(self, text="Donor Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Make a New Donation", font=("Arial", 14, "underline")).pack(pady=10)
        
        # Frame for the donation form
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # --- Form Fields ---
        
        # 1. Fund Selection
        tk.Label(form_frame, text="Select Fund:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.funds_data = fetch_active_funds()
        self.fund_descriptions = [desc for id, desc, needed, raised, name in self.funds_data]
        self.fund_id_map = {desc: id for id, desc, needed, raised, name in self.funds_data}
        
        self.fund_var = tk.StringVar(self)
        if self.fund_descriptions:
            self.fund_var.set(self.fund_descriptions[0]) # Default to the first fund
        else:
            self.fund_var.set("No Active Funds Available")

        fund_menu = tk.OptionMenu(form_frame, self.fund_var, *self.fund_descriptions)
        fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # 2. Donation Amount
        tk.Label(form_frame, text="Donation Amount ($):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # 3. Anonymity Option (Assuming the Donor table's default is respected on NULL insert)
        tk.Label(form_frame, text="Donate Anonymously:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.is_anonymous_var = tk.BooleanVar(self)
        # Checkbutton will set self.is_anonymous_var to True if checked
        tk.Checkbutton(form_frame, variable=self.is_anonymous_var).grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # 4. Submission Button
        tk.Button(form_frame, text="Submit Donation", command=self.submit_donation, bg='blue', fg='white').grid(row=3, columnspan=2, pady=15)

    def submit_donation(self):
        """Inserts a new record into the Donations table and updates FundsNeeded."""
        if not self.user_id:
            messagebox.showerror("Error", "Donor ID is missing. Please log in again.")
            return

        fund_description = self.fund_var.get()
        donation_amount_str = self.amount_entry.get()
        is_anonymous = self.is_anonymous_var.get()
        
        # --- Validation ---
        if fund_description not in self.fund_id_map:
            messagebox.showerror("Validation Error", "Please select a valid active fund.")
            return

        try:
            donation_amount = float(donation_amount_str)
            if donation_amount <= 0:
                messagebox.showerror("Validation Error", "Donation amount must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid number for Donation Amount.")
            return

        fund_id = self.fund_id_map[fund_description]
        
        # Determine donor_id for the INSERT (NULL if anonymous)
        donor_id_to_insert = None if is_anonymous else self.user_id

        # --- Database Transaction ---
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # 1. Insert into Donations table
                donation_query = """
                INSERT INTO Donations 
                (fund_id, donor_id, donation_amount, payment_status) 
                VALUES (%s, %s, %s, 'Completed')
                """
                # We assume 'Completed' status for simplicity, skipping the 'Pending' payment gateway step.
                cursor.execute(donation_query, (fund_id, donor_id_to_insert, donation_amount))
                
                # 2. Update FundsNeeded table (amount_raised)
                update_fund_query = """
                UPDATE FundsNeeded SET 
                    amount_raised = amount_raised + %s, 
                    is_fully_funded = IF((amount_raised + %s) >= amount_needed, TRUE, FALSE)
                WHERE fund_id = %s
                """
                # We use the donated amount twice in the query to correctly check for full funding
                cursor.execute(update_fund_query, (donation_amount, donation_amount, fund_id))

                conn.commit()
                messagebox.showinfo("Success", f"Donation of ${donation_amount:.2f} submitted successfully to Fund ID {fund_id}!")
                
                # Clear the form and refresh data
                self.amount_entry.delete(0, tk.END)
                self.is_anonymous_var.set(False)
                self.controller.show_frame(MainWindow) # Go back to main window to see updated funds
                
            except mysql.connector.Error as err:
                conn.rollback() # Rollback the transaction if any step failed
                messagebox.showerror("Database Error", f"Failed to submit donation: {err}")
            finally:
                cursor.close()
                conn.close()

class ServiceDashboard(tk.Frame):
    def __init__(self, master, controller, user_id):
        super().__init__(master)
        self.controller = controller
        self.user_id = user_id
        
        tk.Label(self, text="🛠️ Service Dashboard", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Button(self, text="Logout", command=controller.logout).pack(pady=10)
        
        tk.Label(self, text="Verify Charge for Funds You Are Providing Service For", font=("Arial", 14, "underline")).pack(pady=10)
        
        # Frame for the form
        form_frame = tk.Frame(self)
        form_frame.pack(padx=20, pady=10, fill='x')

        # --- Form Fields ---
        
        # 1. Fund Selection
        tk.Label(form_frame, text="Select Fund to Update:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.funds_data = [] # Will be populated on refresh
        self.fund_descriptions = []
        self.fund_map = {} # Maps description to (fund_id, current_proof)
        
        self.fund_var = tk.StringVar(self)
        self.fund_var.set("Loading Funds...")

        fund_menu = tk.OptionMenu(form_frame, self.fund_var, *['Loading Funds...'])
        fund_menu.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # 2. Proof of Charge (Link)
        tk.Label(form_frame, text="Proof of Charge (URL):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.proof_entry = tk.Entry(form_frame, width=40)
        self.proof_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        # 3. Submission Button
        tk.Button(form_frame, text="Update Proof of Charge", command=self.update_proof, bg='orange', fg='white').grid(row=2, columnspan=2, pady=15)
        
        # 4. Bind selection change to update entry field
        self.fund_var.trace_add("write", lambda *args: self.load_current_proof())
        
        # Initial data load
        self.load_funds()

    def load_funds(self):
        """Fetches and populates the fund selection dropdown."""
        if not self.user_id:
            return

        self.funds_data = fetch_service_funds(self.user_id)
        
        # Clear existing mappings and descriptions
        self.fund_descriptions = []
        self.fund_map = {}

        if not self.funds_data:
            self.fund_var.set("No Funds Assigned to Your Service")
            self.proof_entry.delete(0, tk.END)
            return

        for fund_id, recipient_name, amount_needed, proof_of_charge in self.funds_data:
            description = f"Fund ID {fund_id} for {recipient_name} (${amount_needed:.2f})"
            self.fund_descriptions.append(description)
            self.fund_map[description] = (fund_id, proof_of_charge if proof_of_charge else '')
            
        # Update the OptionMenu's options
        menu = self.children['!frame2'].children['!optionmenu'].children['!menu'] # Access the underlying menu
        menu.delete(0, "end")
        for fund_desc in self.fund_descriptions:
            menu.add_command(label=fund_desc, command=tk._setit(self.fund_var, fund_desc))

        # Set default value and load the initial proof
        self.fund_var.set(self.fund_descriptions[0])
        self.load_current_proof()

    def load_current_proof(self):
        """Loads the proof_of_charge for the currently selected fund into the entry field."""
        selected_desc = self.fund_var.get()
        if selected_desc in self.fund_map:
            fund_id, current_proof = self.fund_map[selected_desc]
            self.proof_entry.delete(0, tk.END)
            self.proof_entry.insert(0, current_proof)
        else:
            self.proof_entry.delete(0, tk.END)

    def update_proof(self):
        """Updates the proof_of_charge for the selected fund in the FundsNeeded table."""
        selected_desc = self.fund_var.get()
        new_proof = self.proof_entry.get()
        
        if selected_desc not in self.fund_map or not self.user_id:
            messagebox.showerror("Error", "Please select a valid fund.")
            return
        
        fund_id, _ = self.fund_map[selected_desc]

        # --- Database Update ---
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                query = """
                UPDATE FundsNeeded 
                SET proof_of_charge = %s
                WHERE fund_id = %s AND service_id = %s
                """
                cursor.execute(query, (new_proof, fund_id, self.user_id))
                conn.commit()
                messagebox.showinfo("Success", f"Proof of Charge for Fund ID {fund_id} updated successfully!")
                
                # Refresh data and update the main window
                self.load_funds() 
                self.controller.show_frame(MainWindow)
                
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to update proof of charge: {err}")
            finally:
                cursor.close()
                conn.close()

# Note: You may need to update the initial load of the MainApp to call load_funds() 
# when the ServiceDashboard frame is shown for the first time or after a login. 
# For simplicity, I've added load_funds() to the end of the __init__ and update_proof() methods.

# --- 4. Main Display Window (Before Login) ---

class MainWindow(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
        tk.Label(self, text="🏠 Fundraising Platform", font=("Arial", 24, "bold")).pack(pady=10)
        
        # --- Login/Register Buttons ---
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Log In", command=lambda: controller.show_frame(LoginWindow), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Register", command=lambda: controller.show_frame(RegistrationWindow), width=15).pack(side=tk.LEFT, padx=10)
        
        # --- Funds Needed Display ---
        tk.Label(self, text="🌟 Active Fundraising Goals", font=("Arial", 16, "underline")).pack(pady=10)
        self.create_funds_table()
        
        # --- Donations Display ---
        tk.Label(self, text="💖 Latest Donations", font=("Arial", 16, "underline")).pack(pady=10)
        self.create_donations_table()

        self.load_data()

    def create_funds_table(self):
        """Creates the Treeview widget for FundsNeeded."""
        columns = ('#ID', 'Recipient', 'Service', 'Needed', 'Raised', 'Funded')
        self.funds_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for col in columns:
            self.funds_tree.heading(col, text=col)
            self.funds_tree.column(col, anchor=tk.CENTER, width=70 if col in ('#ID', 'Funded') else 120)
        self.funds_tree.pack(padx=20, pady=5)

    def create_donations_table(self):
        """Creates the Treeview widget for Donations."""
        columns = ('#D_ID', '#F_ID', 'Donor', 'Amount', 'Date')
        self.donations_tree = ttk.Treeview(self, columns=columns, show='headings', height=5)
        for col in columns:
            self.donations_tree.heading(col, text=col)
            self.donations_tree.column(col, anchor=tk.CENTER, width=70 if col in ('#D_ID', '#F_ID') else 120)
        self.donations_tree.pack(padx=20, pady=5)

    def load_data(self):
        """Fetches and populates data into both tables."""
        # Clear existing data
        for item in self.funds_tree.get_children():
            self.funds_tree.delete(item)
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)

        # Load FundsNeeded
        funds_data = fetch_funds_data()
        for fund in funds_data:
            # Format currency and boolean flag
            needed = f"${fund[3]:.2f}"
            raised = f"${fund[4]:.2f}"
            funded = "YES" if fund[5] else "NO"
            self.funds_tree.insert('', tk.END, values=(fund[0], fund[1], fund[2], needed, raised, funded))

        # Load Donations
        donations_data = fetch_donations_data()
        for donation in donations_data:
            # Format currency and date
            donor_name = donation[2] if donation[2] is not None else "Anonymous"
            amount = f"${donation[3]:.2f}"
            date_str = donation[4].strftime("%Y-%m-%d") if donation[4] else "N/A"
            self.donations_tree.insert('', tk.END, values=(donation[0], donation[1], donor_name, amount, date_str))


# --- 5. Main Login/Registration Windows ---
# ... (LoginWindow and RegistrationWindow classes remain the same) ...

class LoginWindow(tk.Frame):
    # (Same as before)
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        tk.Label(self, text="Welcome! Please Log In", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
        tk.Label(self, text="Email:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Label(self, text="Password:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.password_entry = tk.Entry(self, show="*", width=30)
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self, text="Login", command=self.handle_login).grid(row=3, column=1, pady=10, sticky='w')
        tk.Button(self, text="Back to Main", command=lambda: controller.show_frame(MainWindow)).grid(row=4, columnspan=2, pady=10)

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get() 
        # Use the sample data credentials:
        # Recipient: alice.r@example.com / hash_recipient_123
        # Donor: charlie.d@example.com / hash_donor_123
        # Service: bob.s@example.com / hash_service_123

        user_id, user_role = authenticate_user(email, password) 

        if user_id:
            messagebox.showinfo("Success", f"Logged in as {user_role}.")
            self.controller.login(user_id, user_role)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

class RegistrationWindow(tk.Frame):
    # (Simplified as before)
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        tk.Label(self, text="New User Registration", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
        tk.Label(self, text="Choose Role:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.role_var = tk.StringVar(self)
        self.role_var.set("Recipient")
        roles = ['Recipient', 'Donor', 'Service', 'Admin']
        tk.OptionMenu(self, self.role_var, *roles).grid(row=1, column=1, padx=10, pady=5, sticky='w')
        tk.Button(self, text="Complete Registration", command=self.handle_registration).grid(row=5, column=1, pady=10, sticky='w')
        tk.Button(self, text="Back to Main", command=lambda: controller.show_frame(MainWindow)).grid(row=6, columnspan=2, pady=10)

    def handle_registration(self):
        role = self.role_var.get()
        messagebox.showinfo("Registered", f"Registration simulated! New user created with role: {role}. You can now log in.")
        self.controller.show_frame(LoginWindow)


# --- 6. Main Application Controller ---

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fundraising Project")
        self.geometry("800x600")
        
        self.user_id = None
        self.user_role = None

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # Initialize all possible frames
        for F in (MainWindow, LoginWindow, RegistrationWindow, AdminDashboard, RecipientDashboard, DonorDashboard, ServiceDashboard):
            page_name = F.__name__
            # Dashboards require user_id, pass controller for now, update in login
            if F in (RecipientDashboard, DonorDashboard, ServiceDashboard):
                frame = F(master=container, controller=self, user_id=None) 
            else:
                frame = F(master=container, controller=self)

            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainWindow) # Start on the new Main Window

    def show_frame(self, cont):
        """Raises the requested frame to the top."""
        frame = self.frames[cont.__name__]
        # Reload data if going to the main window
        if cont.__name__ == 'MainWindow':
            frame.load_data()
        frame.tkraise()

    def login(self, user_id, user_role):
        """Called upon successful login."""
        self.user_id = user_id
        self.user_role = user_role

        # Route to the appropriate dashboard
        if user_role == 'Admin':
            self.show_frame(AdminDashboard)
        elif user_role == 'Recipient':
            self.frames['RecipientDashboard'].user_id = user_id # Update the user_id in the frame
            self.show_frame(RecipientDashboard)
        elif user_role == 'Donor':
            self.frames['DonorDashboard'].user_id = user_id
            self.show_frame(DonorDashboard)
        elif user_role == 'Service':
            self.frames['ServiceDashboard'].user_id = user_id
            self.show_frame(ServiceDashboard)
        else:
            messagebox.showerror("Error", "Role not recognized.")
            self.show_frame(LoginWindow)

    def logout(self):
        """Resets user state and returns to the Main Window."""
        self.user_id = None
        self.user_role = None
        self.show_frame(MainWindow)
        
    def show_frame(self, cont):
            """Raises the requested frame to the top and reloads data if necessary."""
            frame = self.frames[cont.__name__]
            
            # Always reload data when returning to the public view
            if cont.__name__ == 'MainWindow':
                frame.load_data()
            
            # Reload data for dashboards that list dynamic data
            elif cont.__name__ == 'AdminDashboard':
                # This calls the load_funds method we added to AdminDashboard
                frame.load_funds() 
            elif cont.__name__ == 'DonorDashboard':
                # Ensure your DonorDashboard has a load_funds method for this to work
                # If not, you should add one that wraps the fund fetching logic.
                # Assuming you added one, or this will be handled in the next step.
                try:
                    frame.load_funds()
                except AttributeError:
                    pass # Silently skip if not yet implemented

            frame.tkraise()
            
# --- Main Execution ---
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()