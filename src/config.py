DOMAIN_RATE_LIMIT = 5
ENABLE_DEBUG_OUTPUT = True
ENABLE_DEBUG_NOFORWARD = True # If set to True, will not forward requests, instead it will hang for 3 seconds on the request. Intended to test the rate limiter



############################
# REDIS CONFIGURATION
# Replace with your own credentials
############################


redis_endpoint = "redis://redis-endpoint.com"

redis_pass = "USER"
redis_user = "PASS"




