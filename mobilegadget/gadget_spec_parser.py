from gadget import *
from lxml import objectify
import logging

class GadgetSpecParser():
    # public function parse(GadgetId $id, String $xml)
    def parse(self, xml, context):
        if not xml:
            raise RuntimeError, "Empty XML document"

        # TODO add libxml_get_errors() functionality so we can have a bit more understandable errors..
        doc = objectify.fromstring(xml)
        if doc is None:
	    raise RuntimeError, "Invalid XML document"

        if doc.find('ModulePrefs') is None:
            raise RuntimeError, "Missing or duplicated <ModulePrefs>"

        gadget = Gadget(context.getGadgetId(), context)
	# process ModulePref attributes
        self.processModulePrefs(gadget, doc.ModulePrefs)
	# process UserPrefs, if any
        if doc.findall('UserPref'):
            for pref in doc.UserPref:
                self.processUserPref(gadget, pref);

        if doc.find("Content"):
            for content in doc.Content:
                self.processContent(gadget, content)

	# FIXME : should we add an else { throw new SpecParserException("Missing <Content> block"); } here ? Java version doesn't but it seems like we should ?
        if doc.find("ModulePrefs/Require"):
            for feature in doc.ModulePrefs.Require:
                self.processFeature(gadget, feature, True)

        if doc.find("ModulePrefs/Optional"):
            for feature in doc.ModulePrefs.Optional:
                self.processFeature(gadget, feature, False)

	# TODO java version has a todo here for parsing icons
        return gadget

    def processModulePrefs(self, gadget, ModulePrefs):
	attributes = dict(ModulePrefs.attrib)
	if not attributes.has_key('title'):
            raise RuntimeError, 'Missing or empty "title" attribute.'

	# Get ModulePrefs attributes
	# (trim is used here since it not only cleans up the text, but also auto-casts the SimpleXMLElement to a string)
	gadget.title = attributes['title'].strip()
	gadget.author = attributes.get('author', '')
	gadget.authorEmail = attributes.get('author_email', '')
	gadget.description = attributes.get('description', '')
	gadget.directoryTitle = attributes.get('directory_title', '')
	gadget.screenshot = attributes.get('screenshot', '')
	gadget.thumbnail = attributes.get('thumbnail', '')
	gadget.titleUrl = attributes.get('title_url', '')
	gadget.backgroundColor = attributes.get('background-color', '')
	gadget.textColor = attributes.get('text-color', '')
	gadget.linkColor = attributes.get('link-color', '')
	gadget.hrColor = attributes.get('hr-color', '')
        banpc = attributes.get('prohibit-pc', 'false')
	gadget.prohibitPC =  banpc.lower() == 'true'
	for locale in ModulePrefs.get('Locale', []):
	    gadget.localeSpecs.append(self.processLocale(locale))


    def processLocale(self, locale):
        attributes = locale.attributes()
        messageAttr = attributes.getDefault('messages', '')
	languageAttr = attributes.getDefault('lang', 'all')
	countryAttr = attributes.getDefault('country', 'all')
	rtlAttr = attributes.getDefault('language_direction', '')
	rightToLeft = rtlAttr == 'rtl';
	locale = LocaleSpec()
	locale.rightToLeft = rightToLeft
	# FIXME java seems to use a baseurl here, probably for the http:// part but i'm not sure yet. Should verify behavior later to see if i got it right
        locale.url = messageAttr;
        locale.locale = Locale(languageAttr, countryAttr)
        return locale;

    def processUserPref(self, gadget, pref):
        attributes = pref.attrib
        preference = UserPref()
        if not attributes['name']:
	    raise RuntimeError, "All UserPrefs must have name attributes."

        preference.name = attributes['name'].strip()
        preference.displayName = attributes.get('display_name', '')
	# if its set -and- in our valid 'enum' of types, use it, otherwise assume STRING, to try and emulate java's enum behavior
	#preference.dataType = isset($attributes['datatype']) && in_array(strtoupper($attributes['datatype']), $preference.DataTypes) ? strtoupper($attributes['datatype']) : 'STRING';
	preference.defaultValue = attributes.get('default_value', '').strip()
	if pref.find('EnumValue'):
	    for enum in pref.EnumValue:
                attr = enum.attrib
                # java based shindig doesn't throw an exception here, but it -is- invalid and should trigger a parse error
		if not attr['value']:
                    raise RuntimeError, "EnumValue must have a value field."
                valueText = attr['value'].strip()
		displayText = attr.getDefault('display_value', valueText).strip()
		preference.enumValues[valueText] = displayText

        gadget.userPrefs.append(preference)
                    
    def processContent(self, gadget, content):
        attributes = content.attrib
	if not attributes['type']:
	    raise SpecParserException("No content type specified!")

        type = attributes['type'].strip()
        if type == 'url':
	    if not attributes['href']:
		raise RuntimeError, "Malformed <Content> href value"

            url = attributes['href'].strip()
            gadget.contentType = 'URL'
	    gadget.contentHref = url
        else:
            gadget.contentType = 'HTML'
	    html = content # no trim here since empty lines can have structural meaning, so typecast to string instead
            view = attributes.get('view', '')
	    views = view.split(',')
            for view in views:
	        gadget.addContent(view, html)

    def processFeature(self, gadget, feature, required):
	featureSpec = FeatureSpec()
	attributes = feature.attributes()
	if not attributes['feature']:
            raise RuntimeError, "Feature not specified in <%s> tag" % "Optional" if required else "Required"
	featureSpec.name = attributes['feature'].strip()
	featureSpec.optional = not required
	for param in feature.Param:
            attr = param.attributes()
            if not attr['name']:
	        raise RuntimeError, "Missing name attribute in <Param>."
            name = attr['name'].strip()
            value = param.strip()
            featureSpec.params[name] = value
	    gadget.requires[featureSpec.name] = featureSpec
