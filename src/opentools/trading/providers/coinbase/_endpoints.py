from __future__ import annotations

COINBASE_LIVE_URL = "https://api.coinbase.com"
COINBASE_SANDBOX_URL = "https://api-sandbox.coinbase.com"

# shared prefix
_API_PREFIX = "/api/v3/brokerage"

# accounts
ACCOUNT_PATH = f"{_API_PREFIX}/accounts/{{account_uuid}}"
ACCOUNTS_PATH = f"{_API_PREFIX}/accounts"

# portfolios / balances
PORTFOLIOS_PATH = f"{_API_PREFIX}/portfolios"
PORTFOLIO_BREAKDOWN_PATH = f"{_API_PREFIX}/portfolios/{{portfolio_id}}"
TRANSACTION_SUMMARY_PATH = f"{_API_PREFIX}/transaction_summary"

# orders
ORDERS_PATH = f"{_API_PREFIX}/orders"
ORDERS_BATCH_CANCEL_PATH = f"{_API_PREFIX}/orders/batch_cancel"
ORDERS_HISTORICAL_PATH = f"{_API_PREFIX}/orders/historical/batch"
ORDER_HISTORICAL_PATH = f"{_API_PREFIX}/orders/historical/{{order_id}}"
ORDERS_PREVIEW_PATH = f"{_API_PREFIX}/orders/preview"

# products (symbols, not prices)
PRODUCTS_PATH = f"{_API_PREFIX}/products"
PRODUCT_PATH = f"{_API_PREFIX}/products/{{product_id}}"
