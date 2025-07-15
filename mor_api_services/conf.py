try:
    from django.conf import settings
    MOR_API_SERVICES = getattr(settings, "MOR_API_SERVICES", {})
except Exception:
    MOR_API_SERVICES = {}

MOR_API_SERVICES.setdefault("API_PAD", "api/v1")
MOR_API_SERVICES.setdefault("API_TOKEN_PAD", "api-token-auth")
MOR_API_SERVICES.setdefault("BLOKKEER_TOKEN_GEBRUIK", False)