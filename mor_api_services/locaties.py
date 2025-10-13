from mor_api_services.basis import BasisService


class LocatieService(BasisService):
    _default_error_message = "Er ging iets mis met het ophalen van data van de loactieservice"
    _cache_timeout = 5

    def buurten_met_wijken(self, force_cache=False, cache_timeout=0) -> list:
        url = self.stel_url_samen("buurt").strip("/")
        return self.do_request(url, params={
            "format": "legacy",
        }, raw_response=False, force_cache=force_cache, cache_timeout=cache_timeout)

    def woonplaatsen(self, force_cache=False, cache_timeout=0) -> dict:
        url = self.stel_url_samen("woonplaats").strip("/")
        return self.do_request(url, raw_response=False, force_cache=force_cache, cache_timeout=cache_timeout)
    
    def wijken(self, force_cache=False, cache_timeout=0) -> dict:
        url = self.stel_url_samen("wijk").strip("/")
        return self.do_request(url, raw_response=False, force_cache=force_cache, cache_timeout=cache_timeout)
    
    def buurten(self, force_cache=False, cache_timeout=0) -> dict:
        url = self.stel_url_samen("buurt").strip("/")
        return self.do_request(url, raw_response=False, force_cache=force_cache, cache_timeout=cache_timeout)