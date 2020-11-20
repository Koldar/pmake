class PMakeException(Exception):
    pass


class AssertionPMakeException(PMakeException):
    pass


class InvalidScenarioPMakeException(PMakeException):
    pass
