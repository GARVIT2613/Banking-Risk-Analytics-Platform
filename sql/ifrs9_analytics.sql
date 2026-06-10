/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
ifrs9_analytics.sql

Purpose:
IFRS9 Risk Analytics Engine

Author:
Garvit Mehta

Description:
Provides IFRS9 credit risk analytics including:

1. Portfolio ECL Analysis
2. IFRS9 Stage Distribution
3. Stage Exposure Analysis
4. Probability of Default Analysis
5. Loss Given Default Analysis
6. Exposure at Default Analysis
7. Stage Wise Risk Metrics
8. High Risk Loan Identification

=========================================================
*/


/*
=========================================================
SECTION 1 : PORTFOLIO IFRS9 ANALYTICS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Total Expected Credit Loss

Purpose:
Calculate portfolio level ECL provision.

Business Use:
Executive Dashboard
IFRS9 Dashboard
Investor Reporting
---------------------------------------------------------
*/

SELECT

SUM(ECL_Provision)

AS TotalECL

FROM auto_loan_securitisation_data;



/*
---------------------------------------------------------
QUERY : Portfolio Exposure At Default

Purpose:
Calculate total Exposure At Default.

Business Use:
Risk Management Reporting
---------------------------------------------------------
*/

SELECT

SUM(EAD)

AS PortfolioEAD

FROM auto_loan_securitisation_data;



/*
---------------------------------------------------------
QUERY : Portfolio Average Probability of Default

Purpose:
Measure overall portfolio credit risk.

Business Use:
IFRS9 Monitoring
---------------------------------------------------------
*/

SELECT

AVG(PD_Estimate)

AS PortfolioAveragePD

FROM auto_loan_securitisation_data;



/*
---------------------------------------------------------
QUERY : Portfolio Average Loss Given Default

Purpose:
Measure expected loss severity.

Business Use:
Loss Forecasting
---------------------------------------------------------
*/

SELECT

AVG(LGD_Estimate)

AS PortfolioAverageLGD

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 2 : IFRS9 STAGE ANALYTICS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : IFRS9 Stage Distribution

Purpose:
Count loans and exposure by stage.

Business Use:
Executive Dashboard
IFRS9 Dashboard
---------------------------------------------------------
*/

SELECT

IFRS9_Stage,

COUNT(*) AS LoanCount,

SUM(CurrentBalance) AS Exposure

FROM auto_loan_securitisation_data

GROUP BY IFRS9_Stage

ORDER BY IFRS9_Stage;



/*
---------------------------------------------------------
QUERY : Stage Wise ECL

Purpose:
Calculate ECL contribution by stage.

Business Use:
Risk Reporting
---------------------------------------------------------
*/

SELECT

IFRS9_Stage,

SUM(ECL_Provision)

AS TotalECL

FROM auto_loan_securitisation_data

GROUP BY IFRS9_Stage

ORDER BY IFRS9_Stage;



/*
---------------------------------------------------------
QUERY : Stage Wise Exposure

Purpose:
Measure outstanding exposure by stage.

Business Use:
Credit Risk Monitoring
---------------------------------------------------------
*/

SELECT

IFRS9_Stage,

SUM(CurrentBalance)

AS Exposure

FROM auto_loan_securitisation_data

GROUP BY IFRS9_Stage

ORDER BY IFRS9_Stage;



/*
---------------------------------------------------------
QUERY : Stage 3 Exposure

Purpose:
Measure credit impaired exposure.

Business Use:
Executive Dashboard
---------------------------------------------------------
*/

SELECT

SUM(CurrentBalance)

AS Stage3Exposure

FROM auto_loan_securitisation_data

WHERE IFRS9_Stage = 3;



/*
=========================================================
SECTION 3 : PD ANALYTICS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Average PD by Stage

Purpose:
Compare PD across IFRS9 stages.

Business Use:
Credit Risk Analytics
---------------------------------------------------------
*/

