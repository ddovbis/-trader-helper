class MkDataFields(object):
    TIMESTAMP = "Timestamp"
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    VOLUME = "Volume"

    @staticmethod
    def get_all():
        """
        :return: all values of parameters of the class for non-callable, and non-staticmethod parameters
        """
        return [
            attr for name, attr in MkDataFields.__dict__.items()
            if not name.startswith("__")
               and not callable(attr)
               and not type(attr) is staticmethod
        ]
