import pandas as pd

from sqlalchemy import create_engine

# Read CSV

df = pd.read_csv(
    r"C:\Users\garvi\OneDrive\Desktop\Banking_Risk_Platform\data\auto_loan_securitisation_data.csv"
)

print("Rows Read:", len(df))

# Connect MySQL

engine = create_engine(
    "mysql+pymysql://root:Timomoti%402613@localhost/BankingRiskAnalytics"
)

# Load data

df.to_sql(
    name="auto_loan_securitisation_data",
    con=engine,
    if_exists="append",
    index=False
)

print("Data Loaded Successfully")