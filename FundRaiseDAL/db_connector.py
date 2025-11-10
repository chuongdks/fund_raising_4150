import mysql.connector

# --- 1. Database Configuration (Customize this!) ---
DB_CONFIG = {
    'user': 'root',             # <--- CHANGE THIS
    'password': 'Chuck!2345',   # <--- AND THIS TOO
    'host': '127.0.0.1',
    'database': 'fundraising_db'
}

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        # NOTE: Using print here as this is executed before the main GUI loop
        print(f"Error connecting to MySQL: {err}") 
        return None

# --- DATABASE QUERY FUNCTIONS ---

def authenticate_user(email, password):
    """Checks credentials and returns (user_id, user_type) if valid."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, user_type FROM Users WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result if result else (None, None)
    return (None, None)

def fetch_funds_data():
    """Fetches key information about all FundsNeeded for the Main Window."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS Recipient,
            s.service_name AS Service,
            f.amount_needed,
            f.amount_raised,
            f.is_fully_funded
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        JOIN Services s ON f.service_id = s.user_id
        ORDER BY f.fund_id DESC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

def fetch_donations_data():
    """Fetches key information about recent Donations for the Main Window."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            d.donation_id,
            d.fund_id,
            u_don.name AS Donor,
            d.donation_amount,
            d.donation_date
        FROM Donations d
        LEFT JOIN Donors r ON d.donor_id = r.user_id
        LEFT JOIN Users u_don ON r.user_id = u_don.user_id
        ORDER BY d.donation_date DESC
        LIMIT 10;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

def fetch_services():
    """Fetches all Service IDs and Names for the Recipient's dropdown."""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT user_id, service_name FROM Services"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

def fetch_active_funds():
    """
    Fetches active (verified and not fully funded) funds for the Donor's dropdown.
    Returns list of (fund_id, description, amount_needed, amount_raised, recipient_name).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            CONCAT('Fund for ', u_rec.name, ' (ID: ', f.fund_id, ') - Needed: $', (f.amount_needed - f.amount_raised)) AS fund_description,
            f.amount_needed,
            f.amount_raised,
            u_rec.name
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        WHERE f.is_verified = TRUE AND f.is_fully_funded = FALSE
        ORDER BY f.fund_id ASC;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

def fetch_service_funds(service_user_id):
    """
    Fetches FundsNeeded records associated with the logged-in service provider.
    Returns list of (fund_id, recipient_name, amount_needed, proof_of_charge).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
        SELECT
            f.fund_id,
            u_rec.name AS RecipientName,
            f.amount_needed,
            f.proof_of_charge
        FROM FundsNeeded f
        JOIN Users u_rec ON f.recipient_id = u_rec.user_id
        WHERE f.service_id = %s
        ORDER BY f.fund_id DESC;
        """
        cursor.execute(query, (service_user_id,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    return []

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