/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
stored_procedures.sql

Purpose:
Reusable Stored Procedures

Author:
Garvit Mehta

=========================================================
*/


/*
---------------------------------------------------------
PROCEDURE: Refresh_Portfolio
Purpose:
Provides regional portfolio summary.
---------------------------------------------------------
*/

DELIMITER $$

CREATE PROCEDURE Refresh_Portfolio()

BEGIN

SELECT

Region,

COUNT(*) AS LoanCount,

SUM(CurrentBalance) AS TotalBalance,

SUM(ECL_Provision) AS TotalECL

FROM auto_loan_securitisation_data

GROUP BY Region;

END $$

DELIMITER ;


/*
---------------------------------------------------------
EXECUTE PROCEDURE
---------------------------------------------------------
*/

CALL Refresh_Portfolio();