# Task: Build the Plaid endpoints

**Goal:** write the four endpoints that let a user connect a brokerage account through Plaid and see their holdings.

**Done when:** `python manage.py test plaid_integration` shows all 19 tests passing in the shared session, and the host has opened one pull request.

## How this session works

We all work in **one shared copy of the code** over VS Code Live Share. A PM hosts the session, which means the code, the terminal and the tests all run on the host's computer. You edit the host's files from your own VS Code.

The team is split into **three groups**. Each group owns one part of [`views.py`](backend/plaid_integration/views.py):

| Group | Function(s)                       | URL                                               | Tests that check it                     | Difficulty                 | Members |
| ----- | --------------------------------- | ------------------------------------------------- | --------------------------------------- | -------------------------- | ------- |
| 1     | `connect_page` and `holdings` | `GET /plaid/connect/`, `GET /plaid/holdings/` | `ConnectPageTests`, `HoldingsTests` | Easy–Medium               |         |
| 2     | `create_link_token`             | `POST /plaid/link-token/`                       | `LinkTokenTests`                      | Medium                     |         |
| 3     | `exchange_public_token`         | `POST /plaid/exchange/`                         | `ExchangeTests`                       | Medium (uses the database) |         |

**Inside your group, take turns typing.** One person types (the driver), and the others read along, look things up and suggest the next line. Switch drivers every **15–20 minutes** so everyone gets the keyboard.

### Session plan

| Time       | What happens                                                                                 |
| ---------- | -------------------------------------------------------------------------------------------- |
| 0:00–0:20 | Slides: what endpoints are, how Django handles a request, the Plaid flow, the worked example |
| 0:20–0:30 | Join Live Share, find your group's function, run your tests once and watch them fail         |
| 0:30–1:40 | Build it in your group                                                                       |
| 1:40–1:55 | Teach-back: each group spends 3 minutes walking everyone through their function              |
| 1:55–2:00 | Live demo: connect a fake brokerage with everyone's code running together                    |

## Before the session

