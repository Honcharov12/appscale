""" Top level exceptions for search from AppScale. """

class SearchException(Exception):
  """ Top level exception for search. """
  pass


class InternalError(SearchException):
  """ Internal error exception. """
  pass


class NotConfiguredError(SearchException):
  """ Search is not configured. """
  pass


class UnknownFieldException(SearchException):
  """ Field is not defined """
  pass


class UnknownFieldTypeException(SearchException):
  """ Field type is not defined """
  pass
