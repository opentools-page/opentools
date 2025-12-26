from __future__ import annotations

COINBASE_LIVE_URL = "https://api.coinbase.com/api/v3/brokerage"
COINBASE_SANDBOX_URL = "https://api-sandbox.coinbase.com/api/v3/brokerage"

# accounts
ACCOUNTS_PATH = "/accounts"
ACCOUNT_PATH = "/accounts/{account_id}"

# portfolios / balances
PORTFOLIOS_PATH = "/portfolios"
PORTFOLIO_BREAKDOWN_PATH = "/portfolios/{portfolio_id}"
TRANSACTION_SUMMARY_PATH = "/transaction_summary"

# orders
ORDERS_PATH = "/orders"
ORDERS_BATCH_CANCEL_PATH = "/orders/batch_cancel"
ORDERS_HISTORICAL_PATH = "/orders/historical/batch"
ORDER_HISTORICAL_PATH = "/orders/historical/{order_id}"
ORDERS_PREVIEW_PATH = "/orders/preview"

# products (symbols, not prices)
PRODUCTS_PATH = "/products"
PRODUCT_PATH = "/products/{product_id}"
