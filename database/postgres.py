from dotenv import load_dotenv
import os, psycopg2

load_dotenv()

# Config Database Connection
def create_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432)
        )
        print("Connection successful!")
        return conn

    except psycopg2.Error as e:
        print("Unable to connect to PostgreSQL:")
        print(e)
        return None

# Connecting
connection = create_connection()

# Test Connection
if connection:
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    print("PostgreSQL version:", cursor.fetchone())
    cursor.close()
    connection.close()