/*
---------------------------------------------------------
QUERY : Roll Rate Matrix

Purpose:
Analyze movement between DPD buckets.

Business Use:
Collections
Risk Analytics
---------------------------------------------------------
*/

SELECT

DPD_Bucket_Prior,

DPD_Bucket,

COUNT(*) AS LoanCount

FROM dpd_snapshot_history

GROUP BY

DPD_Bucket_Prior,
DPD_Bucket

ORDER BY

DPD_Bucket_Prior,
DPD_Bucket;

/*
---------------------------------------------------------
QUERY : Cure Rate

Purpose:
Loans returning to current status.
---------------------------------------------------------
*/

SELECT

COUNT(*) AS CureCount

FROM dpd_snapshot_history

WHERE CureFlag = 1;

/*
---------------------------------------------------------
QUERY : Roll Forward Count

Purpose:
Loans moving into worse delinquency.
---------------------------------------------------------
*/

SELECT

COUNT(*) AS RollForwardCount

FROM dpd_snapshot_history

WHERE RollFlag = 'Forward';

/*
---------------------------------------------------------
QUERY : Repossessed Accounts

Purpose:
Track repossessed loans.
---------------------------------------------------------
*/

SELECT

COUNT(*) AS RepossessedAccounts

FROM dpd_snapshot_history

WHERE RepossessionFlag = 1;


/*
---------------------------------------------------------
QUERY : Written Off Accounts

Purpose:
Track write-offs.
---------------------------------------------------------
*/

SELECT

COUNT(*) AS WrittenOffAccounts

FROM dpd_snapshot_history

WHERE WriteOffFlag = 1;

