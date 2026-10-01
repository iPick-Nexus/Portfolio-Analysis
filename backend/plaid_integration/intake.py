from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from .client import client  # adjust import to wherever your client lives

ALLOWED = {"equity", "mutual fund", "etf"}

def fetch_holdings(access_token):
    resp = client.investments_holdings_get(
        InvestmentsHoldingsGetRequest(access_token=access_token)).to_dict()
    sec = {s["security_id"]: s for s in resp["securities"]}

    holdings = []
    for h in resp["holdings"]:
        s = sec[h["security_id"]]
        if s.get("type") == "cash" or not s.get("ticker_symbol"):
            continue  # skip cash / untickered positions
        holdings.append({
            "ticker": s["ticker_symbol"],
            "name": s.get("name"),
            "type": s.get("type"),
            "quantity": h["quantity"],
            "value": h["institution_value"],
            "cost_basis": h.get("cost_basis"),
        })
    return holdings