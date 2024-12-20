bind = "0.0.0.0:8080"
workers = 2
timeout = 120  # Increase from default 30 seconds
keepalive = 5
worker_class = "sync"

# Logging
loglevel = "debug"
accesslog = "-"
errorlog = "-"
