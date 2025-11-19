from FundRaiseDAL import DAL_core


class AuthManager:
    """Handles login and registration logic."""

    def authenticate_user(self, email, password):
        """Returns (user_id, user_type) on success, (None, None) on failure."""
        return DAL_core.authenticate_user(email, password)

    def register_user(self, name, email, password, role):
        """Registers a new user after basic validation.

        Returns (True, user_id) or (False, error_message).
        """
        # Basic validation
        name = (name or '').strip()
        email = (email or '').strip()
        if not name or not email or not password:
            return False, "All fields are required."
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."

        # Check if email already exists
        existing = DAL_core.fetch_user_by_email(email)
        if existing:
            return False, "Email is already registered."

        # Create user (DAL_core will hash the password)
        success, result = DAL_core.create_user(name, email, password, role)
        if success:
            return True, result
        return False, result
        