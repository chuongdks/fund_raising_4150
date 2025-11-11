from FundRaiseDAL import Dal_core

class AuthManager:
    """Handles login and registration logic."""
    def authenticate_user(self, email, password):
        return Dal_core.authenticate_user(email, password)

# Add a Registration logic here.