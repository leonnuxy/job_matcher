import mysql.connector
import logging
from config import DB_CONFIG # Import database configuration

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logging.info("Successfully connected to the database.")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database: {err}")
        return None

def create_results_table(conn):
    """Creates the 'job_results' table if it doesn't exist."""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_title VARCHAR(255),
                company VARCHAR(255),
                location VARCHAR(255),
                job_url VARCHAR(255) UNIQUE, -- Reduced length for index compatibility
                ats_score DECIMAL(5, 2),      -- ATS score (e.g., 85.50)
                similarity_score DECIMAL(5, 4), -- Similarity score (e.g., 0.8765)
                keywords TEXT,                -- Comma-separated keywords
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logging.info("Checked/created 'job_results' table.")
    except mysql.connector.Error as err:
        logging.error(f"Error creating table: {err}")
    finally:
        cursor.close()

def save_job_result(conn, job_data):
    """Saves a single job result to the database.

    Args:
        conn: The database connection object.
        job_data (dict): A dictionary containing job details and scores.
                         Expected keys: 'title', 'company', 'location', 'url',
                                        'ats_score', 'similarity_score', 'keywords' (list)
    """
    cursor = conn.cursor()
    sql = """
        INSERT INTO job_results (job_title, company, location, job_url, ats_score, similarity_score, keywords)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE -- Update scores if URL already exists
            ats_score = VALUES(ats_score),
            similarity_score = VALUES(similarity_score),
            keywords = VALUES(keywords),
            processed_at = CURRENT_TIMESTAMP
    """
    try:
        keywords_str = ','.join(job_data.get('keywords', [])) # Convert list to string
        values = (
            job_data.get('title'),
            job_data.get('company'),
            job_data.get('location'),
            job_data.get('url'),
            job_data.get('ats_score'),
            job_data.get('similarity_score'),
            keywords_str
        )
        cursor.execute(sql, values)
        conn.commit()
        logging.info(f"Saved/Updated result for job: {job_data.get('title')} at {job_data.get('company')}")
    except mysql.connector.Error as err:
        logging.error(f"Error saving job result for {job_data.get('url')}: {err}")
        conn.rollback() # Rollback on error
    except Exception as e:
        logging.error(f"Unexpected error saving job result: {e}")
        conn.rollback()
    finally:
        cursor.close()

# Example Usage (optional, for testing)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    connection = get_db_connection()
    if connection:
        create_results_table(connection)
        # Example data
        test_data = {
            'title': 'Software Engineer',
            'company': 'TestCorp',
            'location': 'Remote',
            'url': 'http://example.com/job/123',
            'ats_score': 88.5,
            'similarity_score': 0.9123,
            'keywords': ['python', 'api', 'docker']
        }
        save_job_result(connection, test_data)
        connection.close()
        logging.info("Database connection closed.")
