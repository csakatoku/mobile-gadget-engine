import logging

class Substitutions():
    types = {'MESSAGE': 'MSG',
             'BIDI': 'BIDI',
             'USER_PREF': 'UP',
             'MODULE': 'MODULE',
             }

    substitutions = {}
	
    def __init__(self):
        for type in self.types.keys():
            self.substitutions[type] = {}
            
    def addSubstitution(self, type, key, value):
        self.substitutions[type]["__%s_%s__" % (self.types[type], key)] = value
	
    def addSubstitutions(self, type, array):
        for key, value in array.items():
            self.addSubstitution(type, key, value)
	
    def substitute(self, input):
        for type in self.types.keys():
            input = self.substituteType(type, input)
        return input
	
    def substituteType(self, type, input):
        ret = input
        for key,val in self.substitutions[type].items():
            ret = ret.replace(key, str(val))
        return ret
