import logging
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode, urlparse, urljoin

import requests
import urllib3
from mor_api_services.conf import MOR_API_SERVICES
from requests import Request, Response

has_cache = True
try:
    from django.core.cache import cache
except Exception:
    has_cache = False


logger = logging.getLogger(__name__)


class BasisService:
    _gebruik_token = False
    _token_retrieve_method = "post"
    _auth_header_key = "Authorization"
    _auth_header_token_prefix = "Token"
    _timeout: tuple[int, ...] = (10, 20)
    _cache_timeout = 0
    _token_api: str = None
    _token: str = None
    _client_name: str = ""
    _default_error_message = "Er ging iets mis met het ophalen van data!"

    def __init__(self, *args, **kwargs: dict):
        basis_url = kwargs.pop("basis_url")
        self._client_name = kwargs.pop("client_name", None)
        self._base_url = str(basis_url).strip("/") if basis_url is not None else ""
        self._timeout = kwargs.pop("timeout", None)
        self._cache_timeout = kwargs.pop("cache_timeout", self._cache_timeout)
        self._token = kwargs.pop("token", self._token)
        self._request = kwargs.pop("request", None)
        self._gebruikersnaam = kwargs.pop("gebruikersnaam", None)
        self._wachtwoord = kwargs.pop("wachtwoord", None)
        self._token_timeout = kwargs.pop("token_timeout", None)
        self._api_path = kwargs.pop("api_pad", MOR_API_SERVICES["API_PAD"])
        self._token_api = kwargs.pop("api_token_pad", MOR_API_SERVICES["API_TOKEN_PAD"])
        self._token_retrieve_method = kwargs.pop("token_retrieve_method", MOR_API_SERVICES["TOKEN_RETRIEVE_METHOD"])
        self._auth_header_key = kwargs.pop("auth_header_key", MOR_API_SERVICES["AUTH_HEADER_KEY"])
        self._auth_header_token_prefix = kwargs.pop("auth_header_token_prefix", MOR_API_SERVICES["AUTH_HEADER_TOKEN_PREFIX"])

        if MOR_API_SERVICES["BLOKKEER_TOKEN_GEBRUIK"]:
            self._gebruik_token = False

        if self._gebruik_token and not self._gebruikersnaam and not self._wachtwoord and not self._token:
            logger.warning(
                f"De service '{self.__class__.__name__}' verwacht het gebruik van een token, alleen er zijn geen credentials opgegeven."
            )

        super().__init__(*args, **kwargs)

    class BasisUrlFout(Exception):
        ...

    class AntwoordFout(Exception):
        ...

    class DataOphalenFout(Exception):
        ...

    class NaarJsonFout(Exception):
        ...

    def haal_token_cache_key(self):
        return f"{self.__class__.__name__}_{self._base_url}_token"

    def haal_token(self, force_cache=False):
        if self._token:
            return self._token
        
        cache_key = self.haal_token_cache_key()
        logger.debug(f"Haal token: key={cache_key}, token_timeout={self._token_timeout}, service={self.__class__.__name__}")
        if not self._token_timeout and has_cache:
            logger.info(f"Haal token: NO TOKEN_TIMEOUT token_timeout={self._token_timeout}, delete token from cache")
            cache.delete(cache_key)
        token = cache.get(cache_key) if has_cache else None
        logger.debug(f"Haal token: token exists={not not token}, token_timeout={self._token_timeout}")

        if not token or force_cache:
            logger.info(f"Haal token: vernieuw token: key={cache_key}, token_timeout={self._token_timeout}")
            padden = self._base_url.strip("/").split("/") + self._token_api.strip("/").split("/") + [""]
            url = "/".join(padden)
            verwachte_status_code = [200, 201]

            try:
                if self._token_retrieve_method == "post":
                    token_response = requests.post(
                        url,
                        json={
                            "username": self._gebruikersnaam,
                            "password": self._wachtwoord,
                        },
                        headers={"user-agent": self._client_name if self._client_name else urllib3.util.SKIP_HEADER},
                    )
                else:
                    token_response = requests.get(
                        url,
                        auth=HTTPBasicAuth(self._gebruikersnaam, self._wachtwoord),
                        headers={
                            "user-agent": self._client_name if self._client_name else urllib3.util.SKIP_HEADER,
                        },
                    )
                    logger.debug(f"request.header: {token_response.request.headers['Authorization']}")
                token_response.raise_for_status()
                data = token_response.json()
            except requests.exceptions.JSONDecodeError:
                self.token_error = {
                    "error": {
                        "status_code": 500,
                        "bericht": "Service verwacht json response van token endpoint",
                        "verwachte_status_code": verwachte_status_code,
                    },
                }
                return
            except requests.exceptions.RequestException as e:
                self.token_error = {
                    "error": {
                        "status_code": 500,
                        "bericht": f"Token endpoint fout: {e}",
                        "verwachte_status_code": verwachte_status_code,
                    },
                }
                return

            if token_response.status_code in verwachte_status_code:
                token = data.get("token")
                logger.info(f"Haal token: vernieuwen geslaagd, reponse code={token_response.status_code}, key={cache_key}, token_timeout={self._token_timeout}")
                if self._token_timeout and has_cache:
                    cache.set(cache_key, token, self._token_timeout)
            else:
                self.token_error = {
                    "error": {
                        "status_code": token_response.status_code,
                        "bericht": data,
                        "verwachte_status_code": verwachte_status_code,
                    },
                }

        return token

    def get_cache_timeout(self, cache_timeout=None):
        return cache_timeout if cache_timeout is not None else self._cache_timeout

    def stel_url_samen(self, *pad):
        padden = self._api_path.strip("/").split("/") + list(pad) + [""]
        return "/".join(padden)

    def get_url(self, url):
        url_o = urlparse(url)
        if not url_o.scheme and not url_o.netloc:
            padden = [self._base_url, url.lstrip("/")]
            return "/".join(padden)
        if f"{url_o.scheme}://{url_o.netloc}" == self._base_url:
            return url
        raise BasisService.BasisUrlFout(f"url: {url}, basis_url: {self._base_url}")

    def get_auth_header(self):
        prefix = f"{self._auth_header_token_prefix} " if self._auth_header_token_prefix else ""
        return {self._auth_header_key: f"{prefix}{self.haal_token()}"}

    def get_headers(self, gebruik_token=None):
        headers = {"user-agent": self._client_name if self._client_name else urllib3.util.SKIP_HEADER}
        gebruik_token = gebruik_token if gebruik_token is not None else self._gebruik_token
        if gebruik_token:
            headers.update(self.get_auth_header())
        return headers

    def naar_json(self, response):
        if response.status_code == 204:
            return {}
        if response.text == "":
            return {}

        try:
            return response.json()
        except Exception as e:
            return {
                "error": {
                    "status_code": response.status_code,
                    "bericht": "Geen json",
                    "tekst": response.text,
                },
            }

    def fout(self, response=None, fout=None, verwachte_status_code=None):
        return {
            "error": {
                "status_code": response.status_code if not fout else 500,
                "bericht": self.naar_json(response) if not fout else "",
                "verwachte_status_code": verwachte_status_code,
            },
        }

    def do_request(
        self,
        url,
        method="get",
        data={},
        params={},
        raw_response=True,
        cache_timeout=None,
        verwachte_status_code=200,
        force_cache=False,
        stream=False,
        gebruik_token=None,
    ) -> Response | dict:
        action: Request = getattr(requests, method)
        self.token_error = None
        url = self.get_url(url)
        cache_timeout = self.get_cache_timeout(cache_timeout)
        response = None
        action_params: dict = {
            "url": url,
            "headers": self.get_headers(gebruik_token),
            "json": data,
            "params": params,
            "timeout": self._timeout,
            "stream": stream,
        }

        if self.token_error:
            return self.token_error

        cache_key = f"{url}?{urlencode(params)}"
        if force_cache and has_cache:
            cache.delete(cache_key)

        if cache_timeout and not stream and method == "get" and not force_cache and has_cache:
            response = cache.get(cache_key)
            logger.debug(f"get from cache: url={cache_key}, cache_timeout={cache_timeout}, response={response}")
            
            if (
                hasattr(response, "status_code")
                and getattr(response, "status_code") not in [200, 201]
            ):
                response = None
        logger.debug(f"cache_timeout={cache_timeout}, method={method}, force_cache={force_cache}")
        if not response:
            try:
                response: Response = action(**action_params)
            except Exception as e:
                logger.error(f"Exception e={e}, url={url}, cache_timeout={cache_timeout}, method={method}, force_cache={force_cache}")
                if has_cache:
                    cache.delete(cache_key)
                return self.fout(fout=e)

            if cache_timeout and not stream and method == "get" and hasattr(response, "status_code") and getattr(response, "status_code") in [200, 201] and has_cache:
                logger.info(
                    f"set cache for: url={cache_key}, cache_timeout={cache_timeout}, force_cache={force_cache}"
                )
                cache.set(cache_key, response, cache_timeout)

        if not hasattr(response, "status_code"):
            logger.error(f"Exception response={response}, url={url}, cache_timeout={cache_timeout}, method={method}, force_cache={force_cache}")

        logger.debug(f"Do request: status code={response.status_code}, url={url}, params={params}")
        if response.status_code == 401 and has_cache:
            logger.info(f"Do request: Unauthorized")
            cache_key = self.haal_token_cache_key()
            cache.delete(cache_key)

        if not isinstance(verwachte_status_code, (list|tuple)):
            verwachte_status_code = [verwachte_status_code]

        if response.status_code not in verwachte_status_code and not raw_response:
            return self.fout(
                response=response, 
                verwachte_status_code=verwachte_status_code,
            )
        
        if raw_response:
            return response
        return self.naar_json(response)
    
    def haal_data(self, url, params={}, raw_response=False, cache_timeout=0, force_cache=True):
        return self.do_request(
            url,
            params=params,
            raw_response=raw_response,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
        )
