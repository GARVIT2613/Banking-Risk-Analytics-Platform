/*
=========================================================
BANKING SECURITISATION & LOAN RISK ANALYTICS PLATFORM

File Name:
create_tables.sql

Purpose:
Complete Database Schema Creation Script

Author:
Garvit Mehta

Description:
Creates:
1. Database
2. Raw Tables
3. Staging Tables
4. Dimension Tables
5. Fact Tables

=========================================================
*/


/*
=========================================================
SECTION 1 : DATABASE CREATION
=========================================================
*/

CREATE DATABASE IF NOT EXISTS BankingRiskAnalytics;

USE BankingRiskAnalytics;


/*
=========================================================
SECTION 2 : RAW TABLES
=========================================================
*/


/*
---------------------------------------------------------
RAW TABLE : auto_loan_securitisation_data

Purpose:
Stores loan-level securitisation portfolio data.

Source:
SAP / ERP / Loan Management Systems
---------------------------------------------------------
*/

CREATE TABLE auto_loan_securitisation_data
(
LoanID VARCHAR(50),
PoolID VARCHAR(50),
BorrowerID VARCHAR(50),
ServicerID VARCHAR(50),
ServicerName VARCHAR(100),
OriginationChannel VARCHAR(50),

OriginationDate DATE,
CutoffDate DATE,
MaturityDate DATE,

OriginalLoanAmount DECIMAL(18,2),

OriginalTerm INT,
RemainingTerm INT,
MonthsOnBook INT,

InterestRate DECIMAL(10,4),

MonthlyEMI DECIMAL(18,2),

LoanPurpose VARCHAR(100),

CurrentBalance DECIMAL(18,2),

ScheduledPaymentDue DECIMAL(18,2),

LastPaymentAmount DECIMAL(18,2),

LastPaymentDate DATE,

DelinquencyStatus VARCHAR(50),

DelinquencyDays INT,

TotalPaymentsDue INT,
TotalPaymentsMade INT,

Times30DPD_Last12M INT,
Times60DPD_Last12M INT,
Times90DPD_Last12M INT,

VehicleMake VARCHAR(100),
VehicleModel VARCHAR(100),

VehicleYear INT,

VehicleType VARCHAR(100),

IsNewVehicle BOOLEAN,

OriginalVehicleValue DECIMAL(18,2),
CurrentVehicleValue DECIMAL(18,2),

LTV_AtOrigination DECIMAL(10,4),
LTV_Current DECIMAL(10,4),

BorrowerAge INT,

EmploymentType VARCHAR(50),

AnnualIncome_INR DECIMAL(18,2),

DTI_Ratio DECIMAL(10,4),

CIBIL_Score_Origination INT,
CIBIL_Score_Current INT,

Region VARCHAR(50),
State VARCHAR(50),

IFRS9_Stage INT,

PD_Estimate DECIMAL(10,6),
LGD_Estimate DECIMAL(10,6),

EAD DECIMAL(18,2),

ECL_Provision DECIMAL(18,2),

IsDefaulted BOOLEAN,
IsModified BOOLEAN,

ModificationType VARCHAR(100),

LossAmount DECIMAL(18,2),
RecoveryAmount DECIMAL(18,2),

NetLoss DECIMAL(18,2),

PrepaymentAmount DECIMAL(18,2),

InsuranceType VARCHAR(50),

HasInsurance BOOLEAN
);


/*
---------------------------------------------------------
RAW TABLE : dpd_snapshot_history

Purpose:
Stores monthly delinquency snapshots.
---------------------------------------------------------
*/

CREATE TABLE dpd_snapshot_history
(
SnapshotDate DATE,

LoanID VARCHAR(50),

PoolID VARCHAR(50),

DPD_Days INT,

DPD_Bucket VARCHAR(50),

DPD_Bucket_Prior VARCHAR(50),

CurrentBalance DECIMAL(18,2),

AmountOverdue DECIMAL(18,2),

EMIsOverdue INT,

LastPaymentDate DATE,

LastPaymentAmount DECIMAL(18,2),

CureFlag BOOLEAN,

RollFlag VARCHAR(50),

RepossessionFlag BOOLEAN,

WriteOffFlag BOOLEAN,

RBI_SMA_Class VARCHAR(50),

ConsecutiveMonthsDelinquent INT,

TransitionType VARCHAR(50)
);


/*
---------------------------------------------------------
RAW TABLE : dynamic_loss_monthly

Purpose:
Stores monthly portfolio loss metrics.
---------------------------------------------------------
*/

CREATE TABLE dynamic_loss_monthly
(
ReportingDate DATE,

BOP_LoanCount INT,
BOP_Balance DECIMAL(18,2),

NewDefaults_Count INT,
NewDefaults_Balance DECIMAL(18,2),

GrossLoss_ThisMonth DECIMAL(18,2),

Recoveries_ThisMonth DECIMAL(18,2),

NetLoss_ThisMonth DECIMAL(18,2),

Prepayments_ThisMonth DECIMAL(18,2),

ScheduledAmort DECIMAL(18,2),

EOP_Balance DECIMAL(18,2),
EOP_LoanCount INT,

CollectionsTotal DECIMAL(18,2),

BillingAmount DECIMAL(18,2),

CollectionEfficiency DECIMAL(10,4),

MonthlyDefaultRate DECIMAL(10,6),

MonthlyNetLossRate DECIMAL(10,6),

SMM DECIMAL(10,6),

CPR_Annualised DECIMAL(10,6),

ExcessSpread_Monthly DECIMAL(18,2)
);


