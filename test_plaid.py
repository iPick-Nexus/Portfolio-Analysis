from plaid_client import client
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest

# 1. Fake-link a test brokerage
pt = client.sandbox_public_token_create(SandboxPublicTokenCreateRequest(
    institution_id="ins_109508",
    initial_products=[Products("investments")],
)).public_token

# 2. Exchange for an access token
access_token = client.item_public_token_exchange(
    ItemPublicTokenExchangeRequest(public_token=pt)).access_token
print("access_token:", access_token)

# 3. Pull holdings
resp = client.investments_holdings_get(
    InvestmentsHoldingsGetRequest(access_token=access_token)).to_dict()
sec = {s["security_id"]: s for s in resp["securities"]}

for h in resp["holdings"]:
    s = sec[h["security_id"]]
    print(f'{s.get("ticker_symbol") or "-":8} {s.get("type"):12} qty={h["quantity"]:<10} value={h["institution_value"]}')