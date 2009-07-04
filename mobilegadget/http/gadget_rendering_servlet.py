# -*- coding: utf-8 -*-
from django.http import *
from mobilegadget.http_servlet import HttpServlet
from mobilegadget.gadget_context import GadgetContext
from mobilegadget.gadget_server import GadgetServer
from urllib2 import HTTPError
import logging, sys

"""
* This class deals with the gadget rendering requests (in default config this
* would be /gadgets/ifr?url=<some gadget's url>). It uses the gadget server and
* gadget context to render the xml to a valid html file, and outputs it.
* 
"""
class GadgetRenderingServlet(HttpServlet):
    prohibitPC = False

    """
    * Creates the gadget using the GadgetServer class and calls outputGadget
    *
    """
    def doGet(self, view=None):
        if not self.url:
            raise RuntimeError, "Missing required parameter: url"

        try:
            # GadgetContext builds up all the contextual variables
            # (based on the url or post) 
            # plus instances all required classes
            # (feature registry, fetcher, blacklist, etc)
            context = GadgetContext(self.url, self.request, 'GADGET')
            context.setModuleId(self.moduleId)
            context.setView(view)

            gadgetServer = GadgetServer()
            if self.request.method != 'GET':
                context.setIgnoreCache(True)
            gadget = gadgetServer.processGadget(context)

            self.title = gadget.title
            self.backgroundColor = gadget.backgroundColor
            self.textColor = gadget.textColor
            self.linkColor = gadget.linkColor
            self.hrColor = gadget.hrColor
            self.prohibitPC = gadget.prohibitPC
            
            return self.outputGadget(gadget, context)

        except HTTPError, e:
            if e.code in (301, 302):
                raise
            return self.outputError(e)            
        except Exception, e:
            self.outputError(e)
            raise

    def doPost(self, view=None):
        return self.doGet(view)
        
    """
    * If an error occured (Exception) this function echo's the Exception's
    * message and if the config['debug'] is true, shows the debug backtrace
    * in a div
    *
    * @param Exception $e the exception to show
    """
    def outputError(self, e):
        logging.error(e)

    """
    * Takes the gadget to output, and depending on its content type calls
    * either outputHtml- or outputUrlGadget
    *
    * @param Gadget $gadget gadget to render
    * @param string $view the view to render
    *  (only valid with a html content type)
    """
    def outputGadget(self, gadget, context):
        if gadget.getContentType() != 'HTML':
            raise RuntimeError, "Content type: '" + gadget.getContentType() \
                + "' is not supported"

        return self.outputHtmlGadget(gadget, context);

    """
    * Outputs a html content type gadget.
    * It creates a html page, with the javascripts from the features inline
    * into the page, plus calls to 'gadgets.config.init' with the syndicator
    * configuration (config/syndicator.js) and 'gadgets.Prefs.setMessages_'
    * with all the substitutions. For external javascripts it adds
    * a <script> tag.
    *
    * @param Gadget $gadget
    * @param GadgetContext $context
    """
    def outputHtmlGadget(self, gadget, context):
        #self.setContentType("text/html; charset=UTF-8")
        self.contentType = "text/html; charset=UTF-8"
        output = ''

        gadgetExceptions = []
        content = gadget.getContentData(context.getView())
        if not content:
            # unknown view
            raise RuntimeError, "View: '" + context.getView() + "' invalid for gadget: " + gadget.getId().getKey()
        if len(gadgetExceptions):
            raise RuntimeError, gadgetExceptions
        output += content + "\n"

        return output

    """
    * Returns the requested libs (from getjsUrl) with the libs_param_name
    * prepended
    * ie: in libs=core:caja:etc.js format
    *
    * @param string $libs the libraries
    * @param Gadget $gadget
    * @return string the libs=... string to append to the redirection url
    """
    def appendLibsToQuery(self, libs, gadget):
        global settings
        ret = "&"
        ret = ret + settings['libs_param_name']
        ret = ret + "="
        ret = ret + self.getJsUrl(libs, gadget)
        return ret

    """
    * Returns the user preferences in &up_<name>=<val> format
    *
    * @param array $libs array of features this gadget requires
    * @param Gadget $gadget
    * @return string the up_<name>=<val> string to use in the redirection url
    """
    def getPrefsQueryString(self, prefVals):
        global settings
        ret = ''
        for (key, val) in prefVals.getPrefs():
            ret = ret + '&'
            ret = ret + settings['userpref_param_prefix']
            ret = ret + urlencode(key)
            ret = ret + '='
            ret = ret + urlencode(val)
        return ret

    def appendMessages(self, gadget):
        msgs = ''
        if (gadget.getMessageBundle()):
            bundle = gadget.getMessageBundle()
            msgs = json_encode(bundle.getMessages())
        return "gadgets.Prefs.setMessages_($msgs);\n"
