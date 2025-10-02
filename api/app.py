import base64
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# Load environment variables
root_path = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root_path / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")

TABLE_ID_MAP = {
    "Deposit": "deposit_id",
    "Withdrawal": "withdraw_id",
    "Transfer": "transfer_id",
    "Payment": "payment_id"
}


# Database helper functions
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Merge transactions from all tables
    query = """
    SELECT deposit_id AS transaction_id, customer_id, 'Deposit' AS type, amount, new_balance, time_stamp, readable_date
    FROM Deposit
    UNION ALL
    SELECT withdraw_id AS transaction_id, customer_id, 'Withdrawal' AS type, amount, new_balance, time_stamp, readable_date
    FROM Withdrawal
    UNION ALL
    SELECT transfer_id AS transaction_id, NULL AS customer_id, 'Transfer' AS type, amount, new_balance, NULL AS time_stamp, NULL AS readable_date
    FROM Transfer
    UNION ALL
    SELECT payment_id AS transaction_id, NULL AS customer_id, 'Payment' AS type, amount, new_balance, time_stamp, readable_date
    FROM Payment
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def fetch_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    TABLE_ID_MAP = {
        "Deposit": "deposit_id",
        "Withdrawal": "withdraw_id",
        "Transfer": "transfer_id",
        "Payment": "payment_id"
    }

    for table, id_field in TABLE_ID_MAP.items():
        cursor.execute(f"SELECT * FROM {table} WHERE {id_field} = %s", (transaction_id,))
        result = cursor.fetchone()
        if result:
            cursor.close()
            conn.close()
            return {"type": table, "data": result}

    cursor.close()
    conn.close()
    return None



def insert_transaction(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    table = data.get("type")
    if table == "Deposit":
        cursor.execute(
            """
            INSERT INTO Deposit (deposit_id, customer_id, amount, time_stamp, readable_date, new_balance)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data["transaction_id"],
                data.get("customer_id"),
                data["amount"],
                data["time_stamp"],
                data.get("readable_date"),
                data.get("new_balance"),
            ),
        )
    elif table == "Withdrawal":
        cursor.execute(
            """
            INSERT INTO Withdrawal (withdraw_id, customer_id, agent_id, amount, fee, new_balance, time_stamp, readable_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["transaction_id"],
                data.get("customer_id"),
                data.get("agent_id"),
                data["amount"],
                data.get("fee"),
                data.get("new_balance"),
                data["time_stamp"],
                data.get("readable_date"),
            ),
        )
    elif table == "Transfer":
        cursor.execute(
            """
            INSERT INTO Transfer (transfer_id, sender_log_id, receiver_log_id, amount, fee, recipient_name, recipient_number, new_balance, transfer_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["transaction_id"],
                data.get("sender_log_id"),
                data.get("receiver_log_id"),
                data["amount"],
                data.get("fee"),
                data.get("recipient_name"),
                data.get("recipient_number"),
                data.get("new_balance"),
                data.get("transfer_type"),
            ),
        )
    elif table == "Payment":
        print(data)
        cursor.execute(
            """
            INSERT INTO Payment (payment_id, sender_log_id, receiver_log_id, amount, fee, new_balance, time_stamp, readable_date, payment_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["transaction_id"],
                data.get("sender_log_id"),
                data.get("receiver_log_id"),
                data["amount"],
                data.get("fee"),
                data.get("new_balance"),
                data["time_stamp"],
                data.get("readable_date"),
                data.get("payment_type"),
            ),
        )
    else:
        raise ValueError("Unknown transaction type")

    conn.commit()
    cursor.close()
    conn.close()


def update_transaction(transaction_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()

    table = data.get("type")
    if table == "Deposit":
        cursor.execute(
            """
            UPDATE Deposit SET customer_id=%s, amount=%s, new_balance=%s, time_stamp=%s, readable_date=%s
            WHERE deposit_id=%s
            """,
            (
                data.get("customer_id"),
                data.get("amount"),
                data.get("new_balance"),
                data.get("time_stamp"),
                data.get("readable_date"),
                transaction_id,
            ),
        )
    elif table == "Withdrawal":
        cursor.execute(
            """
            UPDATE Withdrawal SET customer_id=%s, agent_id=%s, amount=%s, fee=%s, new_balance=%s, time_stamp=%s, readable_date=%s
            WHERE withdraw_id=%s
            """,
            (
                data.get("customer_id"),
                data.get("agent_id"),
                data.get("amount"),
                data.get("fee"),
                data.get("new_balance"),
                data.get("time_stamp"),
                data.get("readable_date"),
                transaction_id,
            ),
        )
    elif table == "Transfer":
        cursor.execute(
            """
            UPDATE Transfer SET sender_log_id=%s, receiver_log_id=%s, amount=%s, fee=%s, recipient_name=%s, recipient_number=%s, new_balance=%s, transfer_type=%s
            WHERE transfer_id=%s
            """,
            (
                data.get("sender_log_id"),
                data.get("receiver_log_id"),
                data.get("amount"),
                data.get("fee"),
                data.get("recipient_name"),
                data.get("recipient_number"),
                data.get("new_balance"),
                data.get("transfer_type"),
                transaction_id,
            ),
        )
    elif table == "Payment":
        cursor.execute(
            """
            UPDATE Payment SET sender_log_id=%s, receiver_log_id=%s, amount=%s, fee=%s, new_balance=%s, time_stamp=%s, readable_date=%s, payment_type=%s
            WHERE payment_id=%s
            """,
            (
                data.get("sender_log_id"),
                data.get("receiver_log_id"),
                data.get("amount"),
                data.get("fee"),
                data.get("new_balance"),
                data.get("time_stamp"),
                data.get("readable_date"),
                data.get("payment_type"),
                transaction_id,
            ),
        )
    else:
        raise ValueError("Unknown transaction type")

    conn.commit()
    cursor.close()
    conn.close()


def delete_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    for table, id_field in TABLE_ID_MAP.items():
        cursor.execute(f"DELETE FROM {table} WHERE {id_field}=%s", (transaction_id,))

    conn.commit()
    cursor.close()
    conn.close()

# HTTP Request Handler
class RequestHandler(BaseHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="SMS API"')
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

    def parse_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body)

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


# Run the server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()