"""Constants for the Essent Dynamic Pricing integration."""
from datetime import timedelta

DOMAIN = "essent_dynamic"
API_URL = "https://www.essent.nl/api/public/dynamicpricing/dynamic-prices/v1"

# We update once every hour to catch tomorrow's prices when they become available
SCAN_INTERVAL = timedelta(hours=1)
