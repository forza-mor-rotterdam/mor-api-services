import logging
from datetime import date, datetime, timedelta

from mor_api_services.basis import BasisService

logger = logging.getLogger(__name__)


class MORCoreService(BasisService):
    _gebruik_token = True

    def get_melding_lijst(self, query_string=""):
        url = self.stel_url_samen("melding")
        response = self.do_request(
            f"{url}?{query_string}",
            raw_response=True,
        )
        if not isinstance(response, dict):
            logger.info(
                f"Melding list: time={response.elapsed.total_seconds()}, size={len(response.content)}, qs={query_string}"
            )
            return self.naar_json(response)
        return response

    def get_melding(self, id, query_string=""):
        url = self.stel_url_samen("melding", str(id))
        return self.do_request(
            f"{url}?{query_string}",
            raw_response=False,
        )

    def get_volgende_melding(self, id, params):
        url = self.stel_url_samen("melding", str(id), "volgende")
        return self.do_request(
            url,
            params=params,
            raw_response=False,
        )

    def melding_gebeurtenis_toevoegen(
        self,
        id,
        bijlagen=[],
        omschrijving_intern=None,
        omschrijving_extern=None,
        gebruiker=None,
    ):
        data = {
            "bijlagen": bijlagen,
            "omschrijving_intern": omschrijving_intern,
            "omschrijving_extern": omschrijving_extern,
            "gebruiker": gebruiker,
        }
        response = self.do_request(
            f"{self._api_path}/melding/{id}/gebeurtenis-toevoegen/",
            method="post",
            data=data,
            
            raw_response=False,
        )
        return response

    def melding_status_aanpassen(
        self,
        id,
        status=None,
        resolutie=None,
        bijlagen=[],
        omschrijving_extern=None,
        omschrijving_intern=None,
        gebruiker=None,
    ):
        data = {
            "bijlagen": bijlagen,
            "omschrijving_extern": omschrijving_extern,
            "omschrijving_intern": omschrijving_intern,
            "gebruiker": gebruiker,
        }
        if status:
            data.update(
                {
                    "status": {
                        "naam": status,
                    },
                    "resolutie": resolutie,
                }
            )
        return self.do_request(
            (
                f"{self._api_path}/melding/{id}/status-aanpassen/"
                if status
                else f"{self._api_path}/melding/{id}/gebeurtenis-toevoegen/"
            ),
            method="patch" if status else "post",
            data=data,
            raw_response=False,
        )

    def melding_heropenen(
        self,
        id,
        bijlagen=[],
        omschrijving_intern=None,
        gebruiker=None,
    ):
        data = {
            "bijlagen": bijlagen,
            "omschrijving_intern": omschrijving_intern,
            "gebruiker": gebruiker,
        }
        data.update(
            {
                "status": {
                    "naam": "openstaand",
                },
                "resolutie": "niet_opgelost",
            }
        )
        return self.do_request(
            f"{self._api_path}/melding/{id}/heropenen/",
            method="patch",
            data=data,
            raw_response=False,
        )

    def melding_annuleren(
        self,
        id,
        bijlagen=[],
        omschrijving_intern=None,
        gebruiker=None,
    ):
        data = {
            "bijlagen": bijlagen,
            "omschrijving_intern": omschrijving_intern,
            "gebruiker": gebruiker,
        }
        data.update(
            {
                "status": {
                    "naam": "geannuleerd",
                },
                "resolutie": "opgelost",
            }
        )
        return self.do_request(
            f"{self._api_path}/melding/{id}/status-aanpassen/",
            method="patch",
            data=data,
            raw_response=False,
        )

    def melding_spoed_aanpassen(self, id, urgentie, omschrijving_intern, gebruiker):
        response = self.do_request(
            f"{self._api_path}/melding/{id}/urgentie-aanpassen/",
            method="patch",
            data={
                "urgentie": urgentie,
                "gebruiker": gebruiker,
                "omschrijving_intern": omschrijving_intern,
            },
            raw_response=False,
        )
        return response

    def locatie_aanpassen(
        self,
        id,
        omschrijving_intern=None,
        locatie={},
        gebruiker=None,
    ):
        data = {
            "gebruiker": gebruiker,
            "omschrijving_intern": omschrijving_intern,
            "locatie": locatie,
        }
        response = self.do_request(
            f"{self._api_path}/melding/{id}/locatie-aanmaken/",
            method="post",
            data=data,
            raw_response=False,
        )
        return response

    def taakapplicaties(self, use_cache=True):
        response = self.do_request(
            f"{self._api_path}/taakapplicatie/",
            cache_timeout=60 * 60 if use_cache else 0,
            raw_response=False,
        )
        return response

    def taak_aanmaken(
        self,
        melding_uuid,
        taakapplicatie_taaktype_url,
        titel,
        bericht=None,
        gebruiker=None,
        additionele_informatie={},
    ):
        data = {
            "taaktype": taakapplicatie_taaktype_url,
            "titel": titel,
            "bericht": bericht,
            "gebruiker": gebruiker,
            "additionele_informatie": additionele_informatie,
        }
        response = self.do_request(
            f"{self._api_path}/melding/{melding_uuid}/taakopdracht/",
            method="post",
            data=data,
            raw_response=False,
            verwachte_status_code=201,
        )
        return response

    def taak_status_aanpassen(
        self,
        taakopdracht_url,
        status,
        resolutie=None,
        omschrijving_intern=None,
        bijlagen=None,
        gebruiker=None,
    ):
        data = {
            "taakstatus": {
                "naam": status,
            },
            "resolutie": resolutie,
            "omschrijving_intern": omschrijving_intern,
            "bijlagen": bijlagen,
            "gebruiker": gebruiker,
        }
        response = self.do_request(
            f"{taakopdracht_url}status-aanpassen/",
            method="patch",
            data=data,
            raw_response=False,
        )
        return response

    def taakopdracht_verwijderen(
        self,
        taakopdracht_url,
        gebruiker=None,
    ):
        response = self.do_request(
            taakopdracht_url,
            params={"gebruiker": gebruiker},
            method="delete",
            raw_response=False,
        )
        return response

    def taakopdracht_notificatie(
        self,
        melding_url,
        taakopdracht_url,
        status=None,
        resolutie=None,
        omschrijving_intern=None,
        bijlagen=None,
        gebruiker=None,
        aangemaakt_op=None,
    ):
        data = {
            "resolutie": resolutie,
            "omschrijving_intern": omschrijving_intern,
            "bijlagen": bijlagen,
            "gebruiker": gebruiker,
            "aangemaakt_op": aangemaakt_op,
        }
        if status:
            data.update({
                "taakstatus": {
                    "naam": status,
                },
            })
        url = f"{melding_url}taakopdracht/{taakopdracht_url.strip('/').split('/')[-1]}/notificatie/"
        response = self.do_request(
            url,
            method="post",
            data=data,
            raw_response=False,
        )
        return response

    def taak_gebeurtenis_toevoegen(
        self,
        taakopdracht_url,
        gebeurtenis_type=None,
        omschrijving_intern=None,
        bijlagen=[],
        gebruiker=None,
    ):
        data = {
            "gebeurtenis_type": gebeurtenis_type,
            "omschrijving_intern": omschrijving_intern,
            "bijlagen": bijlagen,
            "gebruiker": gebruiker,
        }
        return self.do_request(
            f"{taakopdracht_url}gebeurtenis-toevoegen/", method="post", data=data
        )

    def signaal_aanmaken(self, data: {}):
        response = self.do_request(
            f"{self._api_path}/signaal/",
            method="post",
            data=data,
            verwachte_status_code=201,
            raw_response=False,
        )
        return response

    def onderwerp_alias_list(self, cache_timeout=60 * 60, force_cache=False):
        return self.do_request(
            f"{self._api_path}/onderwerp-alias/",
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            params={
                "limit": 200,
            },
            raw_response=False,
        )

    def get_gebruiker(self, gebruiker_email, cache_timeout=60 * 60 * 24, force_cache=False, raw_response=True):
        return self.do_request(
            f"{self._api_path}/gebruiker/{gebruiker_email}/",
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=raw_response,
        )

    def set_gebruiker(self, gebruiker):
        return self.do_request(
            f"{self._api_path}/gebruiker/", method="post", data=gebruiker
        )

    def melding_aantallen(self, datum=None, uur=None, days=1, force_cache=False):
        datum_datetime = (
            datetime.combine(datum, datetime.min.time())
            if isinstance(datum, date)
            else None
        )
        uur_int = uur if uur in range(0, 24) else None
        cache_timeout = 0
        params = {}
        if datum_datetime > datetime.now():
            return []
        if datum_datetime:
            td = timedelta(days=days)
            origineel_aangemaakt_gte = datum_datetime
            origineel_aangemaakt_lt = datum_datetime + td
            if uur_int is not None:
                origineel_aangemaakt_gte = origineel_aangemaakt_gte + timedelta(
                    hours=uur_int
                )
                origineel_aangemaakt_lt = origineel_aangemaakt_gte + timedelta(
                    hours=uur_int + 1
                )
            cache_timeout = (
                60 * 60 * 24 * 30 if origineel_aangemaakt_lt < datetime.now() else 60
            )
            params.update(
                {
                    "origineel_aangemaakt_gte": origineel_aangemaakt_gte.isoformat(),
                    "origineel_aangemaakt_lt": origineel_aangemaakt_lt.isoformat(),
                }
            )
        return self.do_request(
            f"{self._api_path}/melding/aantallen/",
            params=params,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )

    def signaal_aantallen(self, datum=None, uur=None, days=1, force_cache=False):
        datum_datetime = (
            datetime.combine(datum, datetime.min.time())
            if isinstance(datum, date)
            else None
        )
        uur_int = uur if uur in range(0, 24) else None
        cache_timeout = 0
        params = {}
        if datum_datetime > datetime.now():
            return []
        if datum_datetime:
            td = timedelta(days=days)
            origineel_aangemaakt_gte = datum_datetime
            origineel_aangemaakt_lt = datum_datetime + td
            if uur_int is not None:
                origineel_aangemaakt_gte = origineel_aangemaakt_gte + timedelta(
                    hours=uur_int
                )
                origineel_aangemaakt_lt = origineel_aangemaakt_gte + timedelta(
                    hours=uur_int + 1
                )
            cache_timeout = (
                60 * 60 * 24 * 30 if origineel_aangemaakt_lt < datetime.now() else 60
            )
            params.update(
                {
                    "origineel_aangemaakt_gte": origineel_aangemaakt_gte.isoformat(),
                    "origineel_aangemaakt_lt": origineel_aangemaakt_lt.isoformat(),
                }
            )
        return self.do_request(
            f"{self._api_path}/signaal/aantallen/",
            params=params,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )

    def status_veranderingen(self, datum=None, uur=None, days=1, force_cache=False):
        datum_datetime = (
            datetime.combine(datum, datetime.min.time())
            if isinstance(datum, date)
            else None
        )
        uur_int = uur if uur in range(0, 24) else None
        cache_timeout = 0
        params = {}
        if datum_datetime > datetime.now():
            return []
        if datum_datetime:
            td = timedelta(days=days)
            aangemaakt_op_gte = datum_datetime
            aangemaakt_op_lt = datum_datetime + td
            if uur_int is not None:
                aangemaakt_op_gte = aangemaakt_op_gte + timedelta(hours=uur_int)
                aangemaakt_op_lt = aangemaakt_op_gte + timedelta(hours=uur_int + 1)
            cache_timeout = (
                60 * 60 * 24 * 30 if aangemaakt_op_lt < datetime.now() else 60
            )
            params.update(
                {
                    "aangemaakt_op_gte": aangemaakt_op_gte.isoformat(),
                    "aangemaakt_op_lt": aangemaakt_op_lt.isoformat(),
                }
            )
        return self.do_request(
            f"{self._api_path}/status/veranderingen/",
            params=params,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )

    def afgehandelde_meldingen(self, datum=None, uur=None, days=1, force_cache=False):
        datum_datetime = (
            datetime.combine(datum, datetime.min.time())
            if isinstance(datum, date)
            else None
        )
        uur_int = uur if uur in range(0, 24) else None
        cache_timeout = 0
        params = {}
        if datum_datetime > datetime.now():
            return []
        if datum_datetime:
            td = timedelta(days=days)
            aangemaakt_op_gte = datum_datetime
            aangemaakt_op_lt = datum_datetime + td
            if uur_int is not None:
                aangemaakt_op_gte = aangemaakt_op_gte + timedelta(hours=uur_int)
                aangemaakt_op_lt = aangemaakt_op_gte + timedelta(hours=uur_int + 1)
            cache_timeout = (
                60 * 60 * 24 * 30 if aangemaakt_op_lt < datetime.now() else 60
            )
            params.update(
                {
                    "aangemaakt_op_gte": aangemaakt_op_gte.isoformat(),
                    "aangemaakt_op_lt": aangemaakt_op_lt.isoformat(),
                }
            )
        return self.do_request(
            f"{self._api_path}/status/afgehandeld/",
            params=params,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )

    def taaktype_aantallen_per_melding(
        self, datum=None, uur=None, days=1, force_cache=False
    ):
        datum_datetime = (
            datetime.combine(datum, datetime.min.time())
            if isinstance(datum, date)
            else None
        )
        uur_int = uur if uur in range(0, 24) else None
        cache_timeout = 0
        params = {}
        if datum_datetime > datetime.now():
            return []
        if datum_datetime:
            td = timedelta(days=days)
            melding_afgesloten_op_gte = datum_datetime
            melding_afgesloten_op_lt = datum_datetime + td
            if uur_int is not None:
                melding_afgesloten_op_gte = melding_afgesloten_op_gte + timedelta(
                    hours=uur_int
                )
                melding_afgesloten_op_lt = melding_afgesloten_op_gte + timedelta(
                    hours=uur_int + 1
                )
            cache_timeout = (
                60 * 60 * 24 * 30 if melding_afgesloten_op_lt < datetime.now() else 60
            )
            params.update(
                {
                    "melding_afgesloten_op_gte": melding_afgesloten_op_gte.isoformat(),
                    "melding_afgesloten_op_lt": melding_afgesloten_op_lt.isoformat(),
                }
            )
        return self.do_request(
            f"{self._api_path}/taakopdracht/taaktype-aantallen-per-melding/",
            params=params,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )

    def taakopdracht_doorlooptijden(
        self, datum=None, uur=None, days=1, force_cache=False
    ):
        datum_datetime = (
            datetime.combine(datum, datetime.min.time())
            if isinstance(datum, date)
            else None
        )
        uur_int = uur if uur in range(0, 24) else None
        cache_timeout = 0
        params = {}
        if datum_datetime > datetime.now():
            return []
        if datum_datetime:
            td = timedelta(days=days)
            afgesloten_op_gte = datum_datetime
            afgesloten_op_lt = datum_datetime + td
            if uur_int is not None:
                afgesloten_op_gte = afgesloten_op_gte + timedelta(hours=uur_int)
                afgesloten_op_lt = afgesloten_op_gte + timedelta(hours=uur_int + 1)
            cache_timeout = (
                60 * 60 * 24 * 30 if afgesloten_op_lt < datetime.now() else 60
            )
            params.update(
                {
                    "afgesloten_op_gte": afgesloten_op_gte.isoformat(),
                    "afgesloten_op_lt": afgesloten_op_lt.isoformat(),
                }
            )
        return self.do_request(
            f"{self._api_path}/taakopdracht/taakopdracht-doorlooptijden/",
            params=params,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )

    def nieuwe_taakopdrachten(self, datum=None, uur=None, days=1, force_cache=False):
        datum_datetime = (
            datetime.combine(datum, datetime.min.time())
            if isinstance(datum, date)
            else None
        )
        uur_int = uur if uur in range(0, 24) else None
        cache_timeout = 0
        params = {}
        if datum_datetime > datetime.now():
            return []
        if datum_datetime:
            td = timedelta(days=days)
            aangemaakt_op_gte = datum_datetime
            aangemaakt_op_lt = datum_datetime + td
            if uur_int is not None:
                aangemaakt_op_gte = aangemaakt_op_gte + timedelta(hours=uur_int)
                aangemaakt_op_lt = aangemaakt_op_gte + timedelta(hours=uur_int + 1)
            cache_timeout = (
                60 * 60 * 24 * 30 if aangemaakt_op_lt < datetime.now() else 60
            )
            params.update(
                {
                    "aangemaakt_op_gte": aangemaakt_op_gte.isoformat(),
                    "aangemaakt_op_lt": aangemaakt_op_lt.isoformat(),
                }
            )
        return self.do_request(
            f"{self._api_path}/taakopdracht/nieuwe-taakopdrachten/",
            params=params,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )

    def tijdsvak_data_halen(self, url, params):
        return self.do_request(
            url,
            params=params,
            raw_response=False,
        )
    
    def bestand_halen(self, url):
        return self.do_request(
            url,
            stream=True,
        )

    def buurten_met_wijken(self, cache_timeout=0):
        url = self.stel_url_samen("locatie", "buurten")
        return self.do_request(
            url,
            cache_timeout=cache_timeout,
            raw_response=False,
        )
    
    def specificatie_lijst(self, force_cache=False, cache_timeout=0):
        url = self.stel_url_samen("specificatie")
        return self.do_request(
            url,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )
    
    def specificatie_detail(self, specificatie_uuid, force_cache=False, cache_timeout=0):
        url = self.stel_url_samen("specificatie", specificatie_uuid)
        return self.do_request(
            url,
            cache_timeout=cache_timeout,
            force_cache=force_cache,
            raw_response=False,
        )
    
    def specificatie_aanmaken(self, naam:str):
        url = self.stel_url_samen("specificatie")
        return self.do_request(
            url,
            data={
                "naam": naam
            },
            method="post",
            raw_response=False,
        )
    
    def specificatie_naam_aanpassen(self, specificatie_uuid, naam:str):
        url = self.stel_url_samen("specificatie", specificatie_uuid)
        return self.do_request(
            url,
            data={
                "naam": naam
            },
            method="patch",
            raw_response=False,
        )
    
    def specificatie_verwijderen(self, specificatie_uuid):
        url = self.stel_url_samen("specificatie", specificatie_uuid)
        return self.do_request(
            url,
            method="delete",
            raw_response=False,
        )