import xml.etree.ElementTree as ET
import json
import re
import os
from collections import defaultdict
from datetime import datetime

# Paths
XML_PATH = os.path.join("data", "raw", "momo.xml")
OUTPUT_PATH = os.path.join("data", "processed", "formatted_data.json")

# Helper functions for ID generation
def make_id(prefix, idx):
    return f"{prefix}{idx:05d}"

def parse_amount(text):
    # Extracts the first number (float or int) from a string
    match = re.search(r"([\d,]+(?:\.\d+)?)", text.replace(",", ""))
    return float(match.group(1)) if match else 0.0

def parse_phone(text):
    # Extracts a phone number from a string
    match = re.search(r"(\d{9,12})", text)
    return match.group(1) if match else None

def parse_date(ts):
    # Converts timestamp (ms) to ISO format
    try:
        return datetime.fromtimestamp(int(ts) / 1000).isoformat(sep=" ", timespec="seconds")
    except Exception:
        return None

def clean_name(name):
    return name.strip().title() if name else None

# Data containers
data = {
    "Customer": [],
    "Agent": [],
    "Deposit": [],
    "Withdrawal": [],
    "Sender_Log": [],
    "Receiver_Log": [],
    "Transfer": [],
    "Payment": []
}

# Indexes for deduplication
customer_map = {}
agent_map = {}
sender_log_map = {}
receiver_log_map = {}

customer_idx = 1
agent_idx = 1
sender_log_idx = 1
receiver_log_idx = 1
deposit_idx = 1
withdraw_idx = 1
transfer_idx = 1
payment_idx = 1

