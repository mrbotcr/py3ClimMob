'''

This file declares the PCA interfaces and their methods:

This code is based on CKAN 
:Copyright (C) 2007 Open Knowledge Foundation
:license: AGPL V3, see LICENSE for more details.

'''


__all__ = [
    'Interface',
    'IRoutes',
    'IConfig',
    'IResource',
    'ISchema',
    'IPluginObserver',
    'IPluralize',
    'IPackage',
    'ISubmissionStorage',
    'IProduct',
    'ITemplateHelpers'
]


from inspect import isclass
from pyutilib.component.core import Interface as _pca_Interface

class Interface(_pca_Interface):

    @classmethod
    def provided_by(cls, instance):
        return cls.implemented_by(instance.__class__)

    @classmethod
    def implemented_by(cls, other):
        if not isclass(other):
            raise TypeError("Class expected", other)
        try:
            return cls in other._implements
        except AttributeError:
            return False

class IRoutes(Interface):
    """
    Plugin into the creation of routes of the host program.

    """
    def before_mapping(self,config):
        """
        Called before the mapping of router of the host app.

        :param config: ``pyramid.config`` object that can be used to call add_view
        :return Returns a dict array [{'name':'myroute','path':'/myroute','view',viewDefinition,'renderer':'renderere_used'}]
        """
        return []

    def after_mapping(self,config):
        """
        Called after the mapping of router of the host app

        :param config: ``pyramid.config`` object that can be used to call add_view
        :return Returns a dict array [{'name':'myroute','path':'/myroute','view',viewDefinition,'renderer':'renderere_used'}]
        """
        return []

class IConfig(Interface):
    """
    Allows the modification of the Pyramid config 
    """

    def update_config(self, config):
        """
        Called in the init of the host application.

        :param config: ``pyramid.config`` object
        """

class IResource(Interface):
    """
        Allows to hook into the creation of JS and CSS libraries or resources
    """

    def add_libraries(self, config):
        """
        Called by FormShare so plugins can add new JS and CSS libraries to FormShare

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'name':'mylibrary','path':'/path/to/my/resources'}]
        """
        raise NotImplementedError("add_libraries must be implemented in subclasses")

    def add_js_resources(self, config):
        """
        Called by FormShare so plugins can add new JS Resources

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'libraryname':'mylibrary','id':'myResourceID','file':'/relative/path/to/jsFile',
                                      'depends':'resourceID'}]
        """
        raise NotImplementedError("add_js_resources must be implemented in subclasses")

    def add_css_resources(self, config):
        """
        Called by FormShare so plugins can add new FanStatic CSS Resources

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'libraryname':'mylibrary','id':'myResourceID','file':'/relative/path/to/jsFile',
                                      'depends':'resourceID'}]
        """
        raise NotImplementedError("add_css_resources must be implemented in subclasses")

class ISchema(Interface):
    """
        Allows to hook into the schema processes and add new fields into it
    """

    def update_schema(self,config):
        """
        Called by the host application so plugins can add new fields to the project schema

        :param config: ``pyramid.config`` object
        :return Returns a dict array [{'schema':'schema_to_update','fieldname':'myfield','fielddesc':'A good description of myfield'}]
        
        Plugin writers should use the Climmob utility functions:
            - addFieldToUserSchema
            - addFieldToProjectSchema
            - addFieldToQuestionSchema
        
        Instead of constructing the dict by themselves to ensure API compatibility
        
        """
        return []



class IPluralize(Interface):
    """
        Allows to hook into the pluralization function so plugins can extend the pluralization of climmob
    """
    def pluralize(self,noun,locale):
        """
            Called the packages are created

            :param noun: ``Noun to be pluralized``
            :param locale: ``The current locate code e.g. en``
            :return the noun in plural form
        """


class IPackage(Interface):
    """
        Allows to hook into the creation of packages
    """
    def after_create_packages(self,request,user,project,processName,options,packages):
        """
            Called the packages are created

            :param request: ``The current request`` object
            :param user: ``The current user ID``
            :param project: ``The current project ID``
            :param options: ``The number of options each package has e.g., 3 (A,B,C)`` object
            :param packages: ``A multi-dimension dict array containing detail information about the packages `` object
            :return Not needed
        """


class ISubmissionStorage(Interface):
    """
        Allows to hook into the submission of data from ODK Collect.
        Data first lands in XML format and through ODK tools (XMLToJSON) is transformed into JSON format
        which is easy to understand and edit
    """
    def before_save_in_json(self,request,user,project,data):
        """
            Called before the JSON data is stored into the server and before
            is processed into the final MySQL database.
            You can use this to modify the date before is stored in JSON

            :param request: ``The current request`` object
            :param user: ``The current user ID``
            :param project: ``The current project ID``
            :param data: ``The data as milti-dimension dict``
            :return a modified version of data.
            Warning: EXTEND ONLY IF YOU KNOW WHAT YOU ARE DOING!
            Warning: Removing keys from the data may crash Climmob.
            Warning: Any keys that you add will not enter the MySQL unless you also extend beforeSaveInMySQL
        """

    def before_save_in_mysql(self,request,user,project,manifest):
        """
            Called before the data is stored in the MySQL database.
            You can use this to made changes in the manifest before data is stored

            :param request: ``The current request`` object
            :param user: ``The current user ID``
            :param project: ``The current project ID``
            :param manifest: ``The lxml element root of the manifest`` object
            :return a modified version of manifestElementRoot.
            Warning: EXTEND ONLY IF YOU KNOW WHAT YOU ARE DOING!
            Warning: Removing/adding elements to the manifest may crash Climmob.
            Warning: Any elements that you add will not enter the MySQL unless you also extend beforeSaveInJSON
        """

class IProduct(Interface):
    """
        Allows to hook into Climmob's Celery task manager.
    """
    def register_products(self, config):
        """
            Called by the host application so plugins can add new products

            :param config: ``pyramid.config`` object
            :return Returns a dict array [{'name':'productName','description':'A description about the product','metadata':{'key':value},outputs:[{'filename':'myproduct.pdf','mimetype':'application/pdf'}] }]
        """
        return []


class IPluginObserver(Interface):
    """
    Plugin to the plugin loading mechanism
    """

    def before_load(self, plugin):
        """
        Called before a plugin is loaded
        This method is passed the plugin class.
        """

    def after_load(self, service):
        """
        Called after a plugin has been loaded.
        This method is passed the instantiated service object.
        """

    def before_unload(self, plugin):
        """
        Called before a plugin is loaded
        This method is passed the plugin class.
        """

    def after_unload(self, service):
        """
        Called after a plugin has been unloaded.
        This method is passed the instantiated service object.
        """

class ITemplateHelpers(Interface):
    """
    Add custom template helper functions.

    By implementing this plugin interface plugins can provide their own
    template helper functions, which custom templates can then access via the
    ``request.h`` variable.
    """

    def get_helpers(self):
        """
        Return a dict mapping names to helper functions.

        The keys of the dict should be the names with which the helper
        functions will be made available to templates, and the values should be
        the functions themselves. For example, a dict like:
        ``{'example_helper': example_helper}`` allows templates to access the
        ``example_helper`` function via ``request.h.example_helper()``.

        Function names should start with the name of the extension providing
        the function, to prevent name clashes between extensions.
        :return:
        """