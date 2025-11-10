from FundRaiseDAL import db_connector 
import mysql.connector 

class FundraisingManager:
    """
    Business Logic Layer (BLL) for handling all application rules, 
    coordinating with the Data Access Layer (DAL), and performing 
    data validation and transaction orchestration.
    """
    
    # --- User/Auth Logic ---
    def authenticate_user(self, email, password):
        """Authenticates user via DAL."""
        return db_connector.authenticate_user(email, password)

    # --- Admin Logic ---
    def verify_fund(self, fund_id):
        """Verifies a fund and makes it active for donations."""
        conn = db_connector.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                query = "UPDATE FundsNeeded SET is_verified = TRUE WHERE fund_id = %s"
                cursor.execute(query, (fund_id,))
                conn.commit()
                return True, f"Fund ID {fund_id} has been successfully verified! It is now active for donations."
            except mysql.connector.Error as err:
                conn.rollback()
                return False, f"Failed to verify fund: {err}"
            finally:
                cursor.close()
                conn.close()
        return False, "Failed to connect to the database."

    # --- Recipient Logic ---
    def create_fund(self, recipient_id, service_name, amount_needed_str, proof_of_charge, service_map):
        """Submits a new fund request to the DAL after validation."""
        
        if service_name not in service_map:
            return False, "Validation Error: Please select a valid service provider."

        try:
            amount_needed = float(amount_needed_str)
            if amount_needed <= 0:
                return False, "Validation Error: Amount must be greater than zero."
        except ValueError:
            return False, "Validation Error: Please enter a valid number for Amount Needed."

        service_id = service_map[service_name]

        conn = db_connector.get_db_connection()
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
                return True, "Fund Request submitted successfully! It is now pending Admin verification."
            except mysql.connector.Error as err:
                return False, f"Database Error: Failed to submit fund request: {err}"
            finally:
                cursor.close()
                conn.close()
        return False, "Failed to connect to the database."

    # --- Donor Logic ---
    def submit_donation(self, fund_description, donation_amount_str, is_anonymous, fund_id_map, donor_user_id):
        """
        Handles the transaction for a donation, updating both Donations and FundsNeeded tables.
        This is a business transaction that requires two DAL updates (multi-step).
        """
        
        if fund_description not in fund_id_map:
            return False, "Validation Error: Please select a valid active fund."

        try:
            donation_amount = float(donation_amount_str)
            if donation_amount <= 0:
                return False, "Validation Error: Donation amount must be greater than zero."
        except ValueError:
            return False, "Validation Error: Please enter a valid number for Donation Amount."

        fund_id = fund_id_map[fund_description]
        donor_id_to_insert = None if is_anonymous else donor_user_id

        conn = db_connector.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # 1. Insert into Donations table
                donation_query = """
                INSERT INTO Donations 
                (fund_id, donor_id, donation_amount, payment_status) 
                VALUES (%s, %s, %s, 'Completed')
                """
                cursor.execute(donation_query, (fund_id, donor_id_to_insert, donation_amount))
                
                # 2. Update FundsNeeded table (amount_raised and is_fully_funded)
                update_fund_query = """
                UPDATE FundsNeeded SET 
                    amount_raised = amount_raised + %s, 
                    is_fully_funded = IF((amount_raised + %s) >= amount_needed, TRUE, FALSE)
                WHERE fund_id = %s
                """
                cursor.execute(update_fund_query, (donation_amount, donation_amount, fund_id))

                conn.commit()
                return True, f"Donation of ${donation_amount:.2f} submitted successfully to Fund ID {fund_id}!"
                
            except mysql.connector.Error as err:
                conn.rollback() 
                return False, f"Database Error: Failed to submit donation: {err}"
            finally:
                cursor.close()
                conn.close()
        return False, "Failed to connect to the database."
    
    # --- Service Logic ---
    def update_fund_proof(self, fund_description, new_proof, service_user_id, fund_map):
        """Updates the proof of charge for a fund."""
        
        if fund_description not in fund_map:
            return False, "Please select a valid fund."
        
        fund_id, _ = fund_map[fund_description]

        conn = db_connector.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                query = """
                UPDATE FundsNeeded 
                SET proof_of_charge = %s
                WHERE fund_id = %s AND service_id = %s
                """
                cursor.execute(query, (new_proof, fund_id, service_user_id))
                conn.commit()
                return True, f"Proof of Charge for Fund ID {fund_id} updated successfully!"
                
            except mysql.connector.Error as err:
                return False, f"Database Error: Failed to update proof of charge: {err}"
            finally:
                cursor.close()
                conn.close()
        return False, "Failed to connect to the database."