""" This module contains functions for converting data from Protocol Buffer
    data models to unified data models.
"""

import calendar
import time

from google.appengine.datastore import document_pb
from google.appengine.datastore.document_pb import FieldValue

import models

def _from_pb_field(pb_field, doc_lang):
  """ Converter from Protocol Buffer field.

  Args:
    pb_field: An object of Protocol Buffer Field class.
    doc_lang: Documents' language.
  Returns:
    An object of unified Field type.
  """

  field_name = pb_field.name()
  pb_value = pb_field.value()

  if pb_field.value().has_language():
    field_language = pb_value.language()
  else:
    field_language = doc_lang

  field_type, field_value = _get_type_and_value(pb_value)

  return models.Field(field_name, field_language, field_type, field_value)


def _get_type_and_value(pb_value):
  """ Gets type and value of FieldValue object.

  Args:
    pb_value: An object of Protocol Buffer FieldValue class.
  Returns:
    A tuple of Field type and Field value.
  """

  field_type = pb_value.type()

  if field_type == FieldValue.TEXT:
    result_value = pb_value.string_value()
    result_type = models.Field.Type.TEXT
  elif field_type == FieldValue.HTML:
    result_value = pb_value.string_value()
    result_type = models.Field.Type.HTML
  elif field_type == FieldValue.ATOM:
    result_value = pb_value.string_value()
    result_type = models.Field.Type.ATOM
  elif field_type == FieldValue.NUMBER:
    result_value = float(pb_value.string_value())
    result_type = models.Field.Type.NUMBER
  elif field_type == FieldValue.DATE:
    result_value = time.gmtime(int(pb_value.string_value()) // 1000)
    result_type = models.Field.Type.DATE
  elif field_type == FieldValue.GEO:
    geo = pb_value.geo()
    lat = float(geo.lat())
    lng = float(geo.lng())
    result_value = (lat, lng)
    result_type = models.Field.Type.GEO

  return (result_type, result_value)

def _fill_pb_field(pb_field, field):
  """ Fills Protocol Buffer field with values from unified Field class.

  Args:
    pb_field: An object of document_pb.Field class to fill in.
    field: An object of unified Field class.
  """

  converted = _to_pb_field(field)
  pb_field.set_name(converted.name())
  value = pb_field.mutable_value()
  value.set_type(converted.value().type())
  value.set_language(converted.value().language())
  if value.type() != FieldValue.GEO:
    value.set_string_value(converted.value().string_value())
  else:
    geo = value.mutable_geo()
    geo.set_lat(converted.value().geo().lat())
    geo.set_lng(converted.value().geo().lng())


def _to_pb_field(field):
  """ Converter to Protocol Buffer field.

  Args:
    field: An object of unified Field type.
  Returns:
    An object of Protocol Buffer Field class.
  """

  pb_field = document_pb.Field()

  pb_field.set_name(field.name)

  pb_value = pb_field.mutable_value()
  pb_value.set_language(field.language)

  field_type = field.type

  if field_type == models.Field.Type.TEXT:
    pb_value.set_string_value(field.value)
    pb_value.set_type(FieldValue.TEXT)
  elif field_type == models.Field.Type.HTML:
    pb_value.set_string_value(field.value)
    pb_value.set_type(FieldValue.HTML)
  elif field_type == models.Field.Type.ATOM:
    pb_value.set_string_value(field.value)
    pb_value.set_type(FieldValue.ATOM)
  elif field_type == models.Field.Type.NUMBER:
    pb_value.set_string_value(str(field.value))
    pb_value.set_type(FieldValue.NUMBER)
  elif field_type == models.Field.Type.DATE:
    value = calendar.timegm(field.value)
    pb_value.set_string_value(str(int(value * 1000)))
    pb_value.set_type(FieldValue.DATE)
  elif field_type == models.Field.Type.GEO:
    geo = pb_value.mutable_geo()
    lat, lng = field.value
    geo.set_lat(lat)
    geo.set_lng(lng)
    pb_value.set_type(FieldValue.GEO)

  return pb_field


def from_pb_document(pb_doc):
  """ Converter from Protocol Buffer document.

  Args:
    pb_doc: An object of Protocol Buffer Document class.
  Returns:
    An object of unified Document type.
  """

  doc_id = pb_doc.id()
  doc_language = pb_doc.language()
  doc_fields = []

  for field in pb_doc.field_list():
    doc_fields.append(_from_pb_field(field, doc_language))

  return models.Document(doc_id, doc_language, doc_fields)

def to_pb_document(doc):
  """ Converter to Protocol Buffer document.

  Args:
    doc:  An object of unified Document type.
  Returns:
    An object of Protocol Buffer Document class.
  """

  pb_doc = document_pb.Document()

  pb_doc.set_id(doc.id)
  pb_doc.set_language(doc.language)

  for field in doc.fields:
    pb_field = pb_doc.add_field()
    _fill_pb_field(pb_field, field)

  return pb_doc
