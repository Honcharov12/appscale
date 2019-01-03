#!/usr/bin/env python

import time
import unittest

from google.appengine.datastore import document_pb

import models
import pb_adapter

class TestPBAdapter(unittest.TestCase):
  """ A set of test cases for pb_adapter module. """
  @classmethod
  def setUpClass(cls):
    """ Setup of Protocol Buffer Document object. """

    # Creation PB fields of all types
    pb_field_text = document_pb.Field()
    pb_field_text.set_name('helloWorld')
    pb_value = pb_field_text.mutable_value()
    pb_value.set_type(document_pb.FieldValue.TEXT)
    pb_value.set_language('en')
    pb_value.set_string_value('Hello World!')

    pb_field_html = document_pb.Field()
    pb_field_html.set_name('helloHTML')
    pb_value = pb_field_html.mutable_value()
    pb_value.set_type(document_pb.FieldValue.HTML)
    pb_value.set_language('en')
    pb_value.set_string_value('<p>Hello HTML!</p>')

    pb_field_atom = document_pb.Field()
    pb_field_atom.set_name('name')
    pb_value = pb_field_atom.mutable_value()
    pb_value.set_type(document_pb.FieldValue.ATOM)
    pb_value.set_language('en')
    pb_value.set_string_value('John')

    pb_field_number = document_pb.Field()
    pb_field_number.set_name('age')
    pb_value = pb_field_number.mutable_value()
    pb_value.set_type(document_pb.FieldValue.NUMBER)
    pb_value.set_language('ua')
    pb_value.set_string_value('24')

    pb_field_date = document_pb.Field()
    pb_field_date.set_name('secondAfterNY1970')
    pb_value = pb_field_date.mutable_value()
    pb_value.set_type(document_pb.FieldValue.DATE)
    pb_value.set_language('ua')
    # In milliseconds
    pb_value.set_string_value('1000')

    pb_field_geo = document_pb.Field()
    pb_field_geo.set_name('KhPI')
    pb_value = pb_field_geo.mutable_value()
    pb_value.set_type(document_pb.FieldValue.GEO)
    pb_value.set_language('ua')
    geo = pb_value.mutable_geo()
    geo.set_lat(50)
    geo.set_lng(36.25)

    pb_fields = [
      pb_field_text, pb_field_html, pb_field_atom,
      pb_field_number, pb_field_date, pb_field_geo
    ]

    # Creation PB document
    cls.pb_document = document_pb.Document()
    cls.pb_document.set_id('1q2w3e')
    cls.pb_document.set_language('en')

    # Filling document with fields
    for field in pb_fields:
      f = cls.pb_document.add_field()
      f.set_name(field.name())
      v = f.mutable_value()
      v.set_type(field.value().type())
      v.set_language(field.value().language())
      if field.value().type() != document_pb.FieldValue.GEO:
        v.set_string_value(field.value().string_value())
      else:
        geo = v.mutable_geo()
        lat = field.value().geo().lat()
        lng = field.value().geo().lng()
        geo.set_lat(lat)
        geo.set_lng(lng)

    # 1970-01-01T00:00:01
    expected_time = time.struct_time((1970, 1, 1, 0, 0, 1, 3, 1, 0))

    fields = [
      models.Field(name='helloWorld', language='en',
                   type=models.Field.Type.TEXT, value='Hello World!'),
      models.Field(name='helloHTML', language='en',
                   type=models.Field.Type.HTML, value='<p>Hello HTML!</p>'),
      models.Field(name='name', language='en',
                   type=models.Field.Type.ATOM, value='John'),
      models.Field(name='age', language='ua',
                   type=models.Field.Type.NUMBER, value=24),
      models.Field(name='secondAfterNY1970', language='ua',
                   type=models.Field.Type.DATE, value=expected_time),
      models.Field(name='KhPI', language='ua',
                   type=models.Field.Type.GEO, value=(50, 36.25))
    ]

    # Creation of models.Document object
    cls.document = models.Document(id='1q2w3e', language='en', fields=fields)

  def test_from_pb_document(self):
    """ Tests standard way of usage from_pb_document function. """

    # Getting unified Document object from Protocol Buffer document
    converted_document = pb_adapter.from_pb_document(self.pb_document)

    self.assertEquals(self.document, converted_document)

  def test_insertion_non_lang_field(self):
    """ Tests insertion to document field with no language. """

    # PB document creation
    pb_doc = document_pb.Document()
    pb_doc.set_id('qq')
    pb_doc.set_language('en')
    no_lang_field = pb_doc.add_field()

    # Creation field with no language
    no_lang_field.set_name('hello')
    pb_value = no_lang_field.mutable_value()
    pb_value.set_type(document_pb.FieldValue.TEXT)
    pb_value.set_string_value('Hello World!')

    field = [models.Field(name='hello', language='en',
                          type=models.Field.Type.TEXT, value='Hello World!')]
    document = models.Document(id='qq', language='en', fields=field)

    converted_document = pb_adapter.from_pb_document(pb_doc)

    self.assertEqual(document, converted_document)

  def test_to_pb_document(self):
    """ Tests standard way of usage to_pb_document function. """

    converted_document = pb_adapter.to_pb_document(self.document)

    self.assertEqual(self.pb_document, converted_document)
