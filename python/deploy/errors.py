__author__ = 'brhoades'


class Error(Exception):
    """
    Base class for exceptions in this module.
    """


class ParserError(Error):
    """
    Raises an error if an undefined file format is passed to a function
    attempting to parse it.
    """
    pass


class OperationError(Error):
    """
    Raises an error if an operation is attempted for which there is no process.
    """
    pass