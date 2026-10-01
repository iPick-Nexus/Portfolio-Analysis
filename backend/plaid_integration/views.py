from django.shortcuts import render

import json
import plaid
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from plaid.model.country_code import CountryCode
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

from .client import get_client
from .models import PlaidItem


def _plaid_error(e: plaid.ApiException) -> JsonResponse:
    return JsonResponse({"error": json.loads(e.body)}, status = 502)


@login_required
def connect_page(request):
    return render(request, "plaid_integratio/connect.html")


@login_required
@require_POST
def create_link_token(request):
    try:
        resp = get_client.link_token_create(LinkTokenCreateRequestUser(
            user=LinkTokenCreateRequestUser(client_user_id=str(request.user.id)),
            client_name="iPick",
            products=[Products("investment")],
            country_codes=[CountryCode("US")],
            language="en",
        ))
    except plaid.ApiException as e:
        return _plaid_error(e)

    return JsonResponse({"link_token": resp["link_token"]})

@login_required
@require_POST
def exchange_public_token(request):
    body = json.loads(request.body)
    try:
        resp = get_client().item_public_token_exchange(
            ItemPublicTokenExchangeRequest(public_token=body["public_token"])
        )
    except plaid.ApiException as e:
        return  _plaid_error(e)
    PlaidItem.objects.update_or_create(
        item_id=resp["item_id"],
        defaults={
            "user": request.user,
            "access_token": resp["access_token"],
            "institution_name": body.get("institution_name", ""),
        },
    )
    return JsonResponse({"ok": True})


@login_required
def holdings(request):
    try:
        raw = [fetch_holdings(item.access_token) for item in request.user.plaid_items.all()]
    except plaid.ApiException as e:
        return _plaid_error(e)
    return JsonResponse({"positions": holdings_to_positions(raw)})
    
