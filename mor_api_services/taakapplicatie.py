import logging

from mor_api_services.basis import BasisService
logger = logging.getLogger(__name__)


class TaakapplicatieService(BasisService):
    _gebruik_token = True

    def melding_veranderd_notificatie_voor_applicatie(
        self, melding_url, notificatie_type
    ):
        url = self.stel_url_samen("melding")
        return self.do_request(
            url,
            params={
                "melding_url": melding_url,
                "notificatie_type": notificatie_type,
            },
            raw_response=False,
            cache_timeout=0,
        )

    def taak_aanmaken(self, data):
        url = self.stel_url_samen("taak")
        return self.do_request(url, method="post", data=data, verwachte_status_code=201, raw_response=False)

    def taak_verwijderen(self, taak_basis_url, gebruiker=None):
        return self.do_request(taak_basis_url, method="delete", params={"gebruiker": gebruiker}, verwachte_status_code=204, raw_response=False)
    
    def taak_status_aanpassen(self, taak_basis_url, data):
        url = f"{taak_basis_url}status-aanpassen/"
        return self.do_request(url, method="patch", data=data, raw_response=False)
    
    def taaktype_ophalen(self, taaktype_url):
        return self.do_request(
            taaktype_url, 
            raw_response=False,
            gebruik_token=False,
        )