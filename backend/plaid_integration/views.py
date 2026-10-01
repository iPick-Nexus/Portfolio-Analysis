import json

import plaid
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

from .client import client
from .intake import fetch_holdings
from .models import PlaidItem


def _plaid_error(e: plaid.ApiException) -> JsonResponse:
    return JsonResponse({"error": json.loads(e.body)}, status=502)


# TODO: connect_page(request)  ->  GET /plaid/connect/
# Serves the "Connect brokerage" page.
# - Login required.
# - Render the template "plaid_integration/connect.html" (already written). That page
#   loads Plaid Link and calls the three endpoints below.
@login_required
def connect_page(request):
    raise NotImplementedError


# TODO: create_link_token(request)  ->  POST /plaid/link-token/
# Gets a link token from Plaid so the browser can open the Plaid Link popup.
# - Login required, POST only.
# - Call client.link_token_create(LinkTokenCreateRequest(...)) with:
#     user = LinkTokenCreateRequestUser(client_user_id=<the logged-in user's id, as a string>)
#     client_name = "iPick", products = [Products("investments")],
#     country_codes = [CountryCode("US")], language = "en"
# - Return JSON: {"link_token": <resp["link_token"]>}
# - If Plaid raises plaid.ApiException, return _plaid_error(e).
@login_required
@require_POST
def create_link_token(request):
    raise NotImplementedError


# TODO: exchange_public_token(request)  ->  POST /plaid/exchange/
# Called by the page after the user finishes Plaid Link. Swaps the short-lived public
# token for a permanent access token and saves the linked brokerage.
# - Login required, POST only.
# - Request body is JSON: {"public_token": "...", "institution_name": "..."}
#   (institution_name is optional; default to "").
# - Call client.item_public_token_exchange(ItemPublicTokenExchangeRequest(public_token=...)).
#   The response has resp["item_id"] and resp["access_token"].
# - Save a PlaidItem for request.user with item_id, access_token and institution_name.
#   Use update_or_create keyed on item_id so relinking the same brokerage updates the
#   row instead of creating a duplicate.
# - Return JSON: {"ok": true}
# - If Plaid raises plaid.ApiException, return _plaid_error(e) and save nothing.
@login_required
@require_POST
def exchange_public_token(request):
    raise NotImplementedError


# TODO: holdings(request)  ->  GET /plaid/holdings/
# Returns the logged-in user's holdings across all their linked brokerages.
# - Login required.
# - For each PlaidItem belonging to request.user (request.user.plaid_items.all()),
#   call fetch_holdings(item.access_token) from intake.py and combine the lists.
#   Never fetch another user's items.
# - Return JSON: {"holdings": [...]}  (an empty list if nothing is linked).
# - If Plaid raises plaid.ApiException, return _plaid_error(e).
@login_required
def holdings(request):
    raise NotImplementedError
