from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import os
import plaid
from plaid.api import plaid_api

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)

client = plaid_api.PlaidApi(plaid.ApiClient(configuration))