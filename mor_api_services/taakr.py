import logging

from mor_api_services.basis import BasisService

logger = logging.getLogger(__name__)


class TaakRService(BasisService):
    _cache_timeout = 60 * 60

    def get_afdelingen(self, force_cache=False, taakapplicatie_basis_urls=[]) -> list:
        alle_afdelingen = []
        next_page = f"{self._base_url}/api/v1/afdeling/"
        while next_page:
            response = self.do_request(
                next_page,
                params={
                    "taakapplicatie_basis_url": taakapplicatie_basis_urls,
                },
                raw_response=False,
                force_cache=force_cache,
            )
            current_afdelingen = response.get("results", [])
            alle_afdelingen.extend(current_afdelingen)
            next_page = response.get("next")

        return alle_afdelingen

    def get_afdeling(self, afdeling_uuid):
        url = f"{self._base_url}/api/v1/afdeling/{afdeling_uuid}"
        afdeling = self.do_request(
            url,
            raw_response=False,
        )

        return afdeling

    def get_afdeling_by_url(self, afdeling_url, force_cache=False):
        afdeling = self.do_request(
            afdeling_url,
            raw_response=False,
            force_cache=force_cache
        )

        return afdeling

    def get_taaktypes(self, params={}, force_cache=False) -> list:
        alle_taaktypes = []
        next_page = f"{self._base_url}/api/v1/taaktype/"
        while next_page:
            response = self.do_request(
                next_page,
                params=params,
                force_cache=force_cache,
                raw_response=False,
            )
            current_taaktypes = response.get("results", [])
            alle_taaktypes.extend(current_taaktypes)
            next_page = response.get("next")
        return alle_taaktypes

    def get_taaktype(self, taaktype_uuid, force_cache=False):
        url = f"{self._base_url}/api/v1/taaktype/{taaktype_uuid}"
        taaktype = self.do_request(
            url,
            raw_response=False,
            force_cache=force_cache,
        )

        return taaktype

    def get_taaktypes_with_afdelingen(self, melding, force_cache=False, context_taaktypes=[]):
        alle_taaktypes = self.get_taaktypes(force_cache=force_cache)

        # Check rol/context if taaktype is selected and check if the taaktype is active
        taaktypes_categorized = [
            tt
            for tt in alle_taaktypes
            if tt.get("_links", {}).get("taakapplicatie_taaktype_url")
            in context_taaktypes
            and tt.get("actief", False)
        ]

        # Check for which taaktypes a taak has already been created
        gebruikte_taaktypes = [
            *set(
                list(
                    to.get("taaktype")
                    for to in melding.get("taakopdrachten_voor_melding", [])
                    if not to.get("resolutie")
                )
            )
        ]

        taaktypes_with_afdelingen = []
        for tt in taaktypes_categorized:
            if tt.get("taakapplicatie_taaktype_url") not in gebruikte_taaktypes:
                if tt.get("afdelingen"):
                    for afdeling_url in tt.get("afdelingen"):
                        taaktypes_with_afdelingen.append(
                            {
                                "taaktype": tt,
                                "afdeling": self.get_afdeling_by_url(
                                    afdeling_url, force_cache=force_cache
                                ),
                            }
                        )
                else:
                    taaktypes_with_afdelingen.append(
                        {"taaktype": tt, "afdeling": {}}  # empty afdeling object
                    )

        return taaktypes_with_afdelingen

    def vernieuw_taaktypes(self, taaktype_url):
        url = f"{self._base_url}/api/v1/taaktype/vernieuw/"
        taaktypes = self.do_request(
            url,
            params={"taakapplicatie_taaktype_url": taaktype_url},
            cache_timeout=0,
            raw_response=False,
        )
        return taaktypes

    def get_taaktype_by_url(self, taaktype_url, force_cache=False):
        taaktype = self.do_request(
            taaktype_url,
            raw_response=False,
            force_cache=force_cache,
        )

        return taaktype

    def get_taakapplicatie_taaktype_url(self, taaktype_url):
        if taaktype := self.get_taaktype_by_url(taaktype_url):
            return taaktype.get("_links").get("taakapplicatie_taaktype_url")

    def get_niet_actieve_taaktypes(self, melding, force_cache=False):
        alle_taaktypes = self.get_taaktypes(force_cache=force_cache)
        gebruikte_taaktypes = [
            *set(
                list(
                    to.get("taaktype")
                    for to in melding.get("taakopdrachten_voor_melding", [])
                    if not to.get("resolutie")
                )
            )
        ]
        taaktypes = [
            tt
            for tt in alle_taaktypes
            if tt.get("taakapplicatie_taaktype_url") not in gebruikte_taaktypes
        ]
        return taaktypes

    def categorize_taaktypes(self, melding, taaktypes, context_taaktypes=[]):
        taaktypes_categorized = [
            [
                tt.get("_links", {}).get("taakapplicatie_taaktype_url"),
                f"{tt.get('omschrijving')}",
            ]
            for tt in taaktypes
            if tt.get("_links", {}).get("taakapplicatie_taaktype_url")
            in context_taaktypes
            and tt.get("actief", False)
        ]
        gebruikte_taaktypes = [
            *set(
                list(
                    to.get("taaktype")
                    for to in melding.get("taakopdrachten_voor_melding", [])
                    if not to.get("resolutie")
                )
            )
        ]
        taaktypes_categorized = [
            tt for tt in taaktypes_categorized if tt[0] not in gebruikte_taaktypes
        ]
        return taaktypes_categorized
