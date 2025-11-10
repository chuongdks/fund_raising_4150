# main_app.py

import tkinter as tk
from tkinter import messagebox
from FundRaiseGUI import dashboards

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
        for F in (
            dashboards.MainWindow, 
            dashboards.LoginWindow, 
            dashboards.RegistrationWindow, 
            dashboards.AdminDashboard, 
            dashboards.RecipientDashboard, 
            dashboards.DonorDashboard, 
            dashboards.ServiceDashboard
        ):
            page_name = F.__name__
            # Dashboards require user_id, pass controller for now, update in login
            if F in (dashboards.RecipientDashboard, dashboards.DonorDashboard, dashboards.ServiceDashboard):
                frame = F(master=container, controller=self, user_id=None) 
            else:
                frame = F(master=container, controller=self)

            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # UPDATED REFERENCE
        self.show_frame(dashboards.MainWindow) # Start on the Main Window

    def login(self, user_id, user_role):
        """Called upon successful login. Updates user info and routes to dashboard."""
        self.user_id = user_id
        self.user_role = user_role

        # Update user_id in the target frame before showing it
        target_frame_name = user_role + 'Dashboard'
        if user_role in ('Recipient', 'Donor', 'Service'):
            self.frames[target_frame_name].user_id = user_id
        
        # Route to the appropriate dashboard, ensuring data is refreshed (UPDATED REFERENCES)
        if user_role == 'Admin':
            self.show_frame(dashboards.AdminDashboard)
        elif user_role == 'Recipient':
            self.show_frame(dashboards.RecipientDashboard)
        elif user_role == 'Donor':
            self.show_frame(dashboards.DonorDashboard)
        elif user_role == 'Service':
            self.show_frame(dashboards.ServiceDashboard)
        else:
            messagebox.showerror("Error", "Role not recognized.")
            self.show_frame(dashboards.LoginWindow)

    def logout(self):
        """Resets user state and returns to the Main Window."""
        self.user_id = None
        self.user_role = None
        # UPDATED REFERENCE
        self.show_frame(dashboards.MainWindow)
        
    def show_frame(self, cont):
        """Raises the requested frame to the top and reloads data if necessary."""
        frame = self.frames[cont.__name__]
        
        # Data refresh logic for dynamic dashboards
        if cont.__name__ == 'MainWindow':
            frame.load_data()
        elif cont.__name__ in ('AdminDashboard', 'DonorDashboard', 'ServiceDashboard'):
            # These dashboards have a load_funds() method to refresh their data
            frame.load_funds() 

        frame.tkraise()
            
# --- Main Execution ---
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()