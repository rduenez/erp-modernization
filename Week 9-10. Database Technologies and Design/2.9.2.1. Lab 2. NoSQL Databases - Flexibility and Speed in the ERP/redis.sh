podman exec -it erp-redis redis-cli

# User 987 adds 2 Developer Laptops to their cart
HSET cart:user987 TECH-101 2

# User 987 adds 5 Company Tees to their cart
HSET cart:user987 APP-505 5

# Set an expiration (Time-To-Live). The cart will automatically delete itself after 3600 seconds (1 hour)
EXPIRE cart:user987 3600

HGETALL cart:user987
