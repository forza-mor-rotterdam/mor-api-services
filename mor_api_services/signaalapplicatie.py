import logging
from mor_api_services.basis import BasisService
logger = logging.getLogger(__name__)


class SignaalapplicatieService(BasisService):
    _gebruik_token = True

    def notificatie_melding_afgesloten(self, signaal_uri):
        url = f"{signaal_uri}melding-afgesloten/"
        return self.do_request(url, method="post", data={}, cache_timeout=0)