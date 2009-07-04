class GadgetFeatureRegistry():
    features = []
    core = []
    coreDone = False
	
    def __init__(self, featurePath):
        self.registerFeatures(featurePath)

    def registerFeatures(self, featurePath):
        if not featurePath:
            return
        coreDeps = []
        # don't use js
        #loader = JsFeatureLoader()
        #jsFeatures = loader.loadFeatures(featurePath, self)
        jsFeatures = []
        if not self.coreDone:
            for entry in jsFeatures:
                if entry.name[:len('core')].lower() == 'core':
                    coreDeps.append(entry.name)
                    self.core[entry.name] = entry.name

            # Make sure non-core features depend on core.
            for entry in jsFeatures:
                if entry.name[:len('core')] != 'core':
                    entry.deps = entry.deps + self.core
            self.coreDone = True

    def register(self, name, deps, feature):
        # Core entries must come first.
        entry = self.features.get(name)
        if entry == None:
            entry = GadgetFeatureRegistryEntry(name, deps, feature, this)
            if self.coreDone:
                entry.deps = array_merge(entry.deps, self.core)
            self.features[name] = entry
            self.validateFeatureGraph()
        return entry

    def validateFeatureGraph(self):
        # TODO: ensure that features form a DAG and that all deps are provided
        pass

    def getAllFeatures(self):
        return self.features

    def getIncludedFeatures(self, needed, resultsFound, resultsMissing):
        resultsFound = []
        resultsMissing = []
        if not len(needed):
            # Shortcut for gadgets that don't have any explicit dependencies.
            resultsFound = self.core
            return True

        for featureName in needed:
            entry = self.features.get(featureName)
            if not entry:
                resultsMissing.append(featureName)
            else:
                self.addEntryToSet(resultsFound, entry)
        return len(resultsMissing) == 0

    def addEntryToSet(self, results, entry):
        for dep in entry.deps:
            self.addEntryToSet(results, self.features[dep])
        results[entry.name] = entry.name

    def getEntry(self, name):
        return self.features[name]


# poor man's namespacing
class GadgetFeatureRegistryEntry():
    deps = []

    def __init__(self, name, deps, feature, registry):
        self.name = name
        if not deps:
            for dep in deps:
                entry = registry.getEntry(dep)
                self.deps[entry.name] = entry.name

        self.feature = feature

    def getName(self):
        return self.name

    def getDependencies(self):
        return self.deps

    def getFeature(self):
        return self.feature;
