-- Database: momo_sms

DROP DATABASE IF EXISTS momo_sms;
CREATE DATABASE momo_sms;
USE momo_sms;


/* =====================================================
   CUSTOMER TABLE
   Stores sender/receiver information
   ===================================================== */
CREATE TABLE Customer (
    customer_id     VARCHAR(10)   PRIMARY KEY COMMENT 'Unique ID for each customer',
    full_name       VARCHAR(100)  NOT NULL COMMENT 'Customer full name',
    phone_number    VARCHAR(20)   UNIQUE NOT NULL COMMENT 'Customer phone number',
    email           VARCHAR(100)  UNIQUE COMMENT 'Optional email address',
    created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT 'Customer registration date'
);

CREATE INDEX idx_customer_phone ON Customer(phone_number);


/* =====================================================
   AGENT TABLE
   Represents mobile money agents
   ===================================================== */
CREATE TABLE Agent (
    agent_id        VARCHAR(10)   PRIMARY KEY COMMENT 'Unique ID for each agent',
    full_name       VARCHAR(100)  NOT NULL COMMENT 'Agent full name',
    phone_number    VARCHAR(20)   UNIQUE NOT NULL COMMENT 'Agent phone number',
    location        VARCHAR(100)  COMMENT 'Agent location',
    created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT 'Agent registration date'
);

CREATE INDEX idx_agent_phone ON Agent(phone_number);


/* =====================================================
   TRANSACTION TABLE
   Main record of all transactions
   ===================================================== */
CREATE TABLE Transaction (
    transaction_id   VARCHAR(10)  PRIMARY KEY COMMENT 'Unique ID for each transaction',
    customer_id      VARCHAR(10)  NOT NULL COMMENT 'FK to Customer',
    agent_id         VARCHAR(10)  COMMENT 'FK to Agent if agent is involved',
    transaction_type ENUM('Deposit','Withdrawal','Transfer','Payment') NOT NULL COMMENT 'Transaction type',
    amount           DECIMAL(12,2) CHECK (amount > 0) COMMENT 'Transaction amount',
    fee              DECIMAL(12,2) DEFAULT 0 CHECK (fee >= 0) COMMENT 'Fee charged',
    transaction_date DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT 'When the transaction occurred',

    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (agent_id)    REFERENCES Agent(agent_id)
);

CREATE INDEX idx_transaction_date ON Transaction(transaction_date);


/* =====================================================
   DEPOSIT TABLE
   Holds deposit-specific attributes
   ===================================================== */
CREATE TABLE Deposit (
    deposit_id      VARCHAR(10)   PRIMARY KEY COMMENT 'Unique deposit ID',
    transaction_id  VARCHAR(10)   NOT NULL COMMENT 'FK to Transaction',
    source          VARCHAR(50)   NOT NULL COMMENT 'Deposit source (cash, bank, etc.)',

    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
        ON DELETE CASCADE
);


/* =====================================================
   WITHDRAWAL TABLE
   Holds withdrawal-specific attributes
   ===================================================== */
CREATE TABLE Withdrawal (
    withdrawal_id   VARCHAR(10)   PRIMARY KEY COMMENT 'Unique withdrawal ID',
    transaction_id  VARCHAR(10)   NOT NULL COMMENT 'FK to Transaction',
    method          VARCHAR(50)   NOT NULL COMMENT 'Withdrawal method (ATM, agent, etc.)',

    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
        ON DELETE CASCADE
);


/* =====================================================
   TRANSFER TABLE
   Holds transfer-specific attributes
   ===================================================== */
CREATE TABLE Transfer (
    transfer_id     VARCHAR(10)   PRIMARY KEY COMMENT 'Unique transfer ID',
    transaction_id  VARCHAR(10)   NOT NULL COMMENT 'FK to Transaction',
    receiver_id     VARCHAR(10)   NOT NULL COMMENT 'FK to Customer',

    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
        ON DELETE CASCADE,
    FOREIGN KEY (receiver_id)    REFERENCES Customer(customer_id)
);


/* =====================================================
   PAYMENT TABLE
   Holds payment-specific attributes
   ===================================================== */
