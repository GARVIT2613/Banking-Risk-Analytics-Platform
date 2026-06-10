/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
ctes.sql

Purpose:
Common Table Expression Examples

Author:
Garvit Mehta

=========================================================
*/


/*
---------------------------------------------------------
CTE: High Risk Loans
Purpose:
Identify all Stage 3 loans.
---------------------------------------------------------
*/

WITH HighRiskLoans AS
(
SELECT *

FROM auto_loan_securitisation_data

WHERE IFRS9_Stage = 3
)

SELECT *

FROM HighRiskLoans;


/*
---------------------------------------------------------
CTE: High Risk Loan Count
Purpose:
Count all Stage 3 loans.
---------------------------------------------------------
*/

WITH HighRiskLoans AS
(
SELECT *

FROM auto_loan_securitisation_data

WHERE IFRS9_Stage = 3
)

SELECT COUNT(*) AS HighRiskLoanCount

FROM HighRiskLoans;