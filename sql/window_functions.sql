/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
window_functions.sql

Purpose:
Advanced SQL Window Functions

Author:
Garvit Mehta

=========================================================
*/


/*
---------------------------------------------------------
WINDOW FUNCTION: RANK
Purpose:
Ranks loans based on current balance.
---------------------------------------------------------
*/

SELECT

LoanID,

CurrentBalance,

RANK() OVER
(
ORDER BY CurrentBalance DESC
)

AS RiskRank

FROM auto_loan_securitisation_data;


/*
---------------------------------------------------------
WINDOW FUNCTION: ROW_NUMBER
Purpose:
Assigns unique sequence to loans.
---------------------------------------------------------
*/

SELECT

LoanID,

CurrentBalance,

ROW_NUMBER() OVER
(
ORDER BY CurrentBalance DESC
)

AS RowNum

FROM auto_loan_securitisation_data;


/*
---------------------------------------------------------
WINDOW FUNCTION: DENSE_RANK
Purpose:
Assigns rank without gaps.
---------------------------------------------------------
*/

SELECT

LoanID,

CurrentBalance,

DENSE_RANK() OVER
(
ORDER BY CurrentBalance DESC
)

AS DenseRank

FROM auto_loan_securitisation_data;


/*
---------------------------------------------------------
WINDOW FUNCTION: Running Portfolio Balance
Purpose:
Tracks cumulative portfolio balance.
---------------------------------------------------------
*/

SELECT

LoanID,

OriginationDate,

CurrentBalance,

SUM(CurrentBalance)
OVER
(
ORDER BY OriginationDate
)

AS RunningBalance

FROM auto_loan_securitisation_data;


/*
---------------------------------------------------------
WINDOW FUNCTION: Running ECL
Purpose:
Tracks cumulative Expected Credit Loss.
---------------------------------------------------------
*/

SELECT

LoanID,

OriginationDate,

ECL_Provision,

SUM(ECL_Provision)
OVER
(
ORDER BY OriginationDate
)

AS RunningECL

FROM auto_loan_securitisation_data;