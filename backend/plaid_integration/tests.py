import json
from unittest.mock import MagicMock, patch

import plaid
from django.contrib.auth import get_user_model
from django.test import TestCase

from .intake import fetch_holdings
from .models import PlaidItem

# Trimmed investments_holdings_get response, same shape as Plaid Sandbox (First Platypus Bank).
HOLDINGS_RESPONSE = {
    "accounts": [],
    "securities": [
        {"security_id": "sec-cash", "ticker_symbol": None, "name": "U S Dollar", "type": "cash"},
        {"security_id": "sec-sbsi", "ticker_symbol": "SBSI", "name": "Southside Bancshares", "type": "equity"},
        {"security_id": "sec-ewz", "ticker_symbol": "EWZ", "name": "iShares MSCI Brazil", "type": "etf"},
        {"security_id": "sec-bond", "ticker_symbol": None, "name": "Trp Equity Income", "type": "fixed income"},
    ],
    "holdings": [
        {"security_id": "sec-cash", "quantity": 12345.67, "institution_value": 12345.67, "cost_basis": 12345.67},
        {"security_id": "sec-sbsi", "quantity": 213.0, "institution_value": 7397.49, "cost_basis": 10000.0},
        {"security_id": "sec-ewz", "quantity": 5.0, "institution_value": 210.75, "cost_basis": None},
        {"security_id": "sec-bond", "quantity": 10.0, "institution_value": 948.08, "cost_basis": 940.0},
    ],
}


def holdings_mock(*responses):
    """Mock for client.investments_holdings_get; returns one response per call."""
    return MagicMock(side_effect=[MagicMock(to_dict=MagicMock(return_value=r)) for r in responses])


def plaid_error(status=400, body=None):
    e = plaid.ApiException(status=status, reason="Bad Request")
    e.body = json.dumps(body or {"error_code": "INVALID_PUBLIC_TOKEN", "error_message": "bad token"})
    return e


class FetchHoldingsTests(TestCase):
    @patch("plaid_integration.intake.client")
    def test_returns_tickered_non_cash_holdings(self, client):
        client.investments_holdings_get = holdings_mock(HOLDINGS_RESPONSE)
        rows = fetch_holdings("access-1")
        self.assertEqual([r["ticker"] for r in rows], ["SBSI", "EWZ"])

    @patch("plaid_integration.intake.client")
    def test_row_fields(self, client):
        client.investments_holdings_get = holdings_mock(HOLDINGS_RESPONSE)
        sbsi = fetch_holdings("access-1")[0]
        self.assertEqual(sbsi, {
            "ticker": "SBSI",
            "name": "Southside Bancshares",
            "type": "equity",
            "quantity": 213.0,
            "value": 7397.49,
            "cost_basis": 10000.0,
        })

    @patch("plaid_integration.intake.client")
    def test_sends_access_token(self, client):
        client.investments_holdings_get = holdings_mock(HOLDINGS_RESPONSE)
        fetch_holdings("access-1")
        request = client.investments_holdings_get.call_args.args[0]
        self.assertEqual(request.access_token, "access-1")

    @patch("plaid_integration.intake.client")
    def test_empty_account(self, client):
        client.investments_holdings_get = holdings_mock({"accounts": [], "securities": [], "holdings": []})
        self.assertEqual(fetch_holdings("access-1"), [])


class ViewTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user("alice", password="pw")
        self.other = User.objects.create_user("bob", password="pw")
        self.client.force_login(self.user)


class LoginRequiredTests(ViewTestCase):
    def test_all_endpoints_redirect_when_logged_out(self):
        self.client.logout()
        for method, url in [
            ("get", "/plaid/connect/"),
            ("post", "/plaid/link-token/"),
            ("post", "/plaid/exchange/"),
            ("get", "/plaid/holdings/"),
        ]:
            r = getattr(self.client, method)(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertIn("/admin/login/", r["Location"])


class ConnectPageTests(ViewTestCase):
    def test_renders_plaid_link(self):
        r = self.client.get("/plaid/connect/")
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "plaid_integration/connect.html")
        self.assertContains(r, "link-initialize.js")