1. **Install VS Code and the [Live Share extension](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare).** Sign in with GitHub or Microsoft. The host will post a join link at the start.
2. **Do the Setup section of the [root README](README.md)** if you can: Python 3.11 (3.12 is okay; 3.13 and newer won't install), venv, ok, `.env` with Plaid keys, `migrate`. You don't need it to edit in Live Share, but future tasks are done on your own computer, and it lets you run the tests and the demo yourself afterward.
3. **Plaid keys:** you've been invited to our Plaid team. Copy the **client ID** and the **Sandbox secret** from the [Plaid dashboard → Developers → Keys](https://dashboard.plaid.com/developers/keys) into your `.env` file (see README step 5). Never commit `.env` or paste the keys anywhere else.

## How it fits together

An **endpoint** is a URL your server answers. The browser sends a request (a method like GET or POST, plus maybe some data), and your view function sends back a response (here, JSON plus a status code). [`urls.py`](backend/plaid_integration/urls.py) connects each URL to a function in [`views.py`](backend/plaid_integration/views.py).

Connecting a brokerage takes three requests. The connect page makes them in this order:

```
Browser                         Our server (views.py)                Plaid
───────                         ─────────────────────                ─────
1. Click "Connect brokerage"
   POST /plaid/link-token/  ──► create_link_token  ──── asks for ──► link token
                            ◄── {"link_token": ...}                     (Group 2)
2. Plaid popup opens; user logs in to their bank (handled entirely by Plaid)
   Plaid gives the browser a short-lived public token
3. POST /plaid/exchange/    ──► exchange_public_token ── swaps ────► access token
                                saves it in the database (PlaidItem)    (Group 3)
                            ◄── {"ok": true}
4. GET /plaid/holdings/     ──► holdings  ── for each saved item ──► holdings
                            ◄── {"holdings": [...]}                     (Group 1)
```

`GET /plaid/connect/` (`connect_page`, Group 1) serves the page with the button. That page is already written in [`templates/plaid_integration/connect.html`](backend/plaid_integration/templates/plaid_integration/connect.html).

## What to do

Open [`views.py`](backend/plaid_integration/views.py) and find your group's function. It currently says `raise NotImplementedError`. **The TODO comment above it tells you exactly what it must do.** Replace `raise NotImplementedError` with your code.

The slides include a worked example endpoint. Use it as your pattern.

- **Only edit your group's function.** Other groups are typing in the same file at the same time.
- **Only edit `views.py`.** Don't change `tests.py`, `intake.py`, `models.py`, `urls.py`, `client.py` or the template. If you think one of them is wrong, ask a PM.

### Only save code that looks finished

Live Share shows your typing to everyone instantly, but the tests only read the **saved** file. If someone saves a half-written line with a syntax error, Django can't load `views.py`, and **every group's tests fail**, not just yours. So:

- Save when your code at least looks complete (matching brackets, no half-written lines).
- If everyone's tests suddenly fail with a `SyntaxError` or `IndentationError`, read the error. It names the file and line. Whoever owns that line fixes it.

## Check your work

The tests in [`tests.py`](backend/plaid_integration/tests.py) work like an autograder. They fake Plaid's responses, so they never call the real Plaid, but they do check that your code calls Plaid correctly and returns the right thing.

Tests run on the host's computer. Run them in the **shared terminal** the host opens, or ask the host to run them for you. Run only your group's tests, so you aren't confused by other groups' unfinished work:

```bash
python manage.py test plaid_integration.tests.ConnectPageTests   # Group 1
python manage.py test plaid_integration.tests.HoldingsTests      # Group 1
python manage.py test plaid_integration.tests.LinkTokenTests     # Group 2
python manage.py test plaid_integration.tests.ExchangeTests      # Group 3
```

(The shared terminal is already in the `backend/` folder with the venv active. If you're running them on your own computer, see the README.)

When a test fails, read the **last few lines** of its output first. They say what the test expected and what your code returned. A test's name (for example `test_relinking_same_item_updates_instead_of_duplicating`) tells you which rule you missed.

When every group is done, the full run should pass:

```bash
python manage.py test plaid_integration
```

- **At the start** it shows `Ran 19 tests` and `FAILED (errors=12)`. That's expected: 7 tests already pass, and the 12 errors are the unfinished functions.
- **When everyone is done** it shows `OK`.

### What about `plaid_demo.py`?

[`backend/plaid_demo.py`](backend/plaid_demo.py) is **not** a test of your work. It calls the real Plaid Sandbox directly and prints a fake brokerage's holdings, so you can see what raw Plaid data looks like. It never touches `views.py`, so it prints the same thing whether or not your code works. Run it from `backend/` if you're curious:

```bash
python plaid_demo.py
```

## See it working for real

The tests use fake Plaid responses. At the end of the session, the host demos all four endpoints working together against the real Plaid Sandbox. You can repeat this on your own computer afterward:

1. Make a login if you don't have one: `python manage.py createsuperuser`. The endpoints require a logged-in user.
2. `python manage.py runserver`
3. Log in at http://127.0.0.1:8000/admin/
4. Open http://127.0.0.1:8000/plaid/connect/ and click **Connect brokerage**.
5. In the Plaid popup, pick any bank (for example First Platypus Bank) and log in with username `user_good` and password `pass_good`. These are Plaid's fake Sandbox credentials.
6. Your holdings JSON appears on the page.

Open your browser's dev tools (F12) → **Network** tab before clicking. You'll see the page call `/plaid/link-token/` (Group 2), then `/plaid/exchange/` (Group 3), then `/plaid/holdings/` (Group 1): every group's endpoint, in order.

## Rules

- **Never print or log an access token.** It gives ongoing access to someone's brokerage data. Treat it like a password.
- **Never commit `.env`** or put keys in code.
- **Don't edit the tests to make them pass.** If a test looks wrong, ask a PM.
- **Don't run git commands in the shared session.** The host handles git.

## Stuck?

If your group has been stuck for **15 minutes**, ask a PM. Bring the error message (the last few lines) and what you've tried. Being stuck is normal. Staying stuck silently wastes the session.

## When you're done

Only the host commits. Once the full test run shows `OK`, the host commits `views.py` on a branch, credits every member with `Co-authored-by:` lines, and opens **one** pull request. Nobody else needs to commit or push.

```bash
git checkout -b plaid-endpoints
git add backend/plaid_integration/views.py
git commit -m "Implement Plaid endpoints

Co-authored-by: Name <github-email@example.com>
Co-authored-by: Name <github-email@example.com>"
git push -u origin plaid-endpoints
```

GitHub shows co-authors on the commit when the email matches their GitHub account.
