import re

class FilterModule(object):
  ''' Converts CloudFormation Template Parameters to Stack Input mappings '''
  def filters(self):
    return {
        'stack_inputs': stack_inputs
    }

def stack_inputs(inputs, config):
  result = {}
  for key,value in inputs.items():
    try:
      result[key] = str(config.get(key) or value['Default'])
    except KeyError as e:
      raise KeyError("Missing variable for %s input.  Please define this variable or specify a 'Default' property for the input." % key)
  return result