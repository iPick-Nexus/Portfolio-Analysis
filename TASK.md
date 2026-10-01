# Task: Build the Plaid endpoints

**Goal:** write the four endpoints that let a user connect a brokerage account through Plaid and see their holdings.

**Done when:** `python manage.py test plaid_integration` shows all 19 tests passing, and you've opened a pull request.

## Before you start

1. Finish the **Setup** section of the [root README](README.md): Python 3.11 (3.12 is okay; 3.13 and newer won't install), venv, packages, `.env` with Plaid keys, `migrate`. Do this before the session if you can.
2. **Plaid keys:** you've been invited to our Plaid team. Copy the **client ID** and the **Sandbox secret** from the [Plaid dashboard → Developers → Keys](https://dashboard.plaid.com/developers/keys) into your `.env` file (see README step 5). Never commit `.env` or paste the keys anywhere else.
3. Make your own branch:
   ```bash
   git checkout main
   git pull
   git checkout -b <your-name>/plaid-endpoints
   ```

## How it fits together

An **endpoint** is a URL your server answers. The browser sends a request (a method like GET or POST, plus maybe some data), and your view function sends back a response (here, JSON plus a status code). [`urls.py`](backend/plaid_integration/urls.py) connects each URL to a function in [`views.py`](backend/plaid_integration/views.py).

Connecting a brokerage takes three requests. The connect page makes them in this order:

```
Browser                         Our server (views.py)                Plaid
───────                         ─────────────────────                ─────
1. Click "Connect brokerage"
   POST /plaid/link-token/  ──► create_link_token  ──── asks for ──► link token
                            ◄── {"link_token": ...}
2. Plaid popup opens; user logs in to their bank (handled entirely by Plaid)
   Plaid gives the browser a short-lived public token
3. POST /plaid/exchange/    ──► exchange_public_token ── swaps ────► access token
                                saves it in the database (PlaidItem)
                            ◄── {"ok": true}
4. GET /plaid/holdings/     ──► holdings  ── for each saved item ──► holdings
                            ◄── {"holdings": [...]}
```

`GET /plaid/connect/` (`connect_page`) serves the page with the button. That page is already written in [`templates/plaid_integration/connect.html`](backend/plaid_integration/templates/plaid_integration/connect.html).

## What to do

Fill in the four functions in [`views.py`](backend/plaid_integration/views.py). Each one currently says `raise NotImplementedError`. **The TODO comment above each function tells you exactly what it must do.** Replace `raise NotImplementedError` with your code.

Suggested order, easiest first:

| # | Function | URL | Tests that check it | Difficulty |
|---|---|---|---|---|
| 1 | `connect_page` | `GET /plaid/connect/` | `ConnectPageTests` | Easy |
| 2 | `holdings` | `GET /plaid/holdings/` | `HoldingsTests` | Easy–Medium |
| 3 | `create_link_token` | `POST /plaid/link-token/` | `LinkTokenTests` | Medium |
| 4 | `exchange_public_token` | `POST /plaid/exchange/` | `ExchangeTests` | Medium (uses the database) |

The slides from the session include a worked example endpoint. Use it as your pattern.

**Only edit `views.py`.** Don't change `tests.py`, `intake.py`, `models.py`, `urls.py`, `client.py` or the template. If you think one of them is wrong, ask a PM.

## Check your work

The tests in [`tests.py`](backend/plaid_integration/tests.py) work like an autograder. They fake Plaid's responses, so they never call the real Plaid, but they do check that your code calls Plaid correctly and returns the right thing.

From the `backend/` folder, with your venv active:

```bash
python manage.py test plaid_integration
```

- **At the start** you'll see `Ran 19 tests` and `FAILED (errors=12)`. That's expected: 7 tests already pass, and the 12 errors are the unfinished functions.
- **When you're done** you'll see `OK`.

To run only the tests for the function you're working on:

```bash
python manage.py test plaid_integration.tests.ConnectPageTests
python manage.py test plaid_integration.tests.HoldingsTests
python manage.py test plaid_integration.tests.LinkTokenTests
python manage.py test plaid_integration.tests.ExchangeTests
```

When a test fails, read the **last few lines** of its output first. They say what the test expected and what your code returned. A test's name (for example `test_relinking_same_item_updates_instead_of_duplicating`) tells you which rule you missed.

### What about `plaid_demo.py`?

[`backend/plaid_demo.py`](backend/plaid_demo.py) (it used to be `test_plaid.py` in the repo root) is **not** a test of your work. It calls the real Plaid Sandbox directly and prints a fake brokerage's holdings, so you can see what raw Plaid data looks like. It never touches `views.py`, so it prints the same thing whether or not your code works. Run it from `backend/` if you're curious:

```bash
python plaid_demo.py
```

## See it working for real (optional)

The tests use fake Plaid responses. To watch all four endpoints work together against the real Plaid Sandbox:

1. Make a login if you don't have one: `python manage.py createsuperuser`. The endpoints require a logged-in user.
2. `python manage.py runserver`
3. Log in at http://127.0.0.1:8000/admin/
4. Open http://127.0.0.1:8000/plaid/connect/ and click **Connect brokerage**.
5. In the Plaid popup, pick any bank (for example First Platypus Bank) and log in with username `user_good` and password `pass_good`. These are Plaid's fake Sandbox credentials.
6. Your holdings JSON appears on the page.

Open your browser's dev tools (F12) → **Network** tab before clicking. You'll see the page call `/plaid/link-token/`, then `/plaid/exchange/`, then `/plaid/holdings/`: your three endpoints, in order.

## Rules

- **Never print or log an access token.** It gives ongoing access to someone's brokerage data. Treat it like a password.
- **Never commit `.env`** or put keys in code.
- **Don't edit the tests to make them pass.** If a test looks wrong, ask a PM.

## Stuck?

If you've been stuck for **15 minutes**, ask your partner or a PM. Bring the error message (the last few lines) and what you've tried. Being stuck is normal. Staying stuck silently wastes the session.

## When you're done

```bash
git add backend/plaid_integration/views.py
git commit -m "Implement Plaid endpoints"
git push -u origin <your-name>/plaid-endpoints
```

Then open a pull request on GitHub and post the link in the team channel.
