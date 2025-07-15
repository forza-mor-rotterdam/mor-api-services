import copy
import logging
import math

from mor_api_services.basis import BasisService

has_cache = True
try:
    from django.conf import settings
    from django.core.cache import cache
except Exception:
    has_cache = False

logger = logging.getLogger(__name__)


class PDOKService(BasisService):
    _base_url = "https://api.pdok.nl/bzk/locatieserver/search/v3_1"
    _cache_timeout = 60 * 60 * 24 * 7

    def __init__(self, gemeentecode, *args, **kwargs: dict):
        self._gemeentecode = gemeentecode
        super().__init__(*args, **kwargs)

    def get_buurten_middels_gemeentecode(
        self, force_cache
    ) -> dict:
        url = f"{self._base_url}/free"
        results = []
        start = 0
        rows = 10
        params = {
            "start": start,
            "rows": rows,
            "fq": [
                f"gemeentecode:{self._gemeentecode}",
                "bron:CBS",
                "type:buurt",
            ],
            "wt": "json",
            "fl": [
                "woonplaatscode",
                "wijkcode",
                "wijknaam",
                "buurtcode",
                "buurtnaam",
                "centroide_ll",
            ],
        }
        response = self.do_request(
            url, params=params, raw_response=False, force_cache=force_cache
        ).get("response", {})
        result_count = response.get("numFound", 0)
        results.extend(response.get("docs", []))
        loop_range = range(
            (start + 1) * rows, math.ceil(result_count / rows) * rows, rows
        )
        for i in loop_range:
            params_clone = copy.deepcopy(params)
            params_clone.update(
                {
                    "start": i,
                }
            )
            r = self.do_request(
                url,
                params=params_clone,
                raw_response=False,
                force_cache=force_cache,
            ).get("response", {})
            results.extend(r.get("docs", []))

        wijken = {r.get("wijkcode"): r for r in results}
        results_grouped = {
            "wijken": [
                {
                    "wijkcode": wijkcode,
                    "wijknaam": w.get("wijknaam"),
                    "buurten": [
                        {
                            "buurtnaam": b.get("buurtnaam"),
                            "buurtcode": b.get("buurtcode"),
                            "gps": b.get("centroide_ll"),
                        }
                        for b in results
                        if b.get("wijkcode") == wijkcode
                    ],
                }
                for wijkcode, w in wijken.items()
            ]
        }
        if has_cache:
            cache.set(
                settings.WIJKEN_EN_BUURTEN_CACHE_KEY,
                results_grouped,
                settings.MELDINGEN_TOKEN_TIMEOUT,
            )
        return results_grouped

    def get_wijken_middels_gemeentecode(
        self, force_cache=False
    ) -> dict:
        url = f"{self._base_url}/free"
        results = []
        start = 0
        rows = 10
        params = {
            "start": start,
            "rows": rows,
            "fq": [
                f"gemeentecode:{self._gemeentecode}",
                "bron:CBS",
                "type:wijk",
            ],
            "wt": "json",
            "fl": [
                "woonplaatscode",
                "wijkcode",
                "wijknaam",
                "centroide_ll",
            ],
        }
        response = self.do_request(
            url, params=params, raw_response=False, force_cache=force_cache
        ).get("response", {})
        result_count = response.get("numFound", 0)
        results.extend(response.get("docs", []))
        loop_range = range(
            (start + 1) * rows, math.ceil(result_count / rows) * rows, rows
        )
        for i in loop_range:
            params_clone = copy.deepcopy(params)
            params_clone.update(
                {
                    "start": i,
                }
            )
            r = self.do_request(
                url,
                params=params_clone,
                raw_response=False,
                force_cache=force_cache,
            ).get("response", {})
            results.extend(r.get("docs", []))
        return results

    def get_buurten_middels_wijkcodes(self, wijkcodes, force_cache=False) -> list:
        all_data = self.get_buurten_middels_gemeentecode(force_cache=force_cache)
        buurtnamen = []
        for wijk in all_data.get("wijken", []):
            if wijk["wijkcode"] in wijkcodes:
                buurtnamen.extend(
                    [buurt["buurtnaam"] for buurt in wijk.get("buurten", [])]
                )
        return buurtnamen
