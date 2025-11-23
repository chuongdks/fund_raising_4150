from FundRaiseDAL.DAL_core import get_db_connection
import mysql.connector
from datetime import datetime

# ============================================================
# Helper Query Functions related to admin role
# ============================================================

def fetch_unverified_funds():
    """
    Fetches FundsNeeded records that are not yet verified (is_verified = FALSE).
    Returns list of (fund_id, recipient_name, service_name, amount_needed, proof_of_charge).
    """
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
        try:
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except mysql.connector.Error as err:
            print(f"DAL_admin.fetch_unverified_funds Error: {err}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

def fetch_all_funds():
    """
    Fetches ALL FundsNeeded records for admin management.
    Returns list of:
      (fund_id, recipient_name, service_name,
       amount_needed, amount_raised, is_verified, is_fully_funded, proof_of_charge)
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS RecipientName,
            s.service_name AS ServiceName,
            f.amount_needed,
            f.amount_raised,
            f.is_verified,
            f.is_fully_funded,
            f.proof_of_charge
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Services s ON f.service_id = s.user_id
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    return []

def update_fund_verification_status(fund_id: int, admin_id: int, admin_notes: str) -> bool:
    """
    Updates the verification status of a fund, recording the admin who did it 
    and the notes/date.
    Returns (success: bool, message: str).
    """
    conn = get_db_connection()
    current_time = datetime.now()
    
    if conn:
        cursor = conn.cursor()
        
        try:
            query = """
            UPDATE FundsNeeded
            SET is_verified = TRUE,
                verified_by_admin_id = %s,   
                admin_notes = %s,             
                verification_date = %s       
            WHERE fund_id = %s
            """
            # Updated parameters list to match the new query
            params = (admin_id, admin_notes, current_time, fund_id) 
            cursor.execute(query, params)
            conn.commit()
            return True, "Success"
        except mysql.connector.Error:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    return False


def update_fund_amount_and_proof(fund_id: int, new_amount: float, new_proof: str):
    """
    Updates amount_needed and proof_of_charge for a specific fund.
    Returns (success: bool, message: str).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            UPDATE FundsNeeded
            SET amount_needed = %s,
                proof_of_charge = %s
            WHERE fund_id = %s
            """
            cursor.execute(query, (new_amount, new_proof, fund_id))
            conn.commit()
            return True, "Success"
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def delete_fund(fund_id: int):
    """
    Deletes a fund (and its donations) from the database.
    Returns (success: bool, message: str).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Remove dependent donations first (FK constraint)
            cursor.execute("DELETE FROM Donations WHERE fund_id = %s", (fund_id,))
            # Then delete the fund itself
            cursor.execute("DELETE FROM FundsNeeded WHERE fund_id = %s", (fund_id,))
            conn.commit()
            return True, "Success"
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."


def upsert_admin_profile(user_id: int):
    """
    Inserts a new record into the Admins profile table if it doesn't exist.
    This is required to properly register an Admin role.
    Returns (success: bool, message: str).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Check if Admin profile already exists (to prevent duplicates)
            cursor.execute("SELECT user_id FROM Admins WHERE user_id = %s", (user_id,))
            exists = cursor.fetchone()
            
            if not exists:
                # Insert if it doesn't exist
                # Assumes the Admins table only requires the user_id foreign key
                cursor.execute(
                    "INSERT INTO Admins (user_id) VALUES (%s)",
                    (user_id,)
                )
            conn.commit()
            return True, 'Success'
        except mysql.connector.Error as err:
            conn.rollback()
            return False, str(err)
        finally:
            cursor.close()
            conn.close()
    return False, "Failed to connect to the database."