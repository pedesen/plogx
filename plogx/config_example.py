"""
copy this file to config.py and make some adjustments to configure plogx!
"""

# List of paths to ignore (useful for css and js files)
excluded_paths = []

# List of IPs to ignore if you want to blacklist some requests
excluded_ips = []

# Ignore log items, which contain one of these strings in the client field
# Note that you can use regex expressions here Example to ignore Googlebots:
# excluded_clients = [".*Googlebot.*",]
excluded_clients = []