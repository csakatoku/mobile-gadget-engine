import urllib
from gadget_spec_parser import *
from remote_content_request import *
from gadget_feature_registry import *
import logging

"""
* This isn't a multi threaded java envirioment, so we do things a bit more
* straightforward with context blocks and workflows,
* which means departing from how the shindig java implementation works
* but it saves a lot 'dead' code here
"""
class GadgetServer():
    header = {}
    def processGadget(self, context):
        gadget = self.specLoad(context);
        self.featuresLoad(gadget, context);
        return gadget;

    def specLoad(self, context):
        if context.getBlacklist() and context.getBlacklist().isBlacklisted(context.getUrl()):
            raise "Gadget is blacklisted";

        req = RemoteContentRequest(context.getUrl(), {}, context.getPostParam(), context.request)
        xml = context.getHttpFetcher().fetch(req, context)
        if xml.getHttpCode() != 200:
            raise "Failed to retrieve gadget content"

        specParser = GadgetSpecParser()
        try:
            gadget = specParser.parse(xml.getResponseContent(), context)
        except:
            logging.error("gadget parse error")
            raise
            #cache = CacheMemcache()
            #cache.delete()
        return gadget;

    def getBundle(self, localeSpec, context):
        if localeSpec:
            uri = localeSpec.getURI()
            if uri:
                fetcher = context.getHttpFetcher()
                response = fetcher.fetch(RemoteContentRequest(uri), context)
                parser = MessageBundleParser()
                bundle = parser.parse(response.getResponseContent())
                return bundle
        return None

    def localeSpec(self, gadget, locale):
        localeSpecs = gadget.getLocaleSpecs()
        for locSpec in localeSpecs:
            # fix me
            if locSpec.getLocale().equals(locale):
                return locSpec
        return None

    def getLocaleSpec(self, gadget, context):
        locale = context.getLocale()
        # en-US
        localeSpec = self.localeSpec(gadget, locale)
        if (localeSpec == None):
            # en-all
            localeSpec = self.localeSpec(gadget, Locale(locale.getLanguage(), "all"))
        if (localeSpec == None):
            # all-all
            localeSpec = self.localeSpec(gadget, Locale("all", "all"))
        return localeSpec

    def featuresLoad(self, gadget, context):
        #NOTE i've been a bit liberal here with folding code into this function, while it did get a bit long, the many include()'s are slowing us down
        # Should really clean this up a bit in the future though
        localeSpec = self.getLocaleSpec(gadget, context)

        # get the message bundle for this gadget
        bundle = self.getBundle(localeSpec, context)

        #FIXME this is a half-assed solution between following the refactoring and maintaining some of the old code, fixing this up later
        gadget.setMessageBundle(bundle)

        # perform substitutions
        substitutor = gadget.getSubstitutions()

        # Module ID
        substitutor.addSubstitution('MODULE', "ID", gadget.getId().getModuleId())

        # Messages (multi-language)
        if bundle:
            gadget.getSubstitutions().addSubstitutions('MSG', bundle.getMessages())

        # Bidi support
        rtl = False
        if localeSpec != None:
            rtl = localeSpec.isRightToLeft()
        substitutor.addSubstitution('BIDI', "START_EDGE", "right" if rtl else "left")
        substitutor.addSubstitution('BIDI', "END_EDGE", "left" if rtl else "right")
        substitutor.addSubstitution('BIDI', "DIR", "rtl" if rtl else "ltr")
        substitutor.addSubstitution('BIDI', "REVERSE_DIR", "ltr" if rtl else "rtl")

        # userPref's
        upValues = gadget.getUserPrefValues()
        for pref in gadget.getUserPrefs():
            name = pref.getName()
            value = upValues.getPref(name)
            if value == None:
                value = pref.getDefaultValue()
            if value == None:
                value = ""
            substitutor.addSubstitution('USER_PREF', name, value)

        # Process required / desired features
        requires = gadget.getRequires()
        needed = []
        optionalNames = []
        for key,entry in requires:
            needed.append(key)
            if (entry.isOptional()):
                optionalNames.append(key)

        resultsFound = []
        resultsMissing = []
        missingOptional = []
        missingRequired = []
        context.getRegistry().getIncludedFeatures(needed, resultsFound, resultsMissing)
        for missingResult in resultsMissing:
            if missingResult in optionalNames:
                missingOptional[missingResult] = missingResult
            else:
                missingRequired[missingResult] = missingResult

        if len(missingRequired):
            raise("Unsupported feature(s): " + ', '.join(missingRequired))

        # create features
        features = []
        for entry in resultsFound:
            features[entry] = context.getRegistry().getEntry(entry).getFeature().create()

        # prepare them
        for key,feature in features:
            params = gadget.getFeatureParams(gadget, context.getRegistry().getEntry(key))
            feature.prepare(gadget, context, params)

        # and process them
        for key,feature in features:
            params = gadget.getFeatureParams(gadget, context.getRegistry().getEntry(key))
            feature.process(gadget, context, params)
