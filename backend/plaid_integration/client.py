# from functools import lru_cache

# import plaid
# from django.conf import settings
# from plaid.api import plaid_api

# ENVIRONMENTS = {
#     "sandbox": plaid.Environment.Sandbox,
#     "production": plaid.Environment.Production,
# }


# @lru_cache
# def get_client() -> plaid_api.PlaidApi:
#     config = plaid.Configuration(
#         host=ENVIRONMENTS[settings.PLAID_ENV],
#         api_key={"clientId": settings.PLAID_CLIENT_ID, "secret": settings.PLAID_SECRET},
#     )
#     return plaid_api.PlaidApi(plaid.ApiClient(config))


import os
from pathlib import Path
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

env = {"sandbox": plaid.Environment.Sandbox,
       "production": plaid.Environment.Production}[os.environ.get("PLAID_ENV", "sandbox")]

config = plaid.Configuration(
    host=env,
    api_key={"clientId": os.environ["PLAID_CLIENT_ID"],
             "secret": os.environ["PLAID_SECRET"]},
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))