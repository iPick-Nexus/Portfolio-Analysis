from functools import lru_cache

import plaid
from django.conf import settings
from plaid.api import plaid_api

ENVIRONMENTS = {
    "sandbox": plaid.Environment.Sandbox,
    "production": plaid.Environment.Production,
}


@lru_cache
def get_client() -> plaid_api.PlaidApi:
    config = plaid.Configuration(
        host=ENVIRONMENTS[settings.PLAID_ENV],
        api_key={"clientId": settings.PLAID_CLIENT_ID, "secret": settings.PLAID_SECRET},
    )
    return plaid_api.PlaidApi(plaid.ApiClient(config))
