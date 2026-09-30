# Banking Risk Analytics Platform – Streamlit app

## Repo layout (deploy exactly like this)
```
app.py
requirements.txt
.replit                  (Replit only)
.streamlit/config.toml   (light theme)
data/
  auto_loan_securitisation_data.csv
  dpd_snapshot_history.csv
  dynamic_loss_monthly.csv
  static_pool_vintage_data.csv
```

## Streamlit Community Cloud
1. Push all of the above to your GitHub repo (keep `app.py` and `data/` at the repo root).
2. share.streamlit.io -> Create app -> pick repo/branch, main file `app.py` -> Deploy.
3. Every `git push` redeploys automatically.

## Replit
Upload the same files and press Run (`.replit` starts Streamlit on port 5000).

## Local
```
pip install -r requirements.txt
streamlit run app.py
```
