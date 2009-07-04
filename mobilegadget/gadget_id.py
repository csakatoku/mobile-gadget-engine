class GadgetId():
    def __init__(self, uri, moduleId):
        self.uri = uri
        self.moduleId = int(moduleId)

    def getURI(self):
        return self.uri
	
    def getModuleId(self):
        return self.moduleId
	
    def getKey(self):
        return self.getURI()
