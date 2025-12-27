from __future__ import annotations

# Base hosts
COINBASE_LIVE_URL = "https://api.coinbase.com"
COINBASE_SANDBOX_URL = "https://api-sandbox.coinbase.com"

_API_PREFIX = "/api/v3/brokerage"

# accounts
ACCOUNT_PATH = f"{_API_PREFIX}/accounts/{{account_uuid}}"
ACCOUNTS_PATH = f"{_API_PREFIX}/accounts"

# orders
ORDERS_PATH = f"{_API_PREFIX}/orders"
ORDERS_BATCH_CANCEL_PATH = f"{_API_PREFIX}/orders/batch_cancel"
ORDERS_HISTORICAL_PATH = f"{_API_PREFIX}/orders/historical/batch"
ORDER_HISTORICAL_PATH = f"{_API_PREFIX}/orders/historical/{{order_id}}"
ORDERS_PREVIEW_PATH = f"{_API_PREFIX}/orders/preview"

# products (assets)
PRODUCTS_PATH = f"{_API_PREFIX}/products"
PRODUCT_PATH = f"{_API_PREFIX}/products/{{product_id}}"
