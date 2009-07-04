# Locale class doesn't exist in php, so to allow the code base to be closer to the java one, were faking one
class Locale():
    def __init__(self, language, country):
        self.language = language
        self.country = country

    def equals(self, obj):
        if not isinstance(obj, Locale):
            return False;
        return obj.language == self.language and obj.country == self.country
	
    def getLanguage(self):
        return self.language
	
    def getCountry(self):
        return self.country
