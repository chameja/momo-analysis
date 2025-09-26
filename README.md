## Team: 001s
---
# Project: Momo Analysis

### Description
Momo Analysis is a project designed to analyze Mobile Money (MoMo) SMS data for actionable insights into customer transactions, agent activities, and financial flows. The system is built with a normalized relational database and supports various transaction types, including deposits, withdrawals, transfers, and payments.

---

## Table of Contents
- [Team Members](#team-members)
- [Database Design](#database-design)
- [Entity Relationship Diagram (ERD)](#entity-relationship-diagram-erd)
- [Recent Changes](#recent-changes)
- [Sample Data](#sample-data)
- [How to Use](#how-to-use)
- [Project Board](#project-board)

---

## Team Members

| Name                |
| --------------------|
| Chipo Hameja        |
| Peter Opara         |
| Jabes Nshuti Ruranga|
| Emmanuel Akinloye   |

---

## Database Design

The database is designed to efficiently store and manage MoMo transaction data. The schema is defined in [`database/database_setup.sql`](database/database_setup.sql) and includes the following tables:

- **Customer**: Stores customer details such as ID, full name, phone number, email, and registration date.
- **Agent**: Contains agent information including ID, full name, phone number, location, and registration date.
- **Transaction**: Central table for all transactions, referencing both customer and agent, and storing transaction type, amount, fee, and timestamp.
- **Deposit, Withdrawal, Transfer, Payment**: Specialized tables for each transaction type, each referencing the main Transaction table and storing additional attributes specific to the transaction type.
- **Sender_Log & Receiver_Log**: Track sender and receiver activities for transfers and payments, enabling detailed participant tracking.

The schema enforces data integrity through primary and foreign key constraints, and includes indexes for efficient querying.

---

## Entity Relationship Diagram (ERD)

The ERD below visually represents the relationships between the tables in the database:

![Draft HRD Architecture Diagram](https://github.com/chameja/momo-analysis/blob/main/momo_hld.png "Draft HRD Architecture Diagram")

**Key Points:**
- Customers and agents are linked to transactions.
- Each transaction type (Deposit, Withdrawal, Transfer, Payment) has its own table for specific details.
- Sender and receiver logs enable tracking of transaction participants for audit and analysis.

---

## Recent Changes

- **Database Schema Update:**  
  - Normalized the schema for better data integrity and scalability.
  - Added foreign key constraints and indexes.
  - Created specialized tables for each transaction type.
  - Added sender and receiver logs for detailed tracking.
- **Sample Data:**  
  - Populated all main tables with realistic sample data for testing and demonstration.
- **ERD:**  
  - Updated and included a comprehensive ERD diagram reflecting the current schema.
- **JSON Example:**  
  - Added [`examples/json_schemas.json`](examples/json_schemas.json) to illustrate the data structure for customers, agents, and transactions.

---

## Sample Data

Sample data is provided in the SQL setup script and as a JSON file:

- [`database/database_setup.sql`](database/database_setup.sql): Contains SQL statements to create tables and insert sample records.
- [`examples/json_schemas.json`](examples/json_schemas.json): Shows example data for customers, agents, and transactions in JSON format.

---

## How to Use

1. **Set up the database:**  
   Run the SQL script in [`database/database_setup.sql`](database/database_setup.sql) to create and populate the schema.
2. **Review the ERD:**  
   Refer to the ERD diagram above for a visual overview of the database structure.
3. **Explore sample data:**  
   Use the JSON file for data format reference and testing.

---

## Project Board

[Project Board](https://github.com/users/chameja/projects/1/views/1)

## ERd drawing pdf

[text](docs/momo_analysis_erd.pdf)

# ERD Design Rationale and Justification

The provided Entity Relationship Diagram (ERD) represents the structure of a financial system involving customers, agents, and various financial transactions such as deposits, withdrawals, payments, and transfers. Below is a detailed breakdown of the design rationale and justification for the ERD.

## 1. Entities and Their Relationships

### **Customer**
- The **Customer** entity represents individuals using the financial system.
- The `customer_id` serves as the primary key, ensuring unique identification of customers.
- Customers can participate in transactions such as deposits, withdrawals, payments, and transfers.

### **Agent**
- The **Agent** entity represents the intermediaries or facilitators for customer transactions, typically involved in withdrawals.
- The `agent_id` is the primary key for this entity.
- An agent can be linked to multiple withdrawal transactions.

### **Deposit**
- The **Deposit** entity represents a deposit transaction made by a customer.
- It stores information such as the deposit amount, timestamp, and the updated account balance (`new_balance`) after the deposit.
- Each deposit is linked to a specific `customer_id` through a foreign key.

### **Withdrawal**
- The **Withdrawal** entity represents a withdrawal made by a customer through an agent.
- This entity records the transaction amount, associated fee, and the new balance after the transaction.
- The `agent_id` and `customer_id` act as foreign keys, indicating the involved parties.

### **Transfer**
- The **Transfer** entity captures transfer transactions where one customer sends money to another.
- It includes foreign keys to `receiver_log_id` and `sender_log_id` linking to sender and receiver logs.
- The entity records details like the amount transferred, transaction fee, recipient information, and new balance after the transfer.

### **Payment**
- The **Payment** entity represents a payment made by a customer to another entity or individual.
- Similar to transfers, payments involve both a sender and a receiver.
- This entity tracks the amount, fee, new balance, and timestamps for each payment.

### **Receiver Log and Sender Log**
- **Receiver Log** and **Sender Log** track the sender and receiver of transactions.
- These logs store `customer_id` and `transaction_type` (e.g., Payment, Transfer).
- Both log entities are linked to the `Transfer` and `Payment` tables to ensure proper transaction flow.

## 2. Relationship Design

- **One-to-Many (1:N)** relationships are defined between customers and deposits, withdrawals, transfers, and payments. A customer can have multiple transactions in each of these categories.
- **Many-to-One (N:1)** relationships exist between the `Transfer` and `Sender Log` and `Receiver Log` entities, ensuring that multiple transactions can be linked to a single sender or receiver.
- **Many-to-Many (M:N)** relationships are maintained between customers and transactions like `Transfer`, `Payment`, and `Withdrawal` through the use of log tables, which store metadata about the transactions without redundantly duplicating customer data.

## 3. Normalization and Data Integrity

- The schema adheres to **normalization** principles to avoid redundancy and maintain data integrity. This is evident in the use of separate transaction and log entities (e.g., `Receiver Log`, `Sender Log`) that store unique transactional details.
- **Foreign Key Constraints** ensure that each transaction type (deposit, transfer, payment, withdrawal) is correctly associated with the appropriate customer and agent, preserving referential integrity and preventing invalid records.

## 4. Timestamp and Readable Date Fields

- The use of `time_stamp` and `readable_date` in various entities (Deposit, Transfer, Payment, Withdrawal) is essential for tracking when each transaction occurs.
- The `time_stamp` provides a precise date-time format for each transaction, while the `readable_date` offers a more user-friendly format for easier reporting.

## 5. Enums for Transaction Types

- The `transaction_type` field in both the `Receiver Log` and `Sender Log` tables uses **ENUM** to specify possible transaction types (e.g., Payment, Transfer).
- This ensures that only valid transaction types are recorded, which helps maintain data consistency.

## 6. Use of Fees and New Balance

- Both the `Transfer`, `Payment`, and `Withdrawal` entities include fields for `fee` and `new_balance`.
- This reflects the financial nature of the system, where every transaction can affect the account balance and may involve a transaction fee.
- These fields ensure the system can correctly calculate and update the balance after each transaction.

## Conclusion

The ERD design effectively supports a financial system by capturing key entities (Customer, Agent, Transaction Types) and their relationships. The design emphasizes:
- **Data Integrity**: Using foreign key constraints and normalization to avoid redundancy.
- **Transaction Tracking**: Maintaining proper logging of sender and receiver transactions.
- **Timestamping**: Ensuring accurate tracking of when transactions occur.
- **Fee and Balance Management**: Properly handling financial data, such as fees and updated balances.

This structure ensures that the system can track customer financial activities, manage various transaction types, and allow for effective querying and reporting on customer balances and transaction histories.