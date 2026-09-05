import pandas as pd

try:
    import mysql.connector
    MYSQL_LOADED = True
except ImportError:
    MYSQL_LOADED = False


def save_to_mysql(patient_id: str, patient_name: str, risk_score: str, db_password: str = ""):
    """
    Saves a patient risk assessment record into MySQL EHR database table.
    Returns:
        True if successful, or error message string.
    """
    if not MYSQL_LOADED:
        return "mysql.connector module is not installed."

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password=db_password)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS cardio_db")
        cursor.execute("USE cardio_db")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_risk (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(50),
                patient_name VARCHAR(100),
                risk_percent VARCHAR(20),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            cursor.execute("ALTER TABLE patient_risk ADD COLUMN patient_name VARCHAR(100) AFTER patient_id")
        except Exception:
            pass

        cursor.execute(
            "INSERT INTO patient_risk (patient_id, patient_name, risk_percent) VALUES (%s, %s, %s)",
            (patient_id, patient_name, risk_score)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return str(e)


def fetch_from_mysql(db_password: str = ""):
    """
    Fetches the 10 most recent patient risk records from the MySQL database.
    Returns:
        pd.DataFrame or None if failed.
    """
    if not MYSQL_LOADED:
        return None

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password=db_password, database="cardio_db")
        cursor = conn.cursor()
        query = "SELECT patient_id AS 'ID', patient_name AS 'Name', risk_percent AS 'Risk' FROM patient_risk ORDER BY timestamp DESC LIMIT 10"
        df = pd.read_sql(query, conn)
        cursor.close()
        conn.close()
        return df
    except Exception:
        return None
