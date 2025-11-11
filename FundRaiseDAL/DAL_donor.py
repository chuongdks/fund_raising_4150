from DAL_core import get_db_connection
import mysql.connector

# ============================================================
# Helper Query Functions related to donor role
# ============================================================
def fetch_active_funds():
    """Fetches active, unfulfilled funds for the Donor dashboard."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT 
            f.fund_id, 
            CONCAT(f.fund_id, ': ', u_rec.name, ' (', s.service_name, ' - $', f.amount_needed, ')'),
            f.amount_needed,
            f.amount_raised,
            u_rec.name
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Users s ON f.service_id = s.user_id
        WHERE f.is_verified = TRUE AND f.is_fully_funded = FALSE
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        # Returns list of (fund_id, description, needed, raised, recipient_name)
        return data 
    return []

def execute_donation_transaction(fund_id, donor_id_to_insert, donation_amount):
    """Executes the two-step transaction (INSERT Donation and UPDATE FundsNeeded)."""
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
            cursor.execute(donation_query, (fund_id, donor_id_to_insert, donation_amount))
            
            # 2. Update FundsNeeded table
            update_fund_query = """
            UPDATE FundsNeeded SET 
                amount_raised = amount_raised + %s, 
                is_fully_funded = IF((amount_raised + %s) >= amount_needed, TRUE, FALSE)
            WHERE fund_id = %s
            """
            cursor.execute(update_fund_query, (donation_amount, donation_amount, fund_id))

            conn.commit()
            return True, "Success"
            
        except mysql.connector.Error as err:
            conn.rollback() 
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."