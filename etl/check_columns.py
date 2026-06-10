import pandas as pd

df = pd.read_csv(r"C:\Users\garvi\OneDrive\Desktop\Banking_Risk_Platform\data\auto_loan_securitisation_data.csv")

print(df.columns.tolist())
print(df.shape)