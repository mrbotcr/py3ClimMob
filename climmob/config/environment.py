"""
This files configure host application

This code is based on CKAN 
:Copyright (C) 2007 Open Knowledge Foundation
:license: AGPL V3, see LICENSE for more details.

"""

import os
from pyramid.session import SignedCookieSessionFactory
import climmob.plugins as p
from climmob.config.routes import loadRoutes
from climmob.config.jinja_extensions import (
    initialize,
    SnippetExtension,
    extendThis,
    CSSResourceExtension,
    JSResourceExtension,
)
import climmob.resources as r
import climmob.products as prd
from climmob.config.mainresources import createResources
from climmob.models import addColumnToSchema
import climmob.utility.helpers as helpers
from climmob.products.climmob_products import register_products

my_session_factory = SignedCookieSessionFactory("b@HdX5Y6nL")

# This function return the address of a static URL.
# It substitutes request.static_url because
# static_url does not work for plugins when using
# a full path to the static directory


def __url_for_static(request, static_file, library="static"):
    """
    This function return the address of a static URL. It substitutes request.static_url because static_url does not
    work for plugins when using a full path to the static directory
    :param request: Current request object
    :param static_file: Static file being requested
    :param library: Library where the static file is located
    :return: URL to the static resource
    """
    return request.application_url + "/" + library + "/" + static_file


main_policy_array = []


def get_policy_array(request):
    return main_policy_array


class RequestResources(object):
    """
    This class handles the injection of resources in templates
    """

    def __init__(self, request):
        self.request = request
        self.current_resources = []

    def add_resource(self, library_name, resource_id, resource_type):
        self.current_resources.append(
            {
                "libraryName": library_name,
                "resourceID": resource_id,
                "resourceType": resource_type,
            }
        )

    def resource_in_request(self, library_name, resource_id, resource_type):
        for resource in self.current_resources:
            if (
                resource["libraryName"] == library_name
                and resource["resourceID"] == resource_id
                and resource["resourceType"] == resource_type
            ):
                return True
        return False


def __helper(request):
    h = helpers.helper_functions
    return h


def load_environment(settings, config, apppath, policy_array):

    for policy in policy_array:
        main_policy_array.append(policy)

    # Add the session factory to the confing
    config.set_session_factory(my_session_factory)

    # Add render subscribers for internationalization
    # config.add_translation_dirs("climmob:locale")
    config.add_subscriber(
        "climmob.i18n.i18n.add_renderer_globals", "pyramid.events.BeforeRender"
    )
    config.add_subscriber(
        "climmob.i18n.i18n.add_localizer", "pyramid.events.NewRequest"
    )

    config.registry.settings["jinja2.extensions"] = [
        "jinja2.ext.i18n",
        "jinja2.ext.do",
        "jinja2.ext.with_",
        SnippetExtension,
        extendThis,
        CSSResourceExtension,
        JSResourceExtension,
    ]

    config.include("pyramid_jinja2")
    # Add url_for_static to the request so plugins can use static resources
    config.add_request_method(__url_for_static, "url_for_static")

    # config.include('pyramid_fanstatic')
    config.add_request_method(RequestResources, "activeResources", reify=True)
    # This allow to have the helper functions per request
    # request.h.function()
    # config.add_request_method(__helper, 'h',reify=True)

    # Create the main resources
    createResources(apppath, config)

    templatesPathArray = []
    templatesPath = os.path.join(apppath, "templates")
    templatesPathArray.append(templatesPath)

    config.add_settings(templatesPaths=templatesPathArray)

    staticPath = os.path.join(apppath, "static")
    config.add_static_view("static", staticPath, cache_max_age=3600)

    config.add_jinja2_search_path(templatesPath)

    # Load all connected plugins
    p.load_all(settings)

    # Add a series of helper functions to the request like pluralize
    helpers.load_plugin_helpers()
    config.add_request_method(__helper, "h", reify=True)

    config.add_request_method(get_policy_array, "policies", reify=False)

    # Load any change in the configuration done by connected plugins
    for plugin in p.PluginImplementations(p.IConfig):
        plugin.update_config(config)

    # Call any connected plugins to add their libraries
    for plugin in p.PluginImplementations(p.IResource):
        pluginLibraries = plugin.add_libraries(config)
        for library in pluginLibraries:
            r.add_library(library["name"], library["path"], config)

    # Call any connected plugins to add their CSS Resources
    for plugin in p.PluginImplementations(p.IResource):
        cssResources = plugin.add_css_resources(config)
        for resource in cssResources:
            r.add_css_resource(
                resource["libraryname"],
                resource["id"],
                resource["file"],
                resource["depends"],
            )

        # Call any connected plugins to add their JS Resources
        for plugin in p.PluginImplementations(p.IResource):
            js_resources = plugin.add_js_resources(config)
            for resource in js_resources:
                r.add_js_resource(
                    resource["libraryname"],
                    resource["id"],
                    resource["file"],
                    resource["depends"],
                )

    # Register climmob products
    for product in register_products(config):
        prd.addProduct(product)

    # Call any connected plugins to add their products
    for plugin in p.PluginImplementations(p.IProduct):
        products = plugin.register_products(config)
        for product in products:
            prd.addProduct(product)

    # Call any connected plugins to add their modifications into the schema
    schemas_allowed = ["user", "project", "question", "assessment"]
    for plugin in p.PluginImplementations(p.ISchema):
        schemaFields = plugin.update_schema(config)
        for field in schemaFields:
            if field["schema"] in schemas_allowed:
                addColumnToSchema(
                    field["schema"], field["fieldname"], field["fielddesc"]
                )

    for plugin in p.PluginImplementations(p.IDatabase):
        plugin.update_orm(config.registry["dbsession_metadata"])

    # jinjaEnv is used by the jinja2 extensions so we get it from the config
    jinjaEnv = config.get_jinja2_environment()

    # setup the jinjaEnv template's paths for the extensions
    initialize(config.registry.settings["templatesPaths"])

    # Finally we load the routes
    loadRoutes(config)
