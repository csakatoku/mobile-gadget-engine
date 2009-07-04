from substitutions import *
from gadget_context import *
import logging

class Gadget():
    messageBundle = []
    # As in UserPref, no enums so fake it
    contentTypes = ['HTML', 'URL']
    contentData = {}
    localeSpecs = []
    preloads = []
    requires = []
    titleUrl = None
    userPrefs = []

    def __init__(self, id=False, context=None):
        # TODO
        self.contentType = 'HTML'
        if id:
            self.id = id
        if context.getUserPrefs():
            self.setPrefs(context.getUserPrefs())
        self.substitutions = Substitutions()
        self.jsLibraries = []
        self.contentData = {}

    def setId(self, id):
        self.id = id

    def setPrefs(self, prefs):
        self.userPrefValues = prefs

    def getAuthor(self):
        return self.substitutions.substitute(self.author)

    def getAuthorEmail(self):
        return self.substitutions.substitute(self.authorEmail)

    def getContentData(self, view=False):
        if self.contentType != 'HTML':
            raise SpecParserException("getContentData() requires contentType HTML")
        if not view:
            view = DEFAULT_VIEW;
        return self.substitutions.substitute(self.contentData[view].strip() if self.contentData.has_key(view) else '')

    def getContentHref(self):
        return self.substitutions.substitute(self.contentHref if self.getContentType() == 'URL' else None)

    def getMessageBundle(self):
        return self.messageBundle

    def getDescription(self):
        return self.substitutions.substitute(self.description)

    def getDirectoryTitle(self):
        return self.substitutions.substitute(self.directoryTitle)

    def getId(self):
        return self.id

    def getJsLibraries(self):
        return self.jsLibraries

    def addJsLibrary(self, library):
        self.jsLibraries.expand(library)

    def getLocaleSpecs(self):
        return self.localeSpecs

    def getFeatureParams(self, gadget, feature):
        # FIXME not working atm
        spec = gadget.getRequires()
        spec = spec.getDefault(feature.getName(), None)
        if spec == None:
            return []
        else:
            return spec.getParams()

    def getPreloads(self):
        ret = []
        for preload in self.preloads:
            ret.expand(self.substitution.substitute(preload))
        return ret

    def getRequires(self):
        return self.requires

    def getScreenshot(self):
        return self.substitutions.substitute(self.screenshot)

    def getSubstitutions(self):
        return self.substitutions

    def getThumbnail(self):
        return self.substitutions.substitute(self.thumbnail)

    def getTitle(self):
        return self.substitutions.substitute(self.title)

    def getTitleURI(self):
        ret = None
        if not empty(self.titleURI):
            ret = self.substitutions.substitute(self.titleURI)
        return ret

    def getUserPrefs(self):
        return self.userPrefs

    def getUserPrefValues(self):
        return self.userPrefValues

    def setMessageBundle(self, messageBundle):
        self.messageBundle = messageBundle

    # gadget Spec functions
    def addContent(self, view, data):
        if not view:
            view = DEFAULT_VIEW
        if not self.contentData.has_key(view):
            self.contentData[view] = ''
        self.contentData[view] += data

    def getContentType(self):
        return self.contentType


class LocaleSpec():
    def getURI(self):
        return self.url

    def getLocale(self):
        return self.locale

    def isRightToLeft(self):
        return self.rightToLeft


class FeatureSpec():
    params = []

    def getName(self):
        return self.name

    def getParams(self):
        return self.params

    def isOptional(self):
        return self.optional


class UserPref():
    DataTypes = ['STRING', 'HIDDEN', 'BOOL', 'ENUM', 'LIST', 'NUMBER']

    def getName(self):
        return self.name

    def getDisplayName(self):
        return self.displayName

    def getDefaultValue(self):
        return self.defaultValue

    def isRequired(self):
        return self.required

    def getDataType(self):
        return self.dataType

    def getEnumValues(self):
        return self.enumValues
