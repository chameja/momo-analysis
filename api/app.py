import base64
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# Get the root folder (one level up from current file)
root_path = Path(__file__).resolve().parent.parent  # parent of parent

# Load the .env file from the root folder
load_dotenv(dotenv_path=root_path / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")

# ---------- Helper DB functions ----------
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Merge transactions from all tables
    query = """
   SELECT deposit_id AS id, 'Deposit' AS type, customer_id, amount, time_stamp, readable_date, new_balance
FROM Deposit
UNION
SELECT withdrawal_id AS id, 'Withdrawal' AS type, customer_id, amount, time_stamp, readable_date, new_balance
FROM Withdrawal
UNION
SELECT transfer_id AS id, 'Transfer' AS type, sender_log_id AS customer_id, amount, NULL AS time_stamp, NULL AS readable_date, new_balance
FROM Transfer
UNION
SELECT payment_id AS id, 'Payment' AS type, sender_log_id AS customer_id, amount, time_stamp, readable_date, new_balance
FROM Payment
"""
    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

def fetch_transaction_by_id(txn_id):
    all_txns = fetch_all_transactions()
    for txn in all_txns:
        if str(txn["id"]) == str(txn_id):
            return txn
    return None

def insert_transaction(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """INSERT INTO Deposit (deposit_id, customer_id, amount, readable_date, new_balance)
               VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(query, (
        data.get("id"),
        data.get("customer_id"),
        data.get("amount"),
        data.get("readable_date"),
        data.get("new_balance")
    ))

    conn.commit()
    cursor.close()
    conn.close()


def update_transaction(txn_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """UPDATE Deposit SET amount=%s, readable_date=%s, new_balance=%s WHERE deposit_id=%s"""
    cursor.execute(query, (
        data.get("amount"),
        data.get("readable_date"),
        data.get("new_balance"),
        txn_id
    ))

    conn.commit()
    cursor.close()
    conn.close()


def delete_transaction(txn_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    for table, id_field in TABLE_ID_MAP.items():
        cursor.execute(f"DELETE FROM {table} WHERE {id_field}=%s", (transaction_id,))

    conn.commit()
    cursor.close()
    conn.close()

# ---------- HTTP Server with Auth ----------
class RequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def _send_unauthorized(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Access to Transactions API"')
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def authenticate(self):
        auth_header = self.headers.get("Authorization")
        if auth_header is None:
            self.do_AUTHHEAD()
            return False
        auth_type, encoded = auth_header.split(" ")
        decoded = base64.b64decode(encoded).decode("utf-8")
        user, passwd = decoded.split(":")
        if user == API_USER and passwd == API_PASS:
            return True
        self.do_AUTHHEAD()
        return False

    # ------------- Endpoints -------------
    def do_GET(self):
        if not self.authenticate():
            return

        if self.path.startswith("/transactions/"):
            transaction_id = self.path.split("/")[-1]
            transaction = fetch_transaction(transaction_id)
            if transaction:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(transaction, default=str).encode())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Transaction not found")
        elif self.path == "/transactions":
            transactions = fetch_all_transactions()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(transactions, default=str).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self.authenticate():
            return
        if self.path == "/transactions":
            data = self.parse_json_body()
            insert_transaction(data)
            self.send_response(201)
            self.end_headers()
            self.wfile.write(b"Transaction created")
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if not self.authenticate():
            return
        if self.path.startswith("/transactions/"):
            transaction_id = self.path.split("/")[-1]
            data = self.parse_json_body()
            update_transaction(transaction_id, data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Transaction updated")
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if not self.authenticate():
            return
        if self.path.startswith("/transactions/"):
            transaction_id = self.path.split("/")[-1]
            delete_transaction(transaction_id)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Transaction deleted")
        else:
            self.send_response(404)
            self.end_headers()


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f" Server running at http://localhost:{port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
