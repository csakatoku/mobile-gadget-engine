class UserPrefs():
    prefs = {}

    def __init__(self, prefs):
        self.prefs = prefs
	
    def getPrefs(self):
        return self.prefs
	
    def getPref(self, name):
        return self.prefs.get(name, None)
