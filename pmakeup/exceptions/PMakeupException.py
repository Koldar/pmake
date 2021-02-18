class PMakeupException(Exception):
    pass


class AssertionPMakeupException(PMakeupException):
    pass


class InvalidScenarioPMakeupException(PMakeupException):
    pass
