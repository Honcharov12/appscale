class Summarizer(object):
  def get_value_to_add(self, request):
    raise NotImplementedError()


class AttrValue(Summarizer):
  def __init__(self, field_name):
    super(AttrValue, self).__init__()
    self._field_name = field_name

  def get_value_to_add(self, request):
    return getattr(request, self._field_name)
