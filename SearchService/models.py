""" This module stores data models for Search API. """

import attr

@attr.s
class Field(object):
  """ Class representing basic field object. """
  class Type(object):
    """ Enum of possible field types. """
    TEXT = 'TEXT'
    HTML = 'HTML'
    ATOM = 'ATOM'
    DATE = 'DATE'
    NUMBER = 'NUMBER'
    GEO = 'GEO'

  name = attr.ib()
  language = attr.ib()
  type = attr.ib()
  value = attr.ib()


@attr.s
class Document(object):
  """ Class representing basic document object. """
  id = attr.ib()
  language = attr.ib()
  fields = attr.ib()
