import pandas as pd

df = pd.read_csv(
    r"C:\Users\garvi\OneDrive\Desktop\Banking_Risk_Platform\data\auto_loan_securitisation_data.csv"
)

print("Total Rows:", len(df))

print("\nNull Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())