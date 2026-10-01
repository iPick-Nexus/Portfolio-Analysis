"""Demo: see what raw Plaid Sandbox data looks like.

This is NOT how you check your work. It calls Plaid directly and never touches views.py.
To check your work, run the tests:  python manage.py test plaid_integration

Run from the backend/ folder (needs your .env with Plaid keys):
    python plaid_demo.py
"""
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest

from plaid_integration.client import client

# 1. Fake-link a test brokerage (First Platypus Bank). In the real app, Plaid Link does this step.
public_token = client.sandbox_public_token_create(SandboxPublicTokenCreateRequest(
    institution_id="ins_109508",
    initial_products=[Products("investments")],
)).public_token

# 2. Exchange the short-lived public token for an access token.
# Never print or log access tokens: they give ongoing access to someone's brokerage data.
access_token = client.item_public_token_exchange(
    ItemPublicTokenExchangeRequest(public_token=public_token)).access_token

# 3. Pull holdings. Plaid returns holdings and securities as separate lists, joined by security_id.
resp = client.investments_holdings_get(
    InvestmentsHoldingsGetRequest(access_token=access_token)).to_dict()
securities = {s["security_id"]: s for s in resp["securities"]}

print(f'{"TICKER":8} {"TYPE":14} {"QUANTITY":>12} {"VALUE":>12}')
for h in resp["holdings"]:
    s = securities[h["security_id"]]
    print(f'{s.get("ticker_symbol") or "-":8} {s.get("type"):14} {h["quantity"]:>12} {h["institution_value"]:>12}')
