/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
indexes.sql

Purpose:
Performance Optimization using SQL Indexes

Author:
Garvit Mehta

=========================================================
*/


/*
---------------------------------------------------------
INDEX: LoanID
Purpose:
Speeds up LoanID based searches and joins.
---------------------------------------------------------
*/

CREATE INDEX idx_loanid
ON auto_loan_securitisation_data(LoanID);


/*
---------------------------------------------------------
INDEX: PoolID
Purpose:
Speeds up pool level securitisation analysis.
---------------------------------------------------------
*/

CREATE INDEX idx_poolid
ON auto_loan_securitisation_data(PoolID);


/*
---------------------------------------------------------
INDEX: BorrowerID
Purpose:
Speeds up borrower level analysis.
---------------------------------------------------------
*/

CREATE INDEX idx_borrowerid
ON auto_loan_securitisation_data(BorrowerID);


/*
---------------------------------------------------------
INDEX: Region
Purpose:
Improves regional reporting performance.
---------------------------------------------------------
*/

CREATE INDEX idx_region
ON auto_loan_securitisation_data(Region);