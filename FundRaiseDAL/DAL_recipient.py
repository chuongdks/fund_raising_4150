from DAL_core import get_db_connection
import mysql.connector

# ============================================================
# Helper Query Functions related to recipients role
# ============================================================
def fetch_all_services():
    """Fetches list of services (id, name) for the Recipient fund creation form."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, name FROM Users WHERE user_type = 'Service'"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

def insert_new_fund(recipient_id, service_id, amount_needed, proof_of_charge):
    """Inserts a new fund request into the FundsNeeded table."""
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
            return True, "Success"
        except mysql.connector.Error as err:
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."