/*
---------------------------------------------------------
RAW TABLE : static_pool_vintage_data

Purpose:
Stores vintage performance metrics.
---------------------------------------------------------
*/

CREATE TABLE static_pool_vintage_data
(
VintageID VARCHAR(20),

VintageStartDate DATE,

OriginalLoanCount INT,

OriginalPoolBalance DECIMAL(18,2),

MonthsOnBook INT,

CumulativeDefaults_Count INT,

CumulativeDefaults_Balance DECIMAL(18,2),

CumulativeGrossLoss DECIMAL(18,2),

CumulativeRecoveries DECIMAL(18,2),

CumulativeNetLoss DECIMAL(18,2),

CumulativeNetLossRate DECIMAL(10,6),

CumulativePrepayments DECIMAL(18,2),

RemainingPoolBalance DECIMAL(18,2),

PoolFactor DECIMAL(10,6),

CurrentDelinq30Plus DECIMAL(10,6),

MarginalLossRate DECIMAL(10,6)
);


/*
=========================================================
SECTION 3 : STAGING TABLES
=========================================================
*/


/*
---------------------------------------------------------
STAGING TABLES

Purpose:
Landing area for ETL validation and cleansing.
---------------------------------------------------------
*/

CREATE TABLE stg_auto_loan_securitisation_data
LIKE auto_loan_securitisation_data;

CREATE TABLE stg_dpd_snapshot_history
LIKE dpd_snapshot_history;

CREATE TABLE stg_dynamic_loss_monthly
LIKE dynamic_loss_monthly;

CREATE TABLE stg_static_pool_vintage_data
LIKE static_pool_vintage_data;


/*
=========================================================
SECTION 4 : DIMENSION TABLES
=========================================================
*/


/*
---------------------------------------------------------
DIMENSION TABLE : DimBorrower

Purpose:
Stores borrower master information.
---------------------------------------------------------
*/

CREATE TABLE DimBorrower
(
BorrowerID VARCHAR(50),

BorrowerAge INT,

EmploymentType VARCHAR(50),

AnnualIncome_INR DECIMAL(18,2),

DTI_Ratio DECIMAL(10,4),

CIBIL_Score_Origination INT,

CIBIL_Score_Current INT
);


/*
---------------------------------------------------------
DIMENSION TABLE : DimVehicle
---------------------------------------------------------
*/

CREATE TABLE DimVehicle
(
VehicleMake VARCHAR(100),

VehicleModel VARCHAR(100),

VehicleYear INT,

VehicleType VARCHAR(100),

IsNewVehicle BOOLEAN,

OriginalVehicleValue DECIMAL(18,2),

CurrentVehicleValue DECIMAL(18,2)
);


/*
---------------------------------------------------------
DIMENSION TABLE : DimRegion
---------------------------------------------------------
*/

CREATE TABLE DimRegion
(
Region VARCHAR(50),

State VARCHAR(50)
);


/*
---------------------------------------------------------
DIMENSION TABLE : DimIFRSStage
---------------------------------------------------------
*/

CREATE TABLE DimIFRSStage
(
IFRS9_Stage INT,

StageDescription VARCHAR(100)
);


/*
---------------------------------------------------------
DIMENSION TABLE : DimDate
---------------------------------------------------------
*/

CREATE TABLE DimDate
(
DateValue DATE,

YearValue INT,

QuarterValue INT,

MonthValue INT,

MonthName VARCHAR(20)
);


/*
=========================================================
SECTION 5 : FACT TABLES
=========================================================
*/


/*
---------------------------------------------------------
FACT TABLE : FactLoanPerformance

Purpose:
Stores loan performance measures.
---------------------------------------------------------
*/

CREATE TABLE FactLoanPerformance
(
LoanID VARCHAR(50),

BorrowerID VARCHAR(50),

OriginationDate DATE,

CurrentBalance DECIMAL(18,2),

DelinquencyDays INT,

IFRS9_Stage INT,

PD_Estimate DECIMAL(10,6),

LGD_Estimate DECIMAL(10,6),

EAD DECIMAL(18,2),

ECL_Provision DECIMAL(18,2),

NetLoss DECIMAL(18,2)
);


/*
---------------------------------------------------------
FACT TABLE : FactDPDHistory
---------------------------------------------------------
*/

CREATE TABLE FactDPDHistory
(
SnapshotDate DATE,

LoanID VARCHAR(50),

DPD_Days INT,

DPD_Bucket VARCHAR(50),

DPD_Bucket_Prior VARCHAR(50),

CurrentBalance DECIMAL(18,2),

TransitionType VARCHAR(50)
);


/*
---------------------------------------------------------
FACT TABLE : FactVintagePerformance
---------------------------------------------------------
*/

CREATE TABLE FactVintagePerformance
(
VintageID VARCHAR(20),

MonthsOnBook INT,

PoolFactor DECIMAL(10,6),

CumulativeNetLossRate DECIMAL(10,6),

CurrentDelinq30Plus DECIMAL(10,6),

MarginalLossRate DECIMAL(10,6)
);


