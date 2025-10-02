import json
import mysql.connector
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from dotenv import load_dotenv
from pathlib import Path
import base64

# ---------------- Load Environment Variables ----------------
root_path = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_path / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")


# ---------------- Database Helpers ----------------
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT deposit_id AS id, 'Deposit' AS type, customer_id, amount, time_stamp, readable_date, new_balance
    FROM Deposit
    UNION
    SELECT withdraw_id AS id, 'Withdrawal' AS type, customer_id, amount, time_stamp, readable_date, new_balance
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

    query = """INSERT INTO Deposit (deposit_id, customer_id, amount, time_stamp, readable_date, new_balance)
               VALUES (%s, %s, %s, NOW(), %s, %s)"""
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

    query = """UPDATE Deposit
               SET amount=%s, readable_date=%s, new_balance=%s
               WHERE deposit_id=%s"""
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


# ---------------- HTTP Server ----------------
class RequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def _send_unauthorized(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Access to Transactions API"')
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())

    def _check_auth(self):
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            self._send_unauthorized()
            return False

        encoded_creds = auth_header.split(" ")[1]
        try:
            decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
            username, password = decoded_creds.split(":", 1)
        except Exception:
            self._send_unauthorized()
            return False

        if username == API_USER and password == API_PASS:
            return True
        else:
            self._send_unauthorized()
            return False

    # ---------------- API Endpoints ----------------
    def do_GET(self):
        if not self._check_auth():
            return

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
        if not self._check_auth():
            return

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
        if not self._check_auth():
            return

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
        if not self._check_auth():
            return

        path_parts = self.path.strip("/").split("/")
        if len(path_parts) == 2 and path_parts[0] == "transactions":
            txn_id = path_parts[1]
            delete_transaction(txn_id)

            self._set_headers(200)
            self.wfile.write(json.dumps({"message": "Transaction deleted"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


# ---------------- Run Server ----------------
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"🚀 Server running at http://localhost:{port}/")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