# Parse XML
context = ET.iterparse(XML_PATH, events=("end",))
for event, elem in context:
    if elem.tag != "sms":
        continue
    attrib = elem.attrib
    body = attrib.get("body", "")
    readable_date = attrib.get("readable_date", "")
    date = attrib.get("date", "")
    date_sent = attrib.get("date_sent", "")
    # Transaction type detection
    # Deposit
    if re.search(r"deposit of", body, re.I):
        # Example: "A bank deposit of 40000 RWF has been added..."
        amount = parse_amount(body)
        new_balance = parse_amount(re.search(r"new balance[: ]*([\d,]+)", body, re.I).group(1)) if re.search(r"new balance[: ]*([\d,]+)", body, re.I) else None
        customer_name = None
        customer_number = None
        # Try to extract customer from context (not always present)
        cust_key = "self"
        if cust_key not in customer_map:
            customer_id = make_id("C", customer_idx)
            customer_map[cust_key] = customer_id
            data["Customer"].append({
                "customer_id": customer_id,
                "customer_name": "Self",
                "customer_number": 36521838  # fallback or dummy
            })
            customer_idx += 1
        deposit_id = make_id("D", deposit_idx)
        data["Deposit"].append({
            "deposit_id": deposit_id,
            "customer_id": customer_map[cust_key],
            "amount": amount,
            "time_stamp": parse_date(date),
            "readable_date": readable_date,
            "new_balance": new_balance
        })
        deposit_idx += 1
    # Withdrawal
    elif re.search(r"withdrawn|withdrawal", body, re.I):
        # Example: "withdrawn 20000 RWF from your mobile money account... via agent: Agent Sophia (250790777777)"
        amount = parse_amount(body)
        fee = parse_amount(re.search(r"Fee paid: ([\d,]+)", body, re.I).group(1)) if re.search(r"Fee paid: ([\d,]+)", body, re.I) else None
        new_balance = parse_amount(re.search(r"new balance[: ]*([\d,]+)", body, re.I).group(1)) if re.search(r"new balance[: ]*([\d,]+)", body, re.I) else None
        agent_match = re.search(r"agent: ([\w ]+) \((\d+)\)", body)
        agent_name = clean_name(agent_match.group(1)) if agent_match else None
        agent_number = agent_match.group(2) if agent_match else None
        if agent_number and agent_number not in agent_map:
            agent_id = make_id("A", agent_idx)
            agent_map[agent_number] = agent_id
            data["Agent"].append({
                "agent_id": agent_id,
                "agent_name": agent_name or "Unknown",
                "agent_number": int(agent_number)
            })
            agent_idx += 1
        cust_key = "self"
        if cust_key not in customer_map:
            customer_id = make_id("C", customer_idx)
            customer_map[cust_key] = customer_id
            data["Customer"].append({
                "customer_id": customer_id,
                "customer_name": "Self",
                "customer_number": 36521838
            })
            customer_idx += 1
        withdraw_id = make_id("W", withdraw_idx)
        data["Withdrawal"].append({
            "withdraw_id": withdraw_id,
            "agent_id": agent_map.get(agent_number),
            "customer_id": customer_map[cust_key],
            "amount": amount,
            "fee": fee,
            "new_balance": new_balance,
            "time_stamp": parse_date(date),
            "readable_date": readable_date
        })
        withdraw_idx += 1
    # Transfer (Send/Receive)
    elif re.search(r"transferred to|received from", body, re.I):
        # Send: "10000 RWF transferred to Samuel Carter (250791666666) from 36521838..."
        # Receive: "You have received 2000 RWF from Jane Smith (*********013)..."
        if "transferred to" in body:
            # Send
            amount = parse_amount(body)
            fee = parse_amount(re.search(r"Fee was: ([\d,]+)", body, re.I).group(1)) if re.search(r"Fee was: ([\d,]+)", body, re.I) else None
            new_balance = parse_amount(re.search(r"New balance: ([\d,]+)", body, re.I).group(1)) if re.search(r"New balance: ([\d,]+)", body, re.I) else None
            recipient_match = re.search(r"transferred to ([\w ]+) \((\d+)\)", body)
            recipient_name = clean_name(recipient_match.group(1)) if recipient_match else None
            recipient_number = recipient_match.group(2) if recipient_match else None
            # Sender (self)
            cust_key = "self"
            if cust_key not in customer_map:
                customer_id = make_id("C", customer_idx)
                customer_map[cust_key] = customer_id
                data["Customer"].append({
                    "customer_id": customer_id,
                    "customer_name": "Self",
                    "customer_number": 36521838
                })
                customer_idx += 1
            # Receiver
            if recipient_number and recipient_number not in customer_map:
                customer_id = make_id("C", customer_idx)
                customer_map[recipient_number] = customer_id
                data["Customer"].append({
                    "customer_id": customer_id,
                    "customer_name": recipient_name or "Unknown",
                    "customer_number": int(recipient_number)
                })
                customer_idx += 1
            # Sender Log
            if cust_key not in sender_log_map:
                sender_log_id = make_id("SL", sender_log_idx)
                sender_log_map[cust_key] = sender_log_id
                data["Sender_Log"].append({
                    "sender_log_id": sender_log_id,
                    "customer_id": customer_map[cust_key],
                    "transaction_type": "Transfer"
                })
                sender_log_idx += 1
            # Receiver Log
            if recipient_number and recipient_number not in receiver_log_map:
                receiver_log_id = make_id("RL", receiver_log_idx)
                receiver_log_map[recipient_number] = receiver_log_id
                data["Receiver_Log"].append({
                    "receiver_log_id": receiver_log_id,
                    "customer_id": customer_map[recipient_number],
                    "transaction_type": "Transfer"
                })
                receiver_log_idx += 1
            transfer_id = make_id("T", transfer_idx)
            data["Transfer"].append({
                "transfer_id": transfer_id,
                "receiver_log_id": receiver_log_map.get(recipient_number),
                "sender_log_id": sender_log_map.get(cust_key),
                "amount": amount,
                "fee": fee,
                "recipient_name": recipient_name,
                "recipient_number": int(recipient_number) if recipient_number else None,
                "new_balance": new_balance,
                "transfer_type": "Send"
            })
            transfer_idx += 1
        elif "received from" in body:
            # Receive
            amount = parse_amount(body)
            new_balance = parse_amount(re.search(r"new balance[: ]*([\d,]+)", body, re.I).group(1)) if re.search(r"new balance[: ]*([\d,]+)", body, re.I) else None
            sender_match = re.search(r"received ([\d,]+) RWF from ([\w ]+) \((\*+\d+)\)", body)
            sender_name = clean_name(sender_match.group(2)) if sender_match else None
            sender_number = sender_match.group(3) if sender_match else None
            # Receiver (self)
            cust_key = "self"
            if cust_key not in customer_map:
                customer_id = make_id("C", customer_idx)
                customer_map[cust_key] = customer_id
                data["Customer"].append({
                    "customer_id": customer_id,
                    "customer_name": "Self",
                    "customer_number": 36521838
                })
                customer_idx += 1
            # Sender
            if sender_number and sender_number not in customer_map:
                customer_id = make_id("C", customer_idx)
                customer_map[sender_number] = customer_id
                data["Customer"].append({
                    "customer_id": customer_id,
                    "customer_name": sender_name or "Unknown",
                    "customer_number": None
                })
                customer_idx += 1
            # Sender Log
            if sender_number and sender_number not in sender_log_map:
                sender_log_id = make_id("SL", sender_log_idx)
                sender_log_map[sender_number] = sender_log_id
                data["Sender_Log"].append({
                    "sender_log_id": sender_log_id,
                    "customer_id": customer_map[sender_number],
                    "transaction_type": "Transfer"
                })
                sender_log_idx += 1
            # Receiver Log
            if cust_key not in receiver_log_map:
                receiver_log_id = make_id("RL", receiver_log_idx)
                receiver_log_map[cust_key] = receiver_log_id
                data["Receiver_Log"].append({
                    "receiver_log_id": receiver_log_id,
                    "customer_id": customer_map[cust_key],
                    "transaction_type": "Transfer"
                })
                receiver_log_idx += 1
            transfer_id = make_id("T", transfer_idx)
            data["Transfer"].append({
                "transfer_id": transfer_id,
                "receiver_log_id": receiver_log_map.get(cust_key),
                "sender_log_id": sender_log_map.get(sender_number),
                "amount": amount,
                "fee": None,
                "recipient_name": "Self",
                "recipient_number": 36521838,
                "new_balance": new_balance,
                "transfer_type": "Receive"
            })
            transfer_idx += 1
    # Payment
    elif re.search(r"Your payment of", body, re.I):
        # Example: "Your payment of 1,000 RWF to Jane Smith 12845 has been completed..."
        amount = parse_amount(body)
        fee = parse_amount(re.search(r"Fee was ([\d,]+)", body, re.I).group(1)) if re.search(r"Fee was ([\d,]+)", body, re.I) else None
        new_balance = parse_amount(re.search(r"new balance[: ]*([\d,]+)", body, re.I).group(1)) if re.search(r"new balance[: ]*([\d,]+)", body, re.I) else None
        receiver_match = re.search(r"to ([\w ]+) (\d{3,})", body)
        receiver_name = clean_name(receiver_match.group(1)) if receiver_match else None
        receiver_number = receiver_match.group(2) if receiver_match else None
        # Sender (self)
        cust_key = "self"
        if cust_key not in customer_map:
            customer_id = make_id("C", customer_idx)
            customer_map[cust_key] = customer_id
            data["Customer"].append({
                "customer_id": customer_id,
                "customer_name": "Self",
                "customer_number": 36521838
            })
            customer_idx += 1
        # Receiver
        if receiver_number and receiver_number not in customer_map:
            customer_id = make_id("C", customer_idx)
            customer_map[receiver_number] = customer_id
            data["Customer"].append({
                "customer_id": customer_id,
                "customer_name": receiver_name or "Unknown",
                "customer_number": int(receiver_number)
            })
            customer_idx += 1
        # Sender Log
        if cust_key not in sender_log_map:
            sender_log_id = make_id("SL", sender_log_idx)
            sender_log_map[cust_key] = sender_log_id
            data["Sender_Log"].append({
                "sender_log_id": sender_log_id,
                "customer_id": customer_map[cust_key],
                "transaction_type": "Payment"
            })
            sender_log_idx += 1
        # Receiver Log
        if receiver_number and receiver_number not in receiver_log_map:
            receiver_log_id = make_id("RL", receiver_log_idx)
            receiver_log_map[receiver_number] = receiver_log_id
            data["Receiver_Log"].append({
                "receiver_log_id": receiver_log_id,
                "customer_id": customer_map[receiver_number],
                "transaction_type": "Payment"
            })
            receiver_log_idx += 1
        payment_id = make_id("P", payment_idx)
        data["Payment"].append({
            "payment_id": payment_id,
            "receiver_log_id": receiver_log_map.get(receiver_number),
            "sender_log_id": sender_log_map.get(cust_key),
            "amount": amount,
            "fee": fee,
            "new_balance": new_balance,
            "time_stamp": parse_date(date),
            "readable_date": readable_date,
            "payment_type": None
        })
        payment_idx += 1
    # Clean up
    elem.clear()

# Write output
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Formatted data written to {OUTPUT_PATH}")
