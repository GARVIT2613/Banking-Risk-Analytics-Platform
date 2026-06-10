import pandas as pd

from sqlalchemy import create_engine

df = pd.read_csv(
    r"C:\Users\garvi\OneDrive\Desktop\Banking_Risk_Platform\data\auto_loan_securitisation_data.csv"
)

print("Original Rows:", len(df))

# Remove duplicates

df = df.drop_duplicates()

print("Rows After Duplicate Removal:", len(df))

# Trim spaces from column names

df.columns = df.columns.str.strip()

engine = create_engine(
    "mysql+pymysql://root:Timomoti%402613@localhost/BankingRiskAnalytics"
)

df.to_sql(
    "auto_loan_securitisation_data",
    engine,
    if_exists="replace",
    index=False
)

print("ETL Complete")