SELECT

IFRS9_Stage,

AVG(PD_Estimate)

AS AvgPD

FROM auto_loan_securitisation_data

GROUP BY IFRS9_Stage

ORDER BY IFRS9_Stage;



/*
---------------------------------------------------------
QUERY : Highest PD Loans

Purpose:
Identify most risky borrowers.

Business Use:
Watchlist Monitoring
---------------------------------------------------------
*/

SELECT

LoanID,

BorrowerID,

PD_Estimate,

CurrentBalance

FROM auto_loan_securitisation_data

ORDER BY PD_Estimate DESC

LIMIT 20;



/*
=========================================================
SECTION 4 : LGD ANALYTICS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Average LGD by Stage

Purpose:
Compare loss severity by stage.

Business Use:
IFRS9 Analytics
---------------------------------------------------------
*/

SELECT

IFRS9_Stage,

AVG(LGD_Estimate)

AS AvgLGD

FROM auto_loan_securitisation_data

GROUP BY IFRS9_Stage

ORDER BY IFRS9_Stage;



/*
---------------------------------------------------------
QUERY : Highest LGD Loans

Purpose:
Identify loans with highest loss severity.

Business Use:
Risk Monitoring
---------------------------------------------------------
*/

SELECT

LoanID,

BorrowerID,

LGD_Estimate,

CurrentBalance

FROM auto_loan_securitisation_data

ORDER BY LGD_Estimate DESC

LIMIT 20;



/*
=========================================================
SECTION 5 : EAD ANALYTICS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Highest EAD Loans

Purpose:
Identify largest credit exposures.

Business Use:
Exposure Monitoring
---------------------------------------------------------
*/

SELECT

LoanID,

BorrowerID,

EAD,

CurrentBalance

FROM auto_loan_securitisation_data

ORDER BY EAD DESC

LIMIT 20;



/*
=========================================================
SECTION 6 : CALCULATED IFRS9 ECL
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Calculated ECL

Purpose:
Calculate IFRS9 Expected Credit Loss using:

ECL = PD × LGD × EAD

Business Use:
Model Validation
---------------------------------------------------------
*/

SELECT

LoanID,

BorrowerID,

PD_Estimate,

LGD_Estimate,

EAD,

(PD_Estimate * LGD_Estimate * EAD)

AS CalculatedECL

FROM auto_loan_securitisation_data;



/*
---------------------------------------------------------
QUERY : Top 20 Highest Calculated ECL Loans

Purpose:
Identify largest expected losses.

Business Use:
Risk Concentration Monitoring
---------------------------------------------------------
*/

SELECT

LoanID,

BorrowerID,

CurrentBalance,

(PD_Estimate * LGD_Estimate * EAD)

AS CalculatedECL

FROM auto_loan_securitisation_data

ORDER BY CalculatedECL DESC

LIMIT 20;



/*
=========================================================
SECTION 7 : HIGH RISK PORTFOLIO ANALYTICS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Stage 3 High Risk Loans

Purpose:
Identify credit impaired loans.

Business Use:
Collections Strategy
Recovery Planning
---------------------------------------------------------
*/

SELECT

LoanID,

BorrowerID,

CurrentBalance,

ECL_Provision,

PD_Estimate,

LGD_Estimate

FROM auto_loan_securitisation_data

WHERE IFRS9_Stage = 3

ORDER BY ECL_Provision DESC;



/*
---------------------------------------------------------
QUERY : High Risk States

Purpose:
Identify states with highest IFRS9 risk.

Business Use:
Regional Risk Monitoring
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
QUERY : High Risk Regions

Purpose:
Identify regions with highest IFRS9 risk.

Business Use:
Portfolio Monitoring
---------------------------------------------------------
*/

SELECT

Region,

SUM(ECL_Provision)

AS TotalECL

FROM auto_loan_securitisation_data

GROUP BY Region

ORDER BY TotalECL DESC;


