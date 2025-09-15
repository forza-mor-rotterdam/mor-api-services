import logging

from mor_api_services.basis import BasisService

logger = logging.getLogger(__name__)


class OnderwerpenService(BasisService):
    _message = True
    _default_error_message = "Er ging iets mis met het ophalen van data van Onderwerpen"
    _cache_timeout = 60 * 60 * 24

    def get_onderwerp(self, url, force_cache=False) -> dict:
        return self.do_request(url, raw_response=False, force_cache=force_cache)

    def get_onderwerpen(self, force_cache=False):
        all_onderwerpen = []
        next_page = f"{self._base_url}/api/v1/category/"
        while next_page:
            response = self.do_request(
                next_page,
                params={
                    "limit": 25,
                },
                raw_response=False,
                force_cache=force_cache,
            )
            current_onderwerpen = response.get("results", [])
            all_onderwerpen.extend(current_onderwerpen)
            next_page = response.get("_links", {}).get("next")
        return all_onderwerpen

    def get_groep(self, groep_uuid, force_cache=False):
        url = f"{self._base_url}/api/v1/group/{groep_uuid}"
        onderwerp_groep = self.do_request(
            url,
            raw_response=False,
            force_cache=force_cache,
        )
        if not onderwerp_groep.get("name"):
            logger.error(
                f"Onderwerp_groep not found: {onderwerp_groep}. Groep url: {url}."
            )
        return onderwerp_groep
