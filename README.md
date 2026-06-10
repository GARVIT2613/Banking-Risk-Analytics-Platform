# End-to-End Banking Securitisation & Loan Risk Analytics Platform

## Introduction

The banking and securitisation industry relies heavily on portfolio monitoring, credit risk management, delinquency tracking, expected credit loss forecasting, and investor reporting.

To simulate a real-world banking risk analytics environment, I built an **End-to-End Banking Securitisation & Loan Risk Analytics Platform** using:

- SQL
- Python
- MySQL
- Power BI
- Data Warehousing
- IFRS9 Analytics
- Roll Rate Analytics
- Vintage Analytics
- Stress Testing

The platform analyzes securitised auto loan portfolios and provides insights into portfolio performance, borrower risk, expected losses, delinquency migration, and portfolio stress scenarios.

---

# Business Questions Analyzed

The project answers the following questions:

### 1. What is the current health of the securitised portfolio?

### 2. How are loans distributed across IFRS9 stages?

### 3. Which borrowers contribute the highest expected credit losses?

### 4. How are delinquent accounts migrating between DPD buckets?

### 5. Which loan vintages perform best and worst?

### 6. How effective are collections and recoveries?

### 7. How does the portfolio behave under economic stress scenarios?

---

# Technology Stack

## Database

- MySQL

## Programming

- Python
- Pandas
- SQLAlchemy

## Analytics

- SQL
- IFRS9 Analytics
- Roll Rate Analytics
- Vintage Analytics
- Collection Analytics
- Stress Testing Framework

## Visualization

- Power BI

---

# Skills Demonstrated

## SQL

- Views
- Indexes
- CTEs
- Window Functions
- Stored Procedures
- Advanced Analytics Queries

## Python

- ETL Development
- Data Validation
- Data Cleaning
- Data Transformation

## Data Engineering

- Data Warehousing
- Data Modeling
- Fact Tables
- Dimension Tables

## Banking Analytics

- IFRS9 Risk Analytics
- PD Analysis
- LGD Analysis
- EAD Analysis
- Expected Credit Loss (ECL)
- Roll Rate Analytics
- Vintage Analytics
- Stress Testing

---

# Project Architecture

```text
CSV Files

↓

Python ETL Layer

↓

MySQL Database

↓

Data Warehouse Layer

↓

Risk Analytics Engine

↓

Power BI Dashboards
```

---

# Dataset Overview

The project uses four banking datasets.

## Auto Loan Securitisation Data

Contains:

- Loan Information
- Borrower Information
- Vehicle Information
- Credit Scores
- Delinquency Information
- IFRS9 Variables

## DPD Snapshot History

Contains:

- Monthly Delinquency Snapshots
- DPD Buckets
- Cure Events
- Roll Forward Events
- Repossession Flags

## Dynamic Loss Monthly

Contains:

- Portfolio Losses
- Recoveries
- Collections
- Collection Efficiency
- Default Rates

## Static Pool Vintage Data

Contains:

- Vintage Performance
- Pool Factor
- Net Loss Rates
- Delinquency Trends

---

# Data Warehouse Design

## Raw Layer

- auto_loan_securitisation_data
- dpd_snapshot_history
- dynamic_loss_monthly
- static_pool_vintage_data

## Staging Layer

- stg_auto_loan_securitisation_data
- stg_dpd_snapshot_history
- stg_dynamic_loss_monthly
- stg_static_pool_vintage_data

## Dimension Tables

- DimBorrower
- DimVehicle
- DimRegion
- DimIFRSStage
- DimDate

## Fact Tables

- FactLoanPerformance
- FactDPDHistory
- FactVintagePerformance

---

# 1️⃣ Portfolio Health Analysis

## Objective

Analyze the overall health of the securitised portfolio.

## Metrics Used

- Portfolio Balance
- Loan Count
- Average DPD
- Total ECL

## SQL Techniques Used

- Aggregate Functions
- Group By
- Portfolio Health Views

## Business Insights

- Portfolio exposure is concentrated across selected regions.
- Stage 3 loans contribute significantly to portfolio risk.
- High-risk borrowers drive a large portion of expected losses.

---

# 2️⃣ IFRS9 Risk Analytics

## Objective

Measure expected credit losses and portfolio risk under IFRS9.

## Metrics Used

- IFRS9 Stage Distribution
- Probability of Default (PD)
- Loss Given Default (LGD)
- Exposure at Default (EAD)
- Expected Credit Loss (ECL)

## ECL Formula

```sql
ECL = PD × LGD × EAD
```

## Business Insights

- Stage 3 accounts generate the majority of portfolio ECL.
- Higher PD values result in significantly higher expected losses.
- ECL provides an early warning signal of credit deterioration.

---

# 3️⃣ Delinquency & Roll Rate Analytics

## Objective

Analyze movement of loans across delinquency buckets.

## Roll Rate Flow

```text
Current
↓
1-30 DPD
↓
31-60 DPD
↓
61-90 DPD
↓
90+ DPD
```

