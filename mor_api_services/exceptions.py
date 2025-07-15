class MorApiServicesException(Exception):
    bericht_type = "onbekende fout"

    def __init__(self, bericht):
        self.bericht = bericht

    def __str__(self):
        return "%s: %s" % (self.bericht_type, self.bericht)