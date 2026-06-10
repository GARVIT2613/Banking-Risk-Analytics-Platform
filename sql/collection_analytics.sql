/*
---------------------------------------------------------
QUERY : Average Collection Efficiency

Purpose:
Measure collection effectiveness.
---------------------------------------------------------
*/

SELECT

AVG(CollectionEfficiency)

AS AvgCollectionEfficiency

FROM dynamic_loss_monthly;

/*
---------------------------------------------------------
QUERY : Monthly Collections

Purpose:
Track monthly collection trend.
---------------------------------------------------------
*/

SELECT

ReportingDate,

CollectionsTotal

FROM dynamic_loss_monthly

ORDER BY ReportingDate;

/*
---------------------------------------------------------
QUERY : Monthly Recoveries

Purpose:
Track monthly recoveries.
---------------------------------------------------------
*/

SELECT

ReportingDate,

Recoveries_ThisMonth

FROM dynamic_loss_monthly

ORDER BY ReportingDate;

