from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:Timomoti%402613@localhost/BankingRiskAnalytics"
)

connection = engine.connect()

print("MYSQL CONNECTION SUCCESSFUL")

connection.close()