from django.conf import settings

from basic_remote_content import *
from gadget_id import *
from user_prefs import *
from locale import *
from gadget_feature_registry import *
from cache_memcache import *
import hashlib
import re

DEFAULT_VIEW = 'canvas'
# Configurable classes to use, this way we provide extensibility for what 
# backends the gadget server uses for its logic functionality. 
config = {}
config.update({#'blacklist_class':'BasicGadgetBlacklist',
        'remote_content':'BasicRemoteContent',
        'gadget_signer':'BasicGadgetSigner',
        'gadget_token':'BasicGadgetToken',
        'userpref_param_prefix':'up_',
        'features_path':'/home/hide/scripts/shindig/features',
        })

"""
* GadgetContext contains all contextual variables and classes that are
* relevant for this request, such as url, httpFetcher, feature registry, etc.
* Server wide variables are stored in config.php in the global $config array 
"""
class GadgetContext():
    httpFetcher = None
    locale = None
    renderingContext = None
    registry = None
    userPrefs = None
    gadgetId = None
    view = None
    moduleId = None
    url = None
    cache = None
    blacklist = None
    ignoreCache = False
    syndicatorConfig = None
    syndicator = None

    def __init__(self, url, request, renderingContext):
        self.url = url 
        self.request = request
        # Rendering context is set by the calling event handler
        # (either GADGET or CONTAINER)
	self.setRenderingContext(renderingContext)

        # Request variables
        self.setIgnoreCache(self.getIgnoreCacheParam())
        self.setUrl(self.getUrlParam())
        #self.setModuleId(self.getModuleIdParam())
        self.setView(self.getViewParam())
        self.setSyndicator(self.getSyndicatorParam())
        # NOTE All classes are inititialized when called (aka lazy loading)
        # because we don't need all of them in every situation
	
    def getSyndicatorParam(self):
        synd = 'default'
        if self.request.GET.has_key('synd'):
            synd = self.request.GET['synd'];
        elif self.request.POST.has_key('synd'):
            synd = self.request.POST['synd']
        return synd

    def getIgnoreCacheParam(self):
        # Support both the old Orkut style &bpc and new standard style &nocache= params
        return (self.request.GET.has_key('nocache') and self.request.GET['nocache'] == '1') or (self.request.GET.has_key('bpc') and self.request.GET['bpc'] == '1')

    def getUrlParam(self):
        return self.url

    def getPostParam(self):
        if self.request.POST:
            return self.request.POST
        return None
        
    def getModuleIdParam(self):
        return self.request.GET['mid'] if self.request.GET.has_key('mid') else 0

    def getViewParam(self):
        return self.request.GET['view'] if self.request.GET.has_key('view') else DEFAULT_VIEW

    def instanceBlacklist(self):
        global config
        if config.has_key('blacklist_class'):
            return eval(config['blacklist_class'] + '()')
        else:
            return None

    def instanceUserPrefs(self):
        global config
        prefs = {}
        for key, val in self.request.GET.items():
            if key[:len(config['userpref_param_prefix'])] == config['userpref_param_prefix']:
                name = key[len(config['userpref_param_prefix']):]
                prefs[name] = val

        return UserPrefs(prefs)

    def instanceGadgetId(self, url, moduleId):
        return GadgetId(url, moduleId)

    def instanceHttpFetcher(self):
        global config
        return eval("%s()" % config['remote_content'])

    def instanceCache(self):
        return CacheMemcache()

    def instanceRegistry(self):
        global config
        # Profiling showed 40% of the processing time was spend in the feature registry
        # So by caching this and making it a one time initialization, we almost double the performance  
        #logging.info('instanceRegistry')
        hashkey = hashlib.sha1(config['features_path']).hexdigest()
        registry = self.getCache().get(hashkey)
        if not registry:
            registry = GadgetFeatureRegistry(config['features_path'])
            #self.getCache().set(hashkey, registry)
        return registry

    def instanceLocale(self):
        language = 'all'
        country = 'all'
        if self.request.environ.has_key('HTTP_ACCEPT_LANGUAGE'):
            acceptLanguage = self.request.environ['HTTP_ACCEPT_LANGUAGE'].split(';')
            acceptLanguage = acceptLanguage[0]
	    if acceptLanguage.find('-') > -1:
		lang = acceptLanguage.split('-')
		language = lang[0]
		country = lang[1]
		if country.find(','):
                    country = country.split(',')
		    country = country[0]
	    else:
                language = acceptLanguage
	return Locale(language, country)
	
    def instanceSyndicatorConfig(self):
        global config
        return SyndicatorConfig(config['syndicator_path'])
	
    def getSyndicator(self):
        return self.syndicator
	
    def getSyndicatorConfig(self):
        if self.syndicatorConfig == None:
            self.syndicatorConfig = self.instanceSyndicatorConfig()
        return self.syndicatorConfig
            
    def getCache(self):
	if self.cache == None:
            self.setCache(self.instanceCache())
        return self.cache;

    def getGadgetId(self):
        if self.gadgetId == None:
            self.setGadgetId(self.instanceGadgetId(self.getUrl(), self.getModuleId()))
	return self.gadgetId

    def getModuleId(self):
        return self.moduleId

    def getRegistry(self):
        if self.registry == None:
            self.setRegistry(self.instanceRegistry())
        return self.registry

    def getUrl(self):
        return self.url

    def getUserPrefs(self):
        if self.userPrefs == None:
            self.setUserPrefs(self.instanceUserPrefs())
        return self.userPrefs

    def getView(self):
        return self.view
	
    def setSyndicator(self, syndicator):
        self.syndicator = syndicator
	
    def setSyndicatorConfig(self, syndicatorConfig):
        self.syndicatorConfig = syndicatorConfig

    def setBlacklist(self, blacklist):
        self.blacklist = blacklist

    def setCache(self, cache):
        self.cache = cache

    def setGadgetId(self, gadgetId):
        self.gadgetId = gadgetId

    def setHttpFetcher(self, httpFetcher):
        self.httpFetcher = httpFetcher

    def setLocale(self, locale):
        self.locale = locale

    def setModuleId(self, moduleId):
        self.moduleId = int(moduleId)

    def setRegistry(self, registry):
        self.registry = registry

    def setRenderingContext(self, renderingContext):
        self.renderingContext = renderingContext

    def setUrl(self, url):
        self.url = url

    def setUserPrefs(self, userPrefs):
        self.userPrefs = userPrefs

    def setView(self, view):
        self.view = view

    def setIgnoreCache(self, ignoreCache):
        self.ignoreCache = ignoreCache

    def getIgnoreCache(self):
        return self.ignoreCache

    def getBlacklist(self):
	if self.blacklist == None:
            self.setBlacklist(self.instanceBlacklist())
        return self.blacklist

    def getRenderingContext(self):
        return self.renderingContext

    def getHttpFetcher(self):
        if self.httpFetcher == None:
            self.setHttpFetcher(self.instanceHttpFetcher())
        return self.httpFetcher

    def getLocale(self):
        if self.locale == None:
            self.setLocale(self.instanceLocale())
        return self.locale

    def getFeatureRegistry(self):
        return self.registry
