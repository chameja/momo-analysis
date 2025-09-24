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