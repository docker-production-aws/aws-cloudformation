import json

class FilterModule(object):
  ''' Returns dictionary of items with keyed overrides that override properties with a matching selector'''
  def filters(self):
    return {
        'compact': compact
    }

def compact(obj, separators=(',',':')):
  return json.dumps(obj, separators=separators)