-- Drop the database if it already exists
DROP DATABASE IF EXISTS momo_analysis;

-- Create Database
CREATE DATABASE momo_analysis;
USE momo_analysis;

-- Customer Table
CREATE TABLE Customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(50) NOT NULL,
    customer_number INT(12) UNIQUE NOT NULL
);

-- Agent Table
CREATE TABLE Agent (
    agent_id VARCHAR(50) PRIMARY KEY,
    agent_name VARCHAR(50) NOT NULL,
    agent_number INT(12) UNIQUE NOT NULL
);

-- Deposit Table
CREATE TABLE Deposit (
    deposit_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    amount FLOAT(12,2) NOT NULL,
    time_stamp DATETIME NOT NULL,
    readable_date VARCHAR(50),
    new_balance FLOAT(12,2),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Withdrawal Table
CREATE TABLE Withdrawal (
    withdraw_id VARCHAR(50) PRIMARY KEY,
    agent_id VARCHAR(50),
    customer_id VARCHAR(50),
    amount FLOAT(12,2) NOT NULL,
    fee FLOAT(12,2),
    new_balance FLOAT(12,2),
    time_stamp DATETIME NOT NULL,
    readable_date VARCHAR(50),
    FOREIGN KEY (agent_id) REFERENCES Agent(agent_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Sender Log Table
CREATE TABLE Sender_Log (
    sender_log_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    transaction_type ENUM('Payment', 'Transfer') NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Receiver Log Table
CREATE TABLE Receiver_Log (
    receiver_log_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    transaction_type ENUM('Payment', 'Transfer') NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- Transfer Table
CREATE TABLE Transfer (
    transfer_id VARCHAR(50) PRIMARY KEY,
    receiver_log_id VARCHAR(50),
    sender_log_id VARCHAR(50),
    amount FLOAT(12,2) NOT NULL,
    fee FLOAT(12,2),
    recipient_name VARCHAR(50),
    recipient_number INT(10),
    new_balance FLOAT(12,2),
    transfer_type ENUM('Receive', 'Send'),
    FOREIGN KEY (receiver_log_id) REFERENCES Receiver_Log(receiver_log_id),
    FOREIGN KEY (sender_log_id) REFERENCES Sender_Log(sender_log_id)
);

-- Payment Table
CREATE TABLE Payment (
    payment_id VARCHAR(50) PRIMARY KEY,
    receiver_log_id VARCHAR(50),
    sender_log_id VARCHAR(50),
    amount FLOAT(12,2) NOT NULL,
    fee FLOAT(12,2),
    new_balance FLOAT(12,2),
    time_stamp DATETIME NOT NULL,
    readable_date VARCHAR(50),
    payment_type ENUM('Bill', 'Utility', 'Airtime', 'Data', 'Merchant'),
    FOREIGN KEY (receiver_log_id) REFERENCES Receiver_Log(receiver_log_id),
    FOREIGN KEY (sender_log_id) REFERENCES Sender_Log(sender_log_id)
);
