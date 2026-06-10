/*
---------------------------------------------------------
QUERY : Vintage Performance

Purpose:
Analyze pool performance over time.
---------------------------------------------------------
*/

SELECT

VintageID,
MonthsOnBook,
PoolFactor,
CumulativeNetLossRate

FROM static_pool_vintage_data;

/*
---------------------------------------------------------
QUERY : Worst Vintage

Purpose:
Identify worst performing vintage.
---------------------------------------------------------
*/

SELECT

VintageID,

MAX(CumulativeNetLossRate)
AS MaxLossRate

FROM static_pool_vintage_data

GROUP BY VintageID

ORDER BY MaxLossRate DESC;

/*
---------------------------------------------------------
QUERY : Best Vintage

Purpose:
Identify best performing vintage.
---------------------------------------------------------
*/

SELECT

VintageID,

MIN(CumulativeNetLossRate)
AS MinLossRate

FROM static_pool_vintage_data

GROUP BY VintageID

ORDER BY MinLossRate;

