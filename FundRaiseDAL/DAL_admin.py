from FundRaiseDAL.DAL_core import get_db_connection
import mysql.connector

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
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

def update_fund_verification_status(fund_id):
    """Updates a fund's is_verified status to TRUE."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "UPDATE FundsNeeded SET is_verified = TRUE WHERE fund_id = %s"
            cursor.execute(query, (fund_id,))
            conn.commit()
            return True
        except mysql.connector.Error:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()
    return False