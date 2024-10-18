from django.utils.translation import gettext_lazy as _  # noqa: N812


class MorApiServicesException(Exception):
    bericht_type = _("onbekende fout")

    def __init__(self, bericht):
        self.bericht = bericht

    def __str__(self):
        return "%s: %s" % (self.bericht_type, self.bericht)