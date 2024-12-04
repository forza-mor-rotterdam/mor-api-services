import json
import logging

import jwt
import requests
import urllib3
from django.conf import settings
from django.core.validators import URLValidator

logger = logging.getLogger(__name__)


class MercureService:
    _subscribe_targets = ["*"]
    _publish_targets = []
    _mercure_url = None
    _mercure_publisher_jwt_key = None
    _mercure_subscriber_jwt_key = None

    class ConfigException(Exception):
        ...

    def __init__(self):
        self._publish_targets = settings.MERCURE_PUBLISH_TARGETS
        try:
            validate = URLValidator()
            validate(settings.APP_MERCURE_PUBLIC_URL)
        except Exception as e:
            logentry = (
                f"Config error: APP_MERCURE_PUBLIC_URL is not a valid url, error: {e}"
            )
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)
        if not settings.MERCURE_PUBLISHER_JWT_KEY:
            logentry = "Config error: MERCURE_PUBLISHER_JWT_KEY is None"
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)
        if not settings.MERCURE_SUBSCRIBER_JWT_KEY:
            logentry = "Config error: MERCURE_SUBSCRIBER_JWT_KEY is None"
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)

        self._mercure_url = settings.APP_MERCURE_INTERNAL_URL
        self._mercure_publisher_jwt_key = settings.MERCURE_PUBLISHER_JWT_KEY
        self._mercure_publisher_jwt_alg = settings.MERCURE_PUBLISHER_JWT_ALG
        self._mercure_subscriber_jwt_key = settings.MERCURE_SUBSCRIBER_JWT_KEY
        self._mercure_subscriber_jwt_alg = settings.MERCURE_SUBSCRIBER_JWT_ALG

    def _get_headers(self, token):
        return {
            "user-agent": urllib3.util.SKIP_HEADER,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _get_jwt_token(self, key, algorithm="HS256", mercure_payload=None):
        payload = {
            "mercure": {
                "subscribe": self._subscribe_targets,
                "publish": self._publish_targets,
            },
        }
        if mercure_payload:
            payload["mercure"]["payload"] = mercure_payload
        return jwt.encode(
            payload,
            key,
            algorithm=algorithm,
        )

    def publish(self, topic: str, data=[]):
        data = {
            "topic": topic,
            "data": json.dumps(data),
        }

        response = requests.post(
            self._mercure_url,
            data=data,
            headers=self._get_headers(self.get_publisher_token()),
        )
        response.raise_for_status()

        return response

    def get_subscriptions(self):
        response = requests.get(
            f"{self._mercure_url}/subscriptions",
            headers=self._get_headers(self.get_subscriber_token()),
        )
        response.raise_for_status()
        return response.json()

    def get_subscriber_token(self, payload=None):
        return self._get_jwt_token(
            self._mercure_subscriber_jwt_key,
            mercure_payload=payload,
            algorithm=self._mercure_subscriber_jwt_alg,
        )

    def get_publisher_token(self, payload=None):
        return self._get_jwt_token(
            self._mercure_publisher_jwt_key,
            mercure_payload=payload,
            algorithm=self._mercure_publisher_jwt_alg,
        )