CREATE TABLE Payment (
    payment_id      VARCHAR(10)   PRIMARY KEY COMMENT 'Unique payment ID',
    transaction_id  VARCHAR(10)   NOT NULL COMMENT 'FK to Transaction',
    category        VARCHAR(50)   NOT NULL COMMENT 'Payment category (Bills, Shopping, etc.)',

    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
        ON DELETE CASCADE
);


/* =====================================================
   SENDER LOG
   Tracks sender activity
   ===================================================== */
CREATE TABLE Sender_Log (
    log_id          INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Log entry ID',
    transaction_id  VARCHAR(10) NOT NULL COMMENT 'FK to Transaction',
    sender_id       VARCHAR(10) NOT NULL COMMENT 'FK to Customer (sender)',
    log_time        DATETIME    DEFAULT CURRENT_TIMESTAMP COMMENT 'Log timestamp',

    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
        ON DELETE CASCADE,
    FOREIGN KEY (sender_id)      REFERENCES Customer(customer_id)
);


/* =====================================================
   RECEIVER LOG
   Tracks receiver activity
   ===================================================== */
CREATE TABLE Receiver_Log (
    log_id          INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Log entry ID',
    transaction_id  VARCHAR(10) NOT NULL COMMENT 'FK to Transaction',
    receiver_id     VARCHAR(10) NOT NULL COMMENT 'FK to Customer (receiver)',
    log_time        DATETIME    DEFAULT CURRENT_TIMESTAMP COMMENT 'Log timestamp',

    FOREIGN KEY (transaction_id) REFERENCES Transaction(transaction_id)
        ON DELETE CASCADE,
    FOREIGN KEY (receiver_id)    REFERENCES Customer(customer_id)
);


/* =====================================================
   SAMPLE DATA INSERTION
   At least 5 records per main table
   ===================================================== */

-- Customers
INSERT INTO Customer (customer_id, full_name, phone_number, email) VALUES
('C001', 'AKinloye Emmanuel', '250700111111', 'akinloye@example.com'),
('C002', 'Peter Opara', '250700222222', 'peter@example.com'),
('C003', 'Charlie King', '250700333333', 'charlie@example.com'),
('C004', 'Diana Prince', '250700444444', 'diana@example.com'),
('C005', 'Ethan Hunt', '250700555555', 'ethan@example.com');

-- Agents
INSERT INTO Agent (agent_id, full_name, phone_number, location) VALUES
('A001', 'Agent One', '250710111111', 'Kigali'),
('A002', 'Agent Two', '250710222222', 'Musanze'),
('A003', 'Agent Three', '250710333333', 'Butare'),
('A004', 'Agent Four', '250710444444', 'Rubavu'),
('A005', 'Agent Five', '250710555555', 'Nyagatare');

-- Transactions
INSERT INTO Transaction (transaction_id, customer_id, agent_id, transaction_type, amount, fee) VALUES
('T001', 'C001', 'A001', 'Deposit', 50000, 500),
('T002', 'C002', 'A002', 'Withdrawal', 20000, 200),
('T003', 'C003', 'A003', 'Transfer', 15000, 150),
('T004', 'C004', 'A004', 'Payment', 8000, 80),
('T005', 'C005', 'A005', 'Deposit', 12000, 120);

-- Deposit
INSERT INTO Deposit (deposit_id, transaction_id, source) VALUES
('D001', 'T001', 'Bank'),
('D002', 'T005', 'Cash');

-- Withdrawal
INSERT INTO Withdrawal (withdrawal_id, transaction_id, method) VALUES
('W001', 'T002', 'ATM');

-- Transfer
INSERT INTO Transfer (transfer_id, transaction_id, receiver_id) VALUES
('TR001', 'T003', 'C004');

-- Payment
INSERT INTO Payment (payment_id, transaction_id, category) VALUES
('P001', 'T004', 'Shopping');

-- Sender logs
INSERT INTO Sender_Log (transaction_id, sender_id) VALUES
('T003', 'C003');

-- Receiver logs
INSERT INTO Receiver_Log (transaction_id, receiver_id) VALUES
('T003', 'C004');
