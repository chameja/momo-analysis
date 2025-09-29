import json
import mysql.connector
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the root folder (one level up from current file)
root_path = Path(__file__).resolve().parent.parent  # parent of parent

# Load the .env file from the root folder
load_dotenv(dotenv_path=root_path / ".env")


# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# ---------- Helper DB functions ----------
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_all_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT deposit_id AS id, 'Deposit' AS type, customer_id, amount, time_stamp, readable_date, new_balance
    FROM Deposit
    UNION
    SELECT withdrawal_id, 'Withdrawal', customer_id, amount, time_stamp, readable_date, new_balance
    FROM Withdrawal
    UNION
    SELECT transfer_id, 'Transfer', sender_log_id, amount, NULL, NULL, new_balance
    FROM Transfer
    UNION
    SELECT payment_id, 'Payment', sender_log_id, amount, time_stamp, readable_date, new_balance
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
        if txn["id"] == txn_id:
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
    return True

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
    return True

def delete_transaction(txn_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM Deposit WHERE deposit_id=%s"
    cursor.execute(query, (txn_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return True

# ---------- HTTP Server ----------
class RequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        path_parts = self.path.strip("/").split("/")

        if self.path == "/transactions":
            transactions = fetch_all_transactions()
            self._set_headers()
            self.wfile.write(json.dumps(transactions, default=str).encode())

        elif len(path_parts) == 2 and path_parts[0] == "transactions":
            txn_id = path_parts[1]
            txn = fetch_transaction_by_id(txn_id)
            if txn:
                self._set_headers()
                self.wfile.write(json.dumps(txn, default=str).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Transaction not found"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/transactions":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            insert_transaction(data)

            self._set_headers(201)
            self.wfile.write(json.dumps({"message": "Transaction created"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_PUT(self):
        path_parts = self.path.strip("/").split("/")
        if len(path_parts) == 2 and path_parts[0] == "transactions":
            txn_id = path_parts[1]
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            update_transaction(txn_id, data)

            self._set_headers(200)
            self.wfile.write(json.dumps({"message": "Transaction updated"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_DELETE(self):
        path_parts = self.path.strip("/").split("/")
        if len(path_parts) == 2 and path_parts[0] == "transactions":
            txn_id = path_parts[1]
            delete_transaction(txn_id)

            self._set_headers(200)
            self.wfile.write(json.dumps({"message": "Transaction deleted"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

# ---------- Run server ----------
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"✅ Server running at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
