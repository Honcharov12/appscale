"""" Module for handling operations with Protocol Buffer """

import calendar
from datetime import datetime
import logging

from constants import INDEX_LOCALE_FIELD
from search_exceptions import UnknownFieldException
from solr_interface import Field

from google.appengine.datastore.document_pb import FieldValue
from google.appengine.api.search import search_service_pb


def solr_to_gae(gae_results, solr_results, index):
  """ Converts SOLR results in to GAE compatible documents.

  Args:
    gae_results: A search_service_pb.SearchResponse.
    solr_results: A dictionary returned from SOLR on a search query.
    index: A Index that we are querying for.
  """
  gae_results.set_matched_count(
    len(solr_results['response']['docs']) +
    int(solr_results['response']['start'])
  )
  gae_results.mutable_status().set_code(search_service_pb.SearchServiceError.OK)
  for doc in solr_results['response']['docs']:
    new_result = gae_results.add_result()
    add_gae_doc(doc, new_result, index)


def add_gae_doc(doc, result, index):
  """ Add a new document to a query result.

  Args:
    doc: A dictionary of SOLR document attributes.
    result: A search_service_pb.SearchResult.
    index: Index we queried for.
  """
  new_doc = result.mutable_document()
  new_doc.set_id(doc['id'])
  if INDEX_LOCALE_FIELD in doc:
    new_doc.set_language(doc[INDEX_LOCALE_FIELD][0])
  for key in doc.keys():
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
    add_field_value(new_value, doc[key], field_type)


def add_field_value(new_value, value, ftype):
  """ Adds a value to a result field.

  Args:
    new_value: Value object to fill in.
    value: A str, the internal value to be converted.
    ftype: A str, the field type.
  """
  if ftype == Field.DATE:
    value = calendar.timegm(datetime.strptime(
      value[:-1], "%Y-%m-%dT%H:%M:%S").timetuple())
    new_value.set_string_value(str(int(value * 1000)))
    new_value.set_type(FieldValue.DATE)
  elif ftype == Field.TEXT:
    new_value.set_string_value(value)
    new_value.set_type(FieldValue.TEXT)
  elif ftype == Field.HTML:
    new_value.set_string_value(value)
    new_value.set_type(FieldValue.HTML)
  elif ftype == Field.ATOM:
    new_value.set_string_value(value)
    new_value.set_type(FieldValue.ATOM)
  elif ftype == Field.NUMBER:
    new_value.set_string_value(str(value))
    new_value.set_type(FieldValue.NUMBER)
  elif ftype == Field.GEO:
    geo = new_value.mutable_geo()
    lat, lng = value.split(',')
    geo.set_lat(float(lat))
    geo.set_lng(float(lng))
    new_value.set_type(FieldValue.GEO)
  elif ftype.startswith(Field.TEXT_):
    new_value.set_string_value(value)
    new_value.set_type(FieldValue.TEXT)
  else:
    raise UnknownFieldException("Default field {} not found!".format(ftype))
