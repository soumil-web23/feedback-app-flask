# app.py
from flask import Flask, render_template, request, redirect, url_for
import pymysql
import os

app = Flask(__name__)

# --- CONFIGURE DATABASE CONNECTION ---
# Replace these with the details from your RDS instance
DB_ENDPOINT = "my-feedback-db-instance.cp8s8yy6cv49.ap-south-1.rds.amazonaws.com"
DB_USERNAME = "soumil" # The username you chose
DB_PASSWORD = "skDB1234" # The password you chose
DB_NAME = "feedbackdb" # The DB name you chose
# --- END OF CONFIGURATION ---

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = pymysql.connect(
            host=DB_ENDPOINT,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Database connection successful!")
        return conn
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def setup_database():
    """Creates the feedback table if it doesn't exist."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # SQL to create feedback table [cite: 16]
                create_table_query = """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cursor.execute(create_table_query)
                conn.commit()
            print("Table 'feedback' is ready.")
        finally:
            conn.close()

@app.route('/')
def index():
    """Displays existing feedback."""
    conn = get_db_connection()
    feedback_list = []
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT username, message, created_at FROM feedback ORDER BY created_at DESC")
                feedback_list = cursor.fetchall()
        finally:
            conn.close()
    return render_template('index.html', feedbacks=feedback_list)

@app.route('/submit', methods=['POST'])
def submit():
    """Handles submission of new feedback."""
    username = request.form['username']
    message = request.form['message']
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO feedback (username, message) VALUES (%s, %s)"
                cursor.execute(sql, (username, message))
            conn.commit()
        finally:
            conn.close()
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    setup_database() # This line ensures the table is created when the app starts.
    app.run(host='0.0.0.0', port=80) # Run on port 80 for public access
