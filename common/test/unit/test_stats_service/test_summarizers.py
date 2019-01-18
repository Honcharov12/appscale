import unittest

from appscale.common.service_stats import summarizers
from appscale.common.service_stats.stats_manager import (
  ServiceStats, DEFAULT_REQUEST_FIELDS
)


RequestInfo = ServiceStats.generate_request_model(DEFAULT_REQUEST_FIELDS)


class TestBuiltinSummarizers(unittest.TestCase):
  def test_attr_value(self):
    # Set requests with their latencies and response sizes
    req_a = RequestInfo()
    req_a.latency, req_a.response_size = 10, 250
    req_b = RequestInfo()
    req_b.latency, req_b.response_size = 5, 100
    req_c = RequestInfo()
    req_c.latency, req_c.response_size = 21, 1024

    # Set Summarizer for counting latencies
    get_latency_summarizer = summarizers.AttrValue("latency")

    s = 0
    s += get_latency_summarizer.get_value_to_add(req_a)
    self.assertEqual(s, 10)
    s += get_latency_summarizer.get_value_to_add(req_b)
    self.assertEqual(s, 15)
    s += get_latency_summarizer.get_value_to_add(req_c)
    self.assertEqual(s, 36)

    # Set Summarizer for counting response sizes
    get_response_size_summarizer = summarizers.AttrValue("response_size")

    s = 0
    s += get_response_size_summarizer.get_value_to_add(req_a)
    self.assertEqual(s, 250)
    s += get_response_size_summarizer.get_value_to_add(req_b)
    self.assertEqual(s, 350)
    s += get_response_size_summarizer.get_value_to_add(req_c)
    self.assertEqual(s, 1374)


class TestCustomSummarizer(unittest.TestCase):
  def setUp(self):
    # define class to test
    class DoubleResponseSize(summarizers.Summarizer):
      def get_value_to_add(self, request):
        return request.response_size * 2

    # create object of class DoubleResponseSize to test it
    self.double_response_size_summarizer = DoubleResponseSize()

  def test_custom_summarizer(self):
    # Set requests with their response sizes
    req_a = RequestInfo()
    req_a.response_size = 250
    req_b = RequestInfo()
    req_b.response_size = 100
    req_c = RequestInfo()
    req_c.response_size = 1024

    s = 0
    s += self.double_response_size_summarizer.get_value_to_add(req_a)
    self.assertEqual(s, 500)
    s += self.double_response_size_summarizer.get_value_to_add(req_b)
    self.assertEqual(s, 700)
    s += self.double_response_size_summarizer.get_value_to_add(req_c)
    self.assertEqual(s, 2748)
