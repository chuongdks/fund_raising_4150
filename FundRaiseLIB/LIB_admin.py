from FundRaiseDAL import DAL_admin

class AdminManager:
    """Handles all admin-specific business rules."""
    
    def get_pending_funds_list(self):
        """Fetches pending funds list from DAL."""
        # Returns list of (fund_id, recipient_name, service_name, amount_needed, proof_of_charge)
        return DAL_admin.fetch_unverified_funds()
    
    def verify_fund(self, fund_id):
        """Coordinates fund verification using the Admin DAL."""
        if not fund_id:
            return False, "Error: Fund ID is missing."
        
        success = DAL_admin.update_fund_verification_status(fund_id)
        
        if success:
            return True, f"Fund ID {fund_id} has been successfully verified! It is now active for donations."
        else:
            return False, "Failed to verify fund due to a database error."