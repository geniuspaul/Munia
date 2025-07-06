# middleware/bot_blocker.py

import re
from django.http import JsonResponse
from django.core.cache import cache

SUSPICIOUS_UA = [
    r'bot', r'scrapy', r'httpclient', r'headlesschrome', r'selenium', r'python-requests'
]

def is_bot(ua):
    ua = ua.lower()
    return any(re.search(b, ua) for b in SUSPICIOUS_UA)

class BotBlockerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ua = request.META.get("HTTP_USER_AGENT", "")
        ip = request.META.get("REMOTE_ADDR")

        # Block if suspicious User-Agent
        if is_bot(ua):
            return JsonResponse({"error": "Bot access denied"}, status=403)

        # Rate limit by IP
        cache_key = f"req-ip:{ip}"
        hits = cache.get(cache_key, 0)
        if hits > 100:
            return JsonResponse({"error": "Too many requests. Blocked."}, status=429)
        cache.set(cache_key, hits + 1, timeout=60)

        return self.get_response(request)
