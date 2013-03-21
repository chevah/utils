# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
'''Common interfaces used by Chevah products.'''

from zope.interface import Interface, Attribute


class PublicAttribute(Attribute):
    """
    An public atribute which can only be read.
    """


class PublicWritableAttribute(PublicAttribute):
    """
    An public atribute which can be read and written.
    """


class PublicSectionAttribute(Attribute):
    """
    An public section atribute. This is a collection of attributes and
    can not be written.
    """


class IConfigurationProxy(Interface):
    '''Interface for configurations objects.'''

    def hasSection(section):
        '''Returns True if `section` exists.'''

    def addSection(section):
        '''Add `section` to the configuration.'''

    def hasOption(section, option):
        '''Returns True if `section` contains `options`.'''

    def getString(section, option):
        '''Return the String value for `option` from `section`.'''

    def setString(section, option, value):
        '''Set the String value for `option` from `section`.'''

    def getInteger(section, option):
        '''Return the Integer value for `option` from `section`.'''

    def getint(section, option):
        '''Raise AssertionError if low level methods are called.'''

    def getBoolean(section, option):
        '''Return the Boolean value for `option` from `section`.'''

    def setBoolean(section, option, value):
        '''Set the Boolean value for `option` from `section`.'''

    def getFloat(section, option):
        '''Return the Float value for `option` from `section`.'''


class _IWithPropertiesMixin(Interface):
    """
    Private interface use to share attributed related to properties
    handling.

    This defined a CRUD interface for managing configuration:
    * create
    * get (read)
    * set (update)
    * delete

    All methods receive a `property_path` is in the format
    `section/property` or `section/subsection`.

    Configuration values are passed as primitive data
    (string/integer/None/boolean) and complex objects are not supported.
    Primitive data can be grouped in arrays or dictionaries.

    The class implementing this interface should also define one of the
    following properties to allow exporting them:
    * PublicAttribute
    * PublicWritableAttribute
    * PublicSectionAttribute
    """

    def getPulicAttributeNames():
        """
        Retrun the list of all names of public read attributes.
        """

    def getPulicWritableAttributeNames():
        """
        Retrun the list of all names of public writable attributes.
        """

    def getPublicSectionNames():
        """
        Return the list of all names for public sections.
        """

    def getAttribute(name):
        """
        Return the value of attribute with `name`.

        Raise NoSuchAttributeError if attribute does not exists.
        """

    def setAttribute(name, value):
        """
        Set value for attribute with name.

        Raise NoSuchPropertyException.
        """

    def getSection(name):
        """
        Return the section with `name`.

        Raise NoSuchSectionError if section does not exists.
        """

    def createProperty(property_path, value):
        """
        Add property denoted by `property_path`.
        """

    def getProperty(property_path=None):
        """
        Return a dictionary for properties matching property_path.

        When property_path is None returns all property members as key-value.
        {
            property1_name: property1_value,
            property2_name: property2_value,
            sub_section1: { prop1: value2 },
        }

        When a property_path is specified, it will return only the properties
        for that path.

        For example for `sec1/sec2` it will return"
        {
            'sec1': {
                'sec2' : {
                    'pro2': value1,
                    'prop2': value2,
                }
            }

        }
        """

    def setProperty(property_path, value):
        """
        Set property value denoted by `property_path`.
        """

    def deleteProperty(property_path):
        """
        Delete property denoted by `property_path`.
        """


class IConfigurationSection(_IWithPropertiesMixin):
    """
    A section from the configuration file.
    """

    _proxy = Attribute('Proxy used for persisting the configurations.')


class IConfiguration(_IWithPropertiesMixin):
    '''Root configuration.'''

    def __init__(configuration_path, configuration_file):
        '''Initialize the IConfiguration.

        configuration_path and configuration_file are mutually exclusive.
        '''


class ICredentials(Interface):
    """
    Hold credentials as provides by clients while authentication using
    various services.

    Provides attributes shared by all credential types.
    """
    username = Attribute(
        '''
        Username for which the authentication is requested.
        ''')

    peer = Attribute(
        '''
        IP address and port number for the remote peer requesting
        authentication.
        ''')

    kind_name = Attribute(
        '''
        Human readable name for the type of these credentials.

        Example: `"password"`, `"ssh key"`, `"ssl certificate"`... etc
        ''')


class IPasswordCredentials(ICredentials):
    """
    Credentials based on password.
    """
    password = Attribute(
        '''
        Password associated with the username.
        ''')


class ISSHKeyCredentials(ICredentials):
    """
    Credentials based on SSH key.
    """

    key_algorithm = Attribute(u'Algorithm for SSH key.')
    key_data = Attribute(u'Content of SSH key.')
    key_signed_data = Attribute(u'Signed data for SSH key.')
    key_signature = Attribute(u'Signature for SSH key.')


class ISSLCertificateCredentials(ICredentials):
    """
    Credentials base on SSL certificate.
    """

    certificate = Attribute(
        '''
        pyOpenSSL certificate object.
        ''')


