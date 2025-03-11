import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="worksphere"
    )

def connect():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="worksphere"
    )

def execute_query(query, params=None, fetch_last_id=False):
    """Executes INSERT, UPDATE, DELETE queries."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    
    if fetch_last_id:
        last_id = cursor.lastrowid  # Get the last inserted ID
        conn.commit()
        cursor.close()
        conn.close()
        return last_id
    
    conn.commit()
    conn.close()

def fetch_query(query, params=None):
    """Fetches SELECT query results."""
    conn = connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    conn.close()
    return result

def get_user_role(user_id):
    """Fetches the role of a user."""
    query = "SELECT role FROM users WHERE user_id = %s"
    result = fetch_query(query, (user_id,))
    return result[0]['role'] if result else None
