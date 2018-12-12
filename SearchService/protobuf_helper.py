"""" Module for handling operations with Protocol Buffer """

import calendar
from datetime import datetime

from constants import INDEX_LOCALE_FIELD
from search_exceptions import UnknownFieldException
from solr_interface import Field

from google.appengine.datastore.document_pb import FieldValue


def fill_protobuf_doc(gae_doc, solr_doc, index):
  """ Fill new document from a query result.

  Args:
    solr_doc: A dictionary of SOLR document attributes.
    gae_doc: A search_service_pb.SearchResult.
    index: Index we queried for.
  Raises:
    UnknownFieldException: If there are no some fields in indexes schema.
  """
  new_doc = gae_doc.mutable_document()
  new_doc.set_id(solr_doc['id'])
  if INDEX_LOCALE_FIELD in solr_doc:
    new_doc.set_language(solr_doc[INDEX_LOCALE_FIELD][0])
  for key in solr_doc.keys():
    if not key.startswith(index.name):
      continue
    field_name = key.split("{}_".format(index.name), 1)[1]
    new_field = new_doc.add_field()
    new_field.set_name(field_name)
    new_value = new_field.mutable_value()
    field_type = ""
    for field in index.schema.fields:
      if field['name'] == "{}_{}".format(index.name, field_name):
        field_type = field['type']
    if field_type == "":
      raise UnknownFieldException('Unable to find type for {}_{}'.format(index.name, field_name))
    fill_protobuf_field(new_value, solr_doc[key], field_type)


def fill_protobuf_field(gae_field, solr_field, ftype):
  """ Fills search_service_pb.SearchResult field with a value.

  Args:
    gae_field: A search_service_pb.SearchResult field.
    solr_field: Field value in SOLR.
    ftype: A str, the field type.
  Raises:
    UnknownFieldException: If default field is not found.
  """
  if ftype == Field.DATE:
    value = calendar.timegm(datetime.strptime(
      solr_field[:-1], "%Y-%m-%dT%H:%M:%S").timetuple())
    gae_field.set_string_value(str(int(value * 1000)))
    gae_field.set_type(FieldValue.DATE)
  elif ftype == Field.TEXT:
    gae_field.set_string_value(solr_field)
    gae_field.set_type(FieldValue.TEXT)
  elif ftype == Field.HTML:
    gae_field.set_string_value(solr_field)
    gae_field.set_type(FieldValue.HTML)
  elif ftype == Field.ATOM:
    gae_field.set_string_value(solr_field)
    gae_field.set_type(FieldValue.ATOM)
  elif ftype == Field.NUMBER:
    gae_field.set_string_value(str(solr_field))
    gae_field.set_type(FieldValue.NUMBER)
  elif ftype == Field.GEO:
    geo = gae_field.mutable_geo()
    lat, lng = solr_field.split(',')
    geo.set_lat(float(lat))
    geo.set_lng(float(lng))
    gae_field.set_type(FieldValue.GEO)
  elif ftype.startswith(Field.TEXT_):
    gae_field.set_string_value(solr_field)
    gae_field.set_type(FieldValue.TEXT)
  else:
    raise UnknownFieldException("Default field {} not found!".format(ftype))