class ILocalAdminCredentials(ICredentials):
    """
    Credentials used for administration.
    """

    username = Attribute('Username used at authentication.')
    password = Attribute('Password used at authentication.')
    peer = Attribute('Peer for this credentials')


class IHTTPBasicAuthCredentials(IPasswordCredentials):
    '''Marker interface for password based credentials generated by
    HTTP Basic Authentication.'''


class IHTTPSBasicAuthCredentials(IPasswordCredentials):
    '''Marker interface for password based credentials generated by
    HTTPS Basic Authentication.'''


class IFTPPasswordCredentials(IPasswordCredentials):
    '''Marker interface for a password based credentials obtained via FTP.'''


class IFTPSPasswordCredentials(IPasswordCredentials):
    '''Marker interface for a password based credentials obtained via FTPS.'''


class ISSHPasswordCredentials(IPasswordCredentials):
    '''Marker interface for a password based credentials obtained via SSH.'''


class IFTPSSSLCertificateCredentials(ISSLCertificateCredentials):
    '''Interface for SSL certificate based credentials used for FTPS.'''


class IHTTPSSSLCertificateCredentials(ISSLCertificateCredentials):
    '''Interface for SSL certificate based credentials used for HTTPSS.'''


class IEvent(Interface):
    """An event as raised by a service."""

    id = Attribute(u'Name of the group.')
    data = Attribute('Dictionary with data for this event.')


class IEventDefinition(Interface):
    """Configuration definition for an Event."""

    id = Attribute(u'Name of the group.')
    message = Attribute(u'Text logged for this event.')
    description = Attribute(u'Detailed description')
    version_added = Attribute(u'Version when this event was added.')
    version_removed = Attribute(u'Version when this event was removed.')


class IEventGroupDefinition(Interface):
    """Configuration definition for an EventGroup."""

    name = Attribute(u'Name of the group.')
    description = Attribute(u'Group description')


class IEventsDefinition(Interface):
    """Stores the definitions for events and event groups.

    Definitions are the static rules for all events.
    """

    def load():
        """Load configured events, eventgroups and rules.

        Raises an error if the configration is not valid.
        """

    def getEventDefinition(id):
        """
        Return the EventDefiniton for `id`.

        Raises an error if EventDefinition was not found.
        """

    def getAllEventDefinitions():
        """
        Return a dictionary with all EventDefiniton.

        The dictionary is keyed based on event id.
        """

    def getAllEventDefinitionsPadded():
        """
        Return a dictionary with all EventDefiniton.

        The dictionary is keyed based on padded event id.
        """

    def getEventGroupDefinition(name):
        """
        Return the EventGroupDefinition for `name`.

        Raises an exception if EventGroupDefinition was not found.
        """

    def getAllEventGroupDefinitions():
        """
        Return a dictionaly with all EventGroupDefinition.

        The dictionary is keyed based on group name.
        """

    def generateDocumentation(template):
        """
        Return a string with events' documentation.

        Documentation is formated as ReStructuredText using Jinja2 `template`.
        """


class IIdleTimeoutProtocol(Interface):
    """
    A protocol that times out if idle.
    """

    timeOut = Attribute(
        u'Number of seconds ofter which the idle connection is disconnected')

    def callLater(period, func):
        """
        Wrapper around L{reactor.callLater} for test purpose.
        """

    def resetTimeout():
        """
        Reset the timeout count down.

        If the connection has already timed out, then do nothing.  If the
        timeout has been cancelled (probably using C{setTimeout(None)}), also
        do nothing.

        It's often a good idea to call this when the protocol has received
        some meaningful input from the other end of the connection.  "I've got
        some data, they're still there, reset the timeout".
        """

    def setTimeout(period):
        """
        Change the timeout period

        @type period: C{int} or C{NoneType}
        @param period: The period, in seconds, to change the timeout to, or
        C{None} to disable the timeout.
        """

    def timeoutConnection():
        """
        Called when the connection times out.

        Override to define behavior other than dropping the connection.
        """


class ILogConfigurationSection(Interface):
    """
    Section storing configurations for the logger.
    """
    file = PublicWritableAttribute(
        'Path to file where logs are stored.')
    file_rotate_external = PublicWritableAttribute(
        'Should be enabled when an external log rotation is enabled. '
        'Yes | No')
    file_rotate_at_size = PublicWritableAttribute(
        'Trigger rotation when file reaches this size. 0 | Disabled')
    file_rotate_each = PublicWritableAttribute(
        '1 hour | 2 seconds | 2 midnight | 3 Monday | Disabled')
    file_rotate_count = PublicWritableAttribute(
        'How many rotated file to be stored. 3 | 0 | Disabled')
    syslog = PublicWritableAttribute(
        'SysLog configuration. /path/to/syslog/pype | syslog.host:port')
    enabled_groups = PublicWritableAttribute(
        'List of groups for which logs are emitted.')
