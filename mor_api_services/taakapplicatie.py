import logging

from mor_api_services.basis import BasisService
logger = logging.getLogger(__name__)


class TaakapplicatieService(BasisService):
    _gebruik_token = True

    def melding_veranderd_notificatie_voor_applicatie(
        self, melding_url, notificatie_type
    ):
        return self.do_request(
            "/api/v1/melding/",
            params={
                "melding_url": melding_url,
                "notificatie_type": notificatie_type,
            },
        )

    def taak_aanmaken(self, data):
        return self.do_request("/api/v1/taak/", method="post", data=data)

    def taak_verwijderen(self, url, gebruiker=None):
        return self.do_request(url, method="delete", params={"gebruiker": gebruiker})
    
    def taak_status_aanpassen(self, url, data):
        return self.do_request(url, method="patch", data=data)