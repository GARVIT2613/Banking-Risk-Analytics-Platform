/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
stress_testing_framework.sql

Purpose:
Portfolio Stress Testing Framework

Author:
Garvit Mehta

Description:
Implements:

1. Base Scenario
2. Mild Stress Scenario
3. Severe Stress Scenario
4. Extreme Stress Scenario
5. PD Shock Analysis
6. LGD Shock Analysis
7. ECL Impact Analysis
8. Portfolio Loss Impact Analysis
9. Scenario Comparison

=========================================================
*/


/*
=========================================================
SECTION 1 : BASE SCENARIO
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Base Scenario

Purpose:
Current portfolio ECL without stress.

Business Use:
Baseline risk measurement.
---------------------------------------------------------
*/

SELECT

SUM(ECL_Provision)

AS BaseScenarioECL

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 2 : MILD STRESS SCENARIO
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Mild Stress Scenario

Purpose:
Assume 10% increase in PD.

Business Use:
Economic slowdown simulation.
---------------------------------------------------------
*/

SELECT

SUM(
(PD_Estimate * 1.10)
*
LGD_Estimate
*
EAD
)

AS MildStressECL

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 3 : SEVERE STRESS SCENARIO
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Severe Stress Scenario

Purpose:
Assume 25% increase in PD.

Business Use:
Recession simulation.
---------------------------------------------------------
*/

SELECT

SUM(
(PD_Estimate * 1.25)
*
LGD_Estimate
*
EAD
)

AS SevereStressECL

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 4 : EXTREME STRESS SCENARIO
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Extreme Stress Scenario

Purpose:
Assume 50% increase in PD.

Business Use:
Financial crisis simulation.
---------------------------------------------------------
*/

SELECT

SUM(
(PD_Estimate * 1.50)
*
LGD_Estimate
*
EAD
)

AS ExtremeStressECL

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 5 : PD SHOCK ANALYSIS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : PD Shock Analysis

Purpose:
Measure impact of increased Probability of Default.

Business Use:
Credit Risk Stress Testing.
---------------------------------------------------------
*/

SELECT

SUM(PD_Estimate)

AS CurrentPD,

SUM(PD_Estimate * 1.25)

AS StressedPD

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 6 : LGD SHOCK ANALYSIS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : LGD Shock Analysis

Purpose:
Measure impact of increased Loss Given Default.

Business Use:
Loss Severity Stress Testing.
---------------------------------------------------------
*/

SELECT

SUM(LGD_Estimate)

AS CurrentLGD,

SUM(LGD_Estimate * 1.20)

AS StressedLGD

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 7 : ECL IMPACT ANALYSIS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : ECL Impact Analysis

Purpose:
Compare current ECL versus stressed ECL.

Business Use:
Capital Planning and Risk Monitoring.
---------------------------------------------------------
*/

SELECT

SUM(ECL_Provision)

AS CurrentECL,

SUM(
(PD_Estimate * 1.25)
*
LGD_Estimate
*
EAD
)

AS StressedECL

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 8 : PORTFOLIO LOSS IMPACT ANALYSIS
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Portfolio Loss Impact Analysis

Purpose:
Estimate stressed portfolio losses.

Business Use:
Portfolio Risk Forecasting.
---------------------------------------------------------
*/

SELECT

SUM(NetLoss)

AS CurrentNetLoss,

SUM(NetLoss * 1.25)

AS StressedNetLoss

FROM auto_loan_securitisation_data;



/*
=========================================================
SECTION 9 : SCENARIO COMPARISON
=========================================================
*/


/*
---------------------------------------------------------
QUERY : Scenario Comparison

Purpose:
Compare Base, Mild, Severe and Extreme
stress scenarios.

Business Use:
Executive Stress Testing Dashboard.
---------------------------------------------------------
*/

SELECT

SUM(ECL_Provision)

AS BaseScenario,

SUM(
(PD_Estimate * 1.10)
*
LGD_Estimate
*
EAD
)

AS MildScenario,

SUM(
(PD_Estimate * 1.25)
*
LGD_Estimate
*
EAD
)

AS SevereScenario,

SUM(
(PD_Estimate * 1.50)
*
LGD_Estimate
*
EAD
)

AS ExtremeScenario

FROM auto_loan_securitisation_data;