class LinkTokenTests(ViewTestCase):
    @patch("plaid_integration.views.client")
    def test_returns_link_token(self, client):
        client.link_token_create.return_value = {"link_token": "link-sandbox-123"}
        r = self.client.post("/plaid/link-token/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"link_token": "link-sandbox-123"})

    @patch("plaid_integration.views.client")
    def test_requests_investments_for_current_user(self, client):
        client.link_token_create.return_value = {"link_token": "link-sandbox-123"}
        self.client.post("/plaid/link-token/")
        request = client.link_token_create.call_args.args[0]
        self.assertEqual(request.user.client_user_id, str(self.user.id))
        self.assertEqual([p.value for p in request.products], ["investments"])

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get("/plaid/link-token/").status_code, 405)

    @patch("plaid_integration.views.client")
    def test_plaid_error_returns_502(self, client):
        client.link_token_create.side_effect = plaid_error(body={"error_code": "INVALID_API_KEYS"})
        r = self.client.post("/plaid/link-token/")
        self.assertEqual(r.status_code, 502)
        self.assertEqual(r.json()["error"]["error_code"], "INVALID_API_KEYS")


class ExchangeTests(ViewTestCase):
    def post(self, **body):
        return self.client.post("/plaid/exchange/", json.dumps(body), content_type="application/json")

    @patch("plaid_integration.views.client")
    def test_saves_item_for_current_user(self, client):
        client.item_public_token_exchange.return_value = {"item_id": "item-1", "access_token": "access-1"}
        r = self.post(public_token="public-1", institution_name="First Platypus Bank")
        self.assertEqual(r.status_code, 200)
        item = PlaidItem.objects.get(item_id="item-1")
        self.assertEqual(item.user, self.user)
        self.assertEqual(item.access_token, "access-1")
        self.assertEqual(item.institution_name, "First Platypus Bank")
        self.assertEqual(client.item_public_token_exchange.call_args.args[0].public_token, "public-1")

    @patch("plaid_integration.views.client")
    def test_relinking_same_item_updates_instead_of_duplicating(self, client):
        client.item_public_token_exchange.side_effect = [
            {"item_id": "item-1", "access_token": "access-old"},
            {"item_id": "item-1", "access_token": "access-new"},
        ]
        self.post(public_token="public-1")
        self.post(public_token="public-2")
        self.assertEqual(PlaidItem.objects.count(), 1)
        self.assertEqual(PlaidItem.objects.get().access_token, "access-new")

    @patch("plaid_integration.views.client")
    def test_plaid_error_saves_nothing(self, client):
        client.item_public_token_exchange.side_effect = plaid_error()
        r = self.post(public_token="bad")
        self.assertEqual(r.status_code, 502)
        self.assertEqual(r.json()["error"]["error_code"], "INVALID_PUBLIC_TOKEN")
        self.assertFalse(PlaidItem.objects.exists())


class HoldingsTests(ViewTestCase):
    @patch("plaid_integration.intake.client")
    def test_no_linked_accounts(self, client):
        r = self.client.get("/plaid/holdings/")
        self.assertEqual(r.json(), {"holdings": []})
        client.investments_holdings_get.assert_not_called()

    @patch("plaid_integration.intake.client")
    def test_combines_all_linked_accounts(self, client):
        PlaidItem.objects.create(user=self.user, item_id="item-1", access_token="access-1")
        PlaidItem.objects.create(user=self.user, item_id="item-2", access_token="access-2")
        client.investments_holdings_get = holdings_mock(HOLDINGS_RESPONSE, HOLDINGS_RESPONSE)
        r = self.client.get("/plaid/holdings/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([h["ticker"] for h in r.json()["holdings"]], ["SBSI", "EWZ", "SBSI", "EWZ"])

    @patch("plaid_integration.intake.client")
    def test_only_fetches_current_users_items(self, client):
        PlaidItem.objects.create(user=self.user, item_id="item-1", access_token="access-mine")
        PlaidItem.objects.create(user=self.other, item_id="item-2", access_token="access-bob")
        client.investments_holdings_get = holdings_mock(HOLDINGS_RESPONSE)
        self.client.get("/plaid/holdings/")
        tokens = [c.args[0].access_token for c in client.investments_holdings_get.call_args_list]
        self.assertEqual(tokens, ["access-mine"])

    @patch("plaid_integration.intake.client")
    def test_plaid_error_returns_502(self, client):
        PlaidItem.objects.create(user=self.user, item_id="item-1", access_token="access-1")
        client.investments_holdings_get.side_effect = plaid_error(body={"error_code": "ITEM_LOGIN_REQUIRED"})
        r = self.client.get("/plaid/holdings/")
        self.assertEqual(r.status_code, 502)
        self.assertEqual(r.json()["error"]["error_code"], "ITEM_LOGIN_REQUIRED")
