"""

    Zoho API core functions.

"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"

import urllib, urllib2

import logging

try:
    from xml import etree
    from xml.etree.ElementTree import Element, tostring, fromstring
except ImportError:
     try:
         from lxml import etree
         from lxml.etree import  Element, tostring, fromstring
     except ImportError:
         print "XML library not available:  no etree, no lxml"
         raise
   

try:
    import json as simplejson
except ImportError:
    try:
        import simplejson
    except ImportError:
        # Python 2.4, no simplejson installed
        raise RuntimeError("You need json or simplejson library with your Python")


logger = logging.getLogger("Zoho API")


class ZohoException(Exception):
    """ Bad stuff happens. 
    
    If it's level 15 or higher bug, you usually die.
    If it's lower level then you just lose all your data.
    
    Play some Munchkin.
    """


class Connection(object):
    """ Zoho API connector.
        
    Absract base class for all different Zoho API connections.
    Subclass this and override necessary methods to support different Zoho API groups.
    """

    
    def __init__(self, username, password, authtoken, scope, extra_auth_params = {}, auth_url="https://accounts.zoho.com/login"):        
        """
        @param username: manifisto@mfabrik.com 
        
        @param password: xxxxxxx
        
        @param authtoken: Given by Zoho, string like 123123123-rVI20JVBveUOHIeRYWV5b5kQaMGWeIdlI$
                
        @param extra_auth_params: Dictionary of optional HTTP POST parameters passed to the login call
        
        
        @param auth_url: Which URL we use for authentication
        """        
        self.username = username
        self.password = password
        self.authtoken = authtoken
        self.scope = scope
        # 
        self.auth_url = None

    def get_service_name(self):
        """ Return API name which we are using. """
        raise NotImplementedError("Subclass must implement")
        
    def open(self):
        """ Open a new Zoho API session """
        return
    
    def close(self):
        """ Close the current Zoho API session ("ticket") """
        return

    def do_xml_call(self, url, parameters, root):
        """  Do Zoho API call with outgoing XML payload.
        
        Ticket and authtoken parameters will be added automatically.
        
        @param url: URL to be called
        
        @param parameters: Optional POST parameters. 
        
        @param root: ElementTree DOM root node to be serialized.
        """
        
        parameters = parameters.copy()
        parameters["xmlData"] = tostring(root)
        return self.do_call(url, parameters)

    def do_call(self, url, parameters):
        """ Do Zoho API call.
        
        @param url: URL to be called
        
        @param parameters: Optional POST parameters. 
        """
        # Do not mutate orginal dict
        parameters = parameters.copy()
        parameters["authtoken"] = self.authtoken
        parameters["scope"] = self.scope
        
        stringify(parameters)
        
        if logger.getEffectiveLevel() == logging.DEBUG:                                          
            # Output Zoho API call payload
            logger.debug("Doing ZOHO API call:" + url)
            for key, value in parameters.items():
                logger.debug(key + ": " + value)
                
        request = urllib2.Request(url, urllib.urlencode(parameters))
        response = urllib2.urlopen(request).read()

        if logger.getEffectiveLevel() == logging.DEBUG:                                          
            # Output Zoho API call payload
            logger.debug("ZOHO API response:" + url)
            logger.debug(response)
        
        return response

def stringify(params):
    """ Make sure all params are urllib compatible strings """
    for key, value in params.items():
        
        if type(value) == str:
            params[key] == value.decode("utf-8")
        elif type(value) == unicode:
            pass
        else:
            # call __unicode__ of object
            params[key] = unicode(value)
            

def decode_json(json_data):
    """ Helper function to handle Zoho specific JSON decode.

    @return: Python dictionary/list of incoming JSON data
    
    @raise: ZohoException if JSON'ified error message is given by Zoho
    """
    
    # {"response": {"uri":"/crm/private/json/Leads/getRecords","error": {"code":4500,"message":"Problem occured while processing the request"}}}
    data = simplejson.loads(json_data)
    
    response = data.get("response", None)
    if response:
        error = response.get("error", None)
        if error:
            raise ZohoException("Error while calling JSON Zoho api:" + str(error))
    
    return data
