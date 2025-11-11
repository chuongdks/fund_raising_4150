from FundRaiseDAL import DAL_recipient

class RecipientManager:
    """Handles logic for creating and managing fund requests."""
    
    def get_services_data(self):
        """Fetches all service providers for the dropdown list."""
        # Returns list of (id, name)
        return DAL_recipient.fetch_all_services()
        
    def create_fund(self, recipient_id, service_name, amount_needed_str, proof_of_charge, service_map):
        """Submits a new fund request after validation."""
        
        if service_name not in service_map:
            return False, "Validation Error: Please select a valid service provider."

        try:
            amount_needed = float(amount_needed_str)
            if amount_needed <= 0:
                return False, "Validation Error: Amount must be greater than zero."
        except ValueError:
            return False, "Validation Error: Please enter a valid number for Amount Needed."

        service_id = service_map[service_name]
        
        success, db_message = DAL_recipient.insert_new_fund(
            recipient_id, service_id, amount_needed, proof_of_charge
        )
        
        if success:
            return True, "Fund Request submitted successfully! It is now pending Admin verification."
        else:
            return False, f"Database Error: Failed to submit fund request: {db_message}"