import logging
from mor_api_services.basis import BasisService
logger = logging.getLogger(__name__)


class SignaalapplicatieService(BasisService):
    _gebruik_token = True

    def notificatie_melding_afgesloten(self, signaal_uri, url_postfix="melding-afgesloten/", data={}):
        url = f"{signaal_uri}{url_postfix}"
        return self.do_request(
            url, 
            method="post", 
            data=data, 
            cache_timeout=0, 
            raw_response=False,
            verwachte_status_code=[200, 201],
        )