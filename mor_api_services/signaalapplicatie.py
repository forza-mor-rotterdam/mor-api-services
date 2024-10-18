import logging
from mor_api_services.basis import BasisService
logger = logging.getLogger(__name__)


class SignaalapplicatieService(BasisService):
    _gebruik_token = True

    def notificatie_melding_afgesloten(self, signaal_uri):
        melding_afgesloten_url = f"{signaal_uri}melding-afgesloten/"
        response = self.do_request(melding_afgesloten_url)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                logger.warning(
                    f"Melding is waarschijnlijk goed afgesloten, maar response is niet van het type json: url='{melding_afgesloten_url}', response tekst={response.text}, error={e}"
                )

        if response.status_code == 404:
            logger.warning(
                f"Melding kon niet worden afgesloten, vermoedelijk ondersteund de applicatie 'melding afgesloten' niet. url='{melding_afgesloten_url}', status code={response.status_code}, response tekst={response.text}"
            )

        logger.error(
            f"Melding kon niet worden afgesloten. '{melding_afgesloten_url}', status code: {response.status_code}, response tekst={response.text}"
        )