import json
from dotenv import load_dotenv
import os
import mysql.connector

# Update these with your MySQL credentials
MYSQL_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

JSON_PATH = "data/processed/formatted_data.json"

# Load JSON data
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Connect to MySQL
conn = mysql.connector.connect(**MYSQL_CONFIG)
cur = conn.cursor()

# Insert Customers
for cust in data["Customer"]:
    cur.execute(
        "INSERT IGNORE INTO Customer (customer_id, customer_name, customer_number) VALUES (%s, %s, %s)",
        (cust["customer_id"], cust["customer_name"], cust["customer_number"])
    )

# Insert Agents
for agent in data["Agent"]:
    cur.execute(
        "INSERT IGNORE INTO Agent (agent_id, agent_name, agent_number) VALUES (%s, %s, %s)",
        (agent["agent_id"], agent["agent_name"], agent["agent_number"])
    )

# Insert Deposits
for dep in data["Deposit"]:
    cur.execute(
        "INSERT IGNORE INTO Deposit (deposit_id, customer_id, amount, time_stamp, readable_date, new_balance) VALUES (%s, %s, %s, %s, %s, %s)",
        (dep["deposit_id"], dep["customer_id"], dep["amount"], dep["time_stamp"], dep["readable_date"], dep["new_balance"])
    )

# Insert Withdrawals
for wd in data["Withdrawal"]:
    cur.execute(
        "INSERT IGNORE INTO Withdrawal (withdraw_id, agent_id, customer_id, amount, fee, new_balance, time_stamp, readable_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (wd["withdraw_id"], wd["agent_id"], wd["customer_id"], wd["amount"], wd["fee"], wd["new_balance"], wd["time_stamp"], wd["readable_date"])
    )

# Insert Sender_Log
for sl in data["Sender_Log"]:
    cur.execute(
        "INSERT IGNORE INTO Sender_Log (sender_log_id, customer_id, transaction_type) VALUES (%s, %s, %s)",
        (sl["sender_log_id"], sl["customer_id"], sl["transaction_type"])
    )

# Insert Receiver_Log
for rl in data["Receiver_Log"]:
    cur.execute(
        "INSERT IGNORE INTO Receiver_Log (receiver_log_id, customer_id, transaction_type) VALUES (%s, %s, %s)",
        (rl["receiver_log_id"], rl["customer_id"], rl["transaction_type"])
    )

# Insert Transfers
for tr in data["Transfer"]:
    cur.execute(
        "INSERT IGNORE INTO Transfer (transfer_id, receiver_log_id, sender_log_id, amount, fee, recipient_name, recipient_number, new_balance, transfer_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (tr["transfer_id"], tr["receiver_log_id"], tr["sender_log_id"], tr["amount"], tr["fee"], tr["recipient_name"], tr["recipient_number"], tr["new_balance"], tr["transfer_type"])
    )

# Insert Payments
for pay in data["Payment"]:
    cur.execute(
        "INSERT IGNORE INTO Payment (payment_id, receiver_log_id, sender_log_id, amount, fee, new_balance, time_stamp, readable_date, payment_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (pay["payment_id"], pay["receiver_log_id"], pay["sender_log_id"], pay["amount"], pay["fee"], pay["new_balance"], pay["time_stamp"], pay["readable_date"], pay["payment_type"])
    )

conn.commit()
cur.close()
conn.close()

print("Data loaded successfully into MySQL database.")