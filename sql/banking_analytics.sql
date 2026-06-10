/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
banking_analytics.sql

Purpose:
Banking Risk Analytics KPI Queries

Author:
Garvit Mehta

=========================================================
*/


/*
---------------------------------------------------------
QUERY: Portfolio Balance
Purpose:
Calculate total outstanding portfolio balance.
---------------------------------------------------------
*/

SELECT

SUM(CurrentBalance)

AS PortfolioBalance

FROM auto_loan_securitisation_data;



/*
---------------------------------------------------------
QUERY: Total Expected Credit Loss
Purpose:
Calculate total ECL provision across portfolio.
---------------------------------------------------------
*/

SELECT

SUM(ECL_Provision)

AS TotalECL

FROM auto_loan_securitisation_data;



/*
---------------------------------------------------------
QUERY: IFRS9 Stage Distribution
Purpose:
Count loans across IFRS9 stages.
---------------------------------------------------------
*/

SELECT

IFRS9_Stage,

COUNT(*) AS LoanCount

FROM auto_loan_securitisation_data

GROUP BY IFRS9_Stage

ORDER BY IFRS9_Stage;



/*
---------------------------------------------------------
QUERY: Top 20 High Risk Loans
Purpose:
Identify loans with highest ECL provisions.
---------------------------------------------------------
*/

SELECT

LoanID,

CurrentBalance,

ECL_Provision

FROM auto_loan_securitisation_data

ORDER BY ECL_Provision DESC

LIMIT 20;



/*
---------------------------------------------------------
QUERY: Highest Risk States
Purpose:
Identify states contributing highest ECL.
---------------------------------------------------------
*/

SELECT

State,

SUM(ECL_Provision)

AS TotalECL

FROM auto_loan_securitisation_data

GROUP BY State

ORDER BY TotalECL DESC;



/*
---------------------------------------------------------
QUERY: Portfolio Delinquency Distribution
Purpose:
Analyze delinquency concentration by status.
---------------------------------------------------------
*/

SELECT

DelinquencyStatus,

COUNT(*) AS LoanCount,

SUM(CurrentBalance) AS Balance

FROM auto_loan_securitisation_data

GROUP BY DelinquencyStatus;



/*
---------------------------------------------------------
QUERY: Stage 3 Exposure
Purpose:
Calculate exposure of credit impaired loans.
---------------------------------------------------------
*/

SELECT

SUM(CurrentBalance)

AS Stage3Exposure

FROM auto_loan_securitisation_data

WHERE IFRS9_Stage = 3;



/*
---------------------------------------------------------
QUERY: Average DPD by Region
Purpose:
Measure delinquency severity by region.
---------------------------------------------------------
*/

SELECT

Region,

AVG(DelinquencyDays)

AS AvgDPD

FROM auto_loan_securitisation_data

GROUP BY Region

ORDER BY AvgDPD DESC;



/*
---------------------------------------------------------
QUERY: Region Wise Exposure
Purpose:
Calculate outstanding exposure by region.
---------------------------------------------------------
*/

SELECT

Region,

SUM(CurrentBalance)

AS Exposure

FROM auto_loan_securitisation_data

GROUP BY Region

ORDER BY Exposure DESC;



/*
---------------------------------------------------------
QUERY: Region Wise ECL
Purpose:
Calculate expected credit loss by region.
---------------------------------------------------------
*/

SELECT

Region,

SUM(ECL_Provision)

AS TotalECL

FROM auto_loan_securitisation_data

GROUP BY Region

ORDER BY TotalECL DESC;