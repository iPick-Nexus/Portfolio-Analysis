# Portfolio-Optimization (Team 2)

Part of the iPick ML build, which is split across three repos:
- Stock-Recommendations (Team 1): package stock_recs, plus the shared contracts/ and vendor/ packages.
- Portfolio-Optimization (this repo, Team 2): package portfolio_analysis (portfolio_analysis/portfolio and portfolio_analysis/llm).
- Portfolio-Reinforcement-Learning (Team 3): package pick_agents.

The private iPick Flask backend (iPickAI_flask) installs all three as pip packages pinned to git tags. Code in portfolio_analysis/ NEVER reads or writes iPick's S3, database, Flask app or user data.

## Exception: backend/ (Plaid portfolio ingestion)
backend/ is a Django app that links user brokerage accounts through Plaid and ingests their holdings into the positions shape (see "Data facts" below). It is the only place allowed to:
- call the Plaid API (through backend/plaid_integration/client.py get_client()),
- store user data (Plaid access tokens and items) in its own database.
Credentials come from environment variables (.env locally, never committed). Tests mock get_client() and never call Plaid. portfolio_analysis/ must not import from backend/; it receives positions as plain inputs.
Run it from backend/ with its own venv: `python3.11 -m venv venv && venv/bin/pip install -r ../requirements.txt`.

## Dependencies
- stock-recommendations (Team 1) is pinned by tag in pyproject.toml. It provides stock_recs.data (load_prices, build_features) and the shared contracts and vendor packages. Import them as `from contracts.types import ...` and `from vendor.track_leader import ...`.
- pick-agents (Team 3) is added in week 6, pinned by tag, for pick_agents.agents.pump_dump.flag_pump_dump.
- Run `python scripts/link_shared.py` after installing: it creates gitignored links contracts/ and vendor/ pointing at the installed copies, so you can read them in the repo. Never edit them; open an issue on Stock-Recommendations and tag a PM.

## Folders
- portfolio_analysis/portfolio, portfolio_analysis/llm: Team 2.
- fixtures/: PM-owned copy of the shared fixture export. Don't edit it.
- examples/: example JSON outputs for the backend.
- tests/team2 and tests/contract (PM-owned).

## Rules
- Write pure functions and classes. Inputs are pandas DataFrames, dicts or the dataclasses in contracts/types.py. Outputs are JSON-serializable dataclasses or DataFrames that match contracts/.
- The only network access allowed: price downloads in stock_recs/data/prices.py (yfinance), and LLM calls through the LLMClient protocol the caller passes in. Tests never touch the network; mock both.
- Never hard-code paths, bucket names, credentials, API keys or model names. Take them as arguments.
- Point-in-time: every function that computes something "as of" a date takes `as_of` explicitly and uses only data dated on or before it. Labels and rewards are the only things that look forward, and they live in functions whose names say so (forward_*, settle_*).
- Put tunable thresholds in the JSON block of skills/NAME/SKILL.md. Load and validate them at import, following vendor/track_leader.py load_leader_policy(). Fail loudly on a bad policy.
- Versions must match production: Python 3.11, pandas==2.3.0, numpy==1.26.4. Add dependencies only to pyproject.toml, pinned, and compatible with these.
- Every public function gets a pytest test that uses fixtures/. CI must pass before merging. Keep PRs small.

## Data facts from production
- fixtures/universe.parquet: ticker, companyName, industry, tradable (bool), asset_type ("" for common stock; otherwise ETF, Mutual Fund, Closed Fund, ...). About 11,000 rows. Tickers ending in "USD" are crypto. Stock recommendations and agent candidate lists use only tradable rows with an empty asset_type and no crypto.
- iPick tickers use "." for share classes (BRK.B). Yahoo uses "-". Always convert with vendor/yf_symbols.py get_ticker_yf(); never write your own mapping.
- fixtures/ticker_track.json maps ticker -> track display name (about 1,500 tracks). The value "-" means no track. Compare and group tracks only through vendor/util_track.py normalize(name).
- fixtures/yf_info_snapshot.parquet: one row per ticker, holding Yahoo Finance info fields (marketCap, revenueGrowth, profitMargins, netIncomeToCommon, trailingPE, forwardPE, beta, averageVolume, floatShares, sharesOutstanding, heldPercentInstitutions, shortPercentOfFloat, sector, industry, currency). revenueGrowth is latest-quarter year-over-year growth as a fraction (0.20 = 20%). THIS IS TODAY'S SNAPSHOT: never use it as a feature in training or backtests (that would be lookahead). Use it only for live filters and display.
- For ETFs and funds, size is totalAssets, and the fundamental fields are None.
- Non-USD companies report marketCap in their own currency. fixtures/usd_currency_ratio.json gives currency -> units per 1 USD. Divide by the ratio to get USD.
- fixtures/track_table_sample.json holds track rows in the backend's shape. Returns look like "1y return": ["25.00%", 25], where the first element is a percent string. Parse them with vendor/track_leader.py period_return().
- The track leader rule is vendor/track_leader.py select_track_leader(stocks, expected_count). Call it; never reimplement it. Live code receives leaders as a dict {normalized_track: ticker} from the caller.
- fixtures/positions_sample.json (synthetic) has the backend's portfolio shape: a list of {symbol, shares, price, total_value, profit_loss, weight, todays_gain_loss, avg_cost}. weight is a PERCENT from 0 to 100. There is a "CASH" row.

## Frames (see contracts/frames.md for exact dtypes)
- PriceFrame (long format): date (datetime64, naive, trading days only), ticker (iPick ticker), adj_close, close, volume. Unique on (date, ticker). SPY is always included as the benchmark.
- FeatureFrame: as_of, ticker, track, normalized_track, eligible, plus the feature columns listed in contracts/features.md (Team 1). Unique on (as_of, ticker).

## Types
contracts/types.py: Recommendation, Holding, PortfolioInput, TrackAssignment, DominanceFinding, PortfolioReport, Pick, Reward, LLMClient. Use these exact types at every public boundary.
