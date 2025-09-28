-- Drop and recreate the database
DROP DATABASE IF EXISTS momo_analysis;
CREATE DATABASE momo_analysis;
USE momo_analysis;

---------------------------------------------------------
-- CUSTOMER TABLE
---------------------------------------------------------
CREATE TABLE Customer (
    customer_id     VARCHAR(50) PRIMARY KEY,
    customer_name   VARCHAR(50) NOT NULL,
    customer_number VARCHAR(12) UNIQUE NOT NULL
);

---------------------------------------------------------
-- AGENT TABLE
---------------------------------------------------------
CREATE TABLE Agent (
    agent_id        VARCHAR(50) PRIMARY KEY,
    agent_name      VARCHAR(50) NOT NULL,
    agent_number    VARCHAR(12) UNIQUE NOT NULL
);

---------------------------------------------------------
-- DEPOSIT TABLE
---------------------------------------------------------
CREATE TABLE Deposit (
    deposit_id      VARCHAR(50) PRIMARY KEY,
    customer_id     VARCHAR(50) NOT NULL,
    amount          FLOAT(10,2) NOT NULL CHECK (amount > 0),
    time_stamp      DATETIME DEFAULT CURRENT_TIMESTAMP,
    readable_date   VARCHAR(50),
    new_balance     FLOAT(10,2),

    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE
);

---------------------------------------------------------
-- WITHDRAWAL TABLE
---------------------------------------------------------
CREATE TABLE Withdrawal (
    withdrawal_id   VARCHAR(50) PRIMARY KEY,
    agent_id        VARCHAR(50) NOT NULL,
    customer_id     VARCHAR(50) NOT NULL,
    amount          FLOAT(10,2) NOT NULL CHECK (amount > 0),
    fee             FLOAT(10,2) DEFAULT 0,
    new_balance     FLOAT(10,2),
    time_stamp      DATETIME DEFAULT CURRENT_TIMESTAMP,
    readable_date   VARCHAR(50),

    FOREIGN KEY (agent_id) REFERENCES Agent(agent_id)
        ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE
);

---------------------------------------------------------
-- SENDER LOG
---------------------------------------------------------
CREATE TABLE Sender_Log (
    sender_log_id   VARCHAR(50) PRIMARY KEY,
    customer_id     VARCHAR(50) NOT NULL,
    transaction_type ENUM('Payment','Transfer'),

    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE
);

---------------------------------------------------------
-- RECEIVER LOG
---------------------------------------------------------
CREATE TABLE Receiver_Log (
    receiver_log_id VARCHAR(50) PRIMARY KEY,
    customer_id     VARCHAR(50) NOT NULL,
    transaction_type ENUM('Payment','Transfer'),

    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE CASCADE
);

---------------------------------------------------------
-- TRANSFER TABLE
---------------------------------------------------------
CREATE TABLE Transfer (
    transfer_id     VARCHAR(50) PRIMARY KEY,
    receiver_log_id VARCHAR(50) NOT NULL,
    sender_log_id   VARCHAR(50) NOT NULL,
    amount          FLOAT(10,2) NOT NULL CHECK (amount > 0),
    fee             FLOAT(10,2) DEFAULT 0,
    recipient_name  VARCHAR(50),
    recipient_number INT(10),
    new_balance     FLOAT(10,2),

    FOREIGN KEY (receiver_log_id) REFERENCES Receiver_Log(receiver_log_id)
        ON DELETE CASCADE,
    FOREIGN KEY (sender_log_id) REFERENCES Sender_Log(sender_log_id)
        ON DELETE CASCADE
);

---------------------------------------------------------
-- PAYMENT TABLE
---------------------------------------------------------
CREATE TABLE Payment (
    payment_id      VARCHAR(50) PRIMARY KEY,
    receiver_log_id VARCHAR(50) NOT NULL,
    sender_log_id   VARCHAR(50) NOT NULL,
    amount          FLOAT(10,2) NOT NULL CHECK (amount > 0),
    fee             FLOAT(10,2) DEFAULT 0,
    new_balance     FLOAT(10,2),
    time_stamp      DATETIME DEFAULT CURRENT_TIMESTAMP,
    readable_date   VARCHAR(50),

    FOREIGN KEY (receiver_log_id) REFERENCES Receiver_Log(receiver_log_id)
        ON DELETE CASCADE,
    FOREIGN KEY (sender_log_id) REFERENCES Sender_Log(sender_log_id)
        ON DELETE CASCADE
);

---------------------------------------------------------
-- SAMPLE DATA
---------------------------------------------------------
-- Customers
INSERT INTO Customer VALUES
('C001', 'Alice', '250700111111'),
('C002', 'Bob', '250700222222');

-- Agents
INSERT INTO Agent VALUES
('A001', 'Agent One', '250710111111'),
('A002', 'Agent Two', '250710222222');

-- Deposits
INSERT INTO Deposit (deposit_id, customer_id, amount, readable_date, new_balance) VALUES
('D001', 'C001', 50000, '2025-09-28', 50000);

-- Withdrawals
INSERT INTO Withdrawal (withdrawal_id, agent_id, customer_id, amount, fee, readable_date, new_balance) VALUES
('W001', 'A001', 'C001', 10000, 100, '2025-09-28', 40000);

-- Logs
INSERT INTO Sender_Log VALUES ('SL001', 'C001', 'Transfer');
INSERT INTO Receiver_Log VALUES ('RL001', 'C002', 'Transfer');

-- Transfer
INSERT INTO Transfer VALUES ('T001', 'RL001', 'SL001', 15000, 150, 'Bob', 250700222222, 55000);

-- Payment
INSERT INTO Payment VALUES ('P001', 'RL001', 'SL001', 8000, 80, 47000, NOW(), '2025-09-28');
