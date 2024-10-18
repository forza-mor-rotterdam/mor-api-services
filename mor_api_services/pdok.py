import copy
import logging
import math

from mor_api_services.basis import BasisService
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PDOKService(BasisService):
    _cache_timeout = 60 * 60 * 24 * 7

    def __init__(self, gemeentecode, *args, **kwargs: dict):
        self._gemeentecode = gemeentecode
        super().__init__(*args, **kwargs)

    def get_buurten_middels_gemeentecode(
        self, gemeentecode=None, force_cache=False
    ) -> dict:
        url = self.stel_url_samen("free").strip("/")
        gemeentecode = gemeentecode if not self._gemeentecode else self._gemeentecode
        results = []
        start = 0
        rows = 10
        params = {
            "start": start,
            "rows": rows,
            "fq": [
                f"gemeentecode:{gemeentecode}",
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
        cache.set(
            settings.WIJKEN_EN_BUURTEN_CACHE_KEY,
            results_grouped,
        )
        return results_grouped

    def get_wijken_middels_gemeentecode(
        self, gemeentecode=None, force_cache=False
    ) -> dict:
        url = self.stel_url_samen("free").strip("/")
        gemeentecode = gemeentecode if not self._gemeentecode else self._gemeentecode
        results = []
        start = 0
        rows = 10
        params = {
            "start": start,
            "rows": rows,
            "fq": [
                f"gemeentecode:{gemeentecode}",
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

    def get_buurten_middels_wijkcodes(self, wijkcodes, gemeentecode=None, force_cache=False) -> list:
        all_data = self.get_buurten_middels_gemeentecode(gemeentecode=gemeentecode, force_cache=force_cache)
        buurtnamen = []
        for wijk in all_data.get("wijken", []):
            if wijk["wijkcode"] in wijkcodes:
                buurtnamen.extend(
                    [buurt["buurtnaam"] for buurt in wijk.get("buurten", [])]
                )
        return buurtnamen
