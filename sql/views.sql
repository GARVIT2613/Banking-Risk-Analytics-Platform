/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
views.sql

Purpose:
Reusable Banking Analytics Views

Author:
Garvit Mehta

=========================================================
*/


/*
---------------------------------------------------------
VIEW: IFRS9 ECL VIEW
Purpose:
Provides Expected Credit Loss calculations for all loans.
Used in IFRS9 Dashboard and Executive Dashboard.
---------------------------------------------------------
*/

CREATE OR REPLACE VIEW vw_IFRS9_ECL AS

SELECT

LoanID,
BorrowerID,
CurrentBalance,
IFRS9_Stage,
PD_Estimate,
LGD_Estimate,
EAD,

(PD_Estimate * LGD_Estimate * EAD) AS Calculated_ECL

FROM auto_loan_securitisation_data;


/*
---------------------------------------------------------
VIEW: PORTFOLIO HEALTH VIEW
Purpose:
Provides portfolio-level risk indicators by region.
---------------------------------------------------------
*/

CREATE OR REPLACE VIEW vw_Portfolio_Health AS

SELECT

Region,

COUNT(*) AS LoanCount,

SUM(CurrentBalance) AS TotalBalance,

AVG(DelinquencyDays) AS AvgDPD,

SUM(ECL_Provision) AS TotalECL

FROM auto_loan_securitisation_data

GROUP BY Region;


/*
---------------------------------------------------------
VIEW: DPD SUMMARY VIEW
Purpose:
Provides delinquency distribution of loans.
---------------------------------------------------------
*/

CREATE OR REPLACE VIEW vw_DPD_Summary AS

SELECT

DelinquencyStatus,

COUNT(*) AS LoanCount,

SUM(CurrentBalance) AS OutstandingBalance

FROM auto_loan_securitisation_data

GROUP BY DelinquencyStatus;