## Metrics Used

- Roll Rate Matrix
- Cure Rate
- Roll Forward Rate
- Repossession Rate
- Write-Off Analysis

## Business Insights

- Roll forward behavior indicates deteriorating credit quality.
- Cure rates measure collection effectiveness.
- Delinquency migration helps predict future defaults.

---

# 4️⃣ Vintage Analytics

## Objective

Analyze loan pool performance across different vintages.

## Metrics Used

- Pool Factor
- Cumulative Net Loss Rate
- Vintage Performance
- Vintage Comparison

## Business Insights

- Older vintages generally show higher cumulative losses.
- Strong vintages exhibit lower loss rates and better payment behavior.
- Vintage analysis helps identify portfolio quality trends.

---

# 5️⃣ Collection Analytics

## Objective

Evaluate collection performance and recovery effectiveness.

## Metrics Used

- Collection Efficiency
- Monthly Recoveries
- Recovery Trends
- Collection Trends

## Business Insights

- Collection efficiency directly impacts profitability.
- Strong recovery performance reduces portfolio losses.
- Collection trends provide early warning indicators.

---

# 6️⃣ Stress Testing Framework

## Objective

Assess portfolio resilience under stressed economic conditions.

## Scenarios Implemented

### Base Scenario

Current Portfolio Risk

### Mild Stress Scenario

10% Increase in PD

### Severe Stress Scenario

25% Increase in PD

### Extreme Stress Scenario

50% Increase in PD

## Metrics Used

- Stressed ECL
- Stressed Net Loss
- Scenario Comparison
- Portfolio Impact Analysis

## Business Insights

- Portfolio losses rise significantly under severe stress.
- Stress testing supports capital planning.
- Extreme scenarios help identify portfolio vulnerabilities.

---

# Advanced SQL Features Implemented

## Views

- vw_IFRS9_ECL
- vw_Portfolio_Health
- vw_DPD_Summary

## Indexes

- idx_loanid
- idx_poolid
- idx_borrowerid
- idx_region

## Common Table Expressions (CTEs)

- HighRiskLoans

## Window Functions

- RANK()
- ROW_NUMBER()
- DENSE_RANK()
- Running Portfolio Balance
- Running ECL

## Stored Procedures

- Refresh_Portfolio()

---

# ETL Pipeline

## Extract

Imported banking datasets from CSV sources.

## Transform

Applied:

- Data Cleaning
- Missing Value Validation
- Duplicate Removal
- Data Type Standardization
- Data Quality Checks

## Load

Loaded transformed datasets into MySQL for analytics and reporting.

---

# Power BI Dashboards

## Executive Summary Dashboard

Provides portfolio-wide KPIs and risk indicators.

## Portfolio Overview Dashboard

Provides portfolio exposure and borrower distribution.

## IFRS9 Dashboard

Monitors ECL, PD, LGD, EAD and stage distribution.

## DPD Dashboard

Tracks delinquency trends and borrower performance.

## Roll Rate Dashboard

Visualizes migration between delinquency buckets.

## Vintage Dashboard

Analyzes vintage-level portfolio performance.

## Collection Dashboard

Tracks recoveries and collection efficiency.

## Stress Testing Dashboard

Compares portfolio performance under different economic scenarios.

---

# Key Project Outcomes

- Built an end-to-end Banking Risk Analytics Platform.
- Developed a structured Data Warehouse architecture.
- Implemented IFRS9 Risk Analytics and Expected Credit Loss calculations.
- Designed Roll Rate and Delinquency Migration Analytics.
- Created Vintage Performance and Collection Analytics frameworks.
- Developed Stress Testing scenarios for portfolio risk forecasting.
- Built multiple Power BI dashboards for executive reporting.
- Applied advanced SQL features including Views, CTEs, Window Functions, Indexes and Stored Procedures.

---

# Repository Structure

```text
Banking_Risk_Platform/

│
├── data/
│
├── sql/
│   ├── create_tables.sql
│   ├── views.sql
│   ├── indexes.sql
│   ├── cte_examples.sql
│   ├── window_functions.sql
│   ├── stored_procedures.sql
│   ├── banking_analytics.sql
│   ├── ifrs9_analytics.sql
│   ├── roll_rate_analytics.sql
│   ├── vintage_analytics.sql
│   ├── collection_analytics.sql
│   └── stress_testing_framework.sql
│
├── python/
│
├── powerbi/
│   └── BankingRiskAnalytics.pbix
│
├── documentation/
│
└── README.md
```

---

# Conclusion

This project demonstrates how modern financial institutions can leverage SQL, Python, Data Warehousing, Risk Analytics, and Power BI to build a comprehensive banking risk monitoring platform.

The solution combines portfolio monitoring, IFRS9 analytics, delinquency tracking, roll rate analysis, vintage performance assessment, collection analytics, and stress testing into a unified framework that supports risk management, investor reporting, and business decision-making.