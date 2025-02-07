from pyramid.httpexceptions import HTTPFound
import json
import logging
from climmob.processes import (
    getLastActivityLogByUser,
    getListOfLanguagesByUser,
    getTechnologiesByUserWithoutCropTaxonomy,
    getProjectsByUserThatRequireSetup,
)

log = logging.getLogger(__name__)


def CheckMiddleware(event):
    request = event.get("request")

    if request.matched_route:

        if not request.authenticated_userid:
            log.debug("No authenticated user. Passing request.")
            return

        authenticated_user = request.authenticated_userid
        try:
            authenticated_user = json.loads(authenticated_user.replace("'", '"'))
        except json.JSONDecodeError as e:
            log.error(f"JSON decode error for authenticated_userid: {e}")
            return

        login = authenticated_user.get("login")
        if not login:
            log.warning(
                "Authenticated user does not have a login key. Passing request."
            )
            return

        last_activity = getLastActivityLogByUser(login, request)
        if last_activity:
            if last_activity["log_message"] != "Welcome to ClimMob":

                list_of_path = []

                list_of_path.append("otherLanguages")
                list_of_path.append("getUserLanguagesPreview")
                list_of_path.append("addUserLanguage")
                list_of_path.append("APIlanguages")

                if request.matched_route.name not in list_of_path:
                    if not getListOfLanguagesByUser(request, login):
                        raise HTTPFound(
                            location=request.route_url(
                                "otherLanguages", _query={"help": "languages"}
                            )
                        )

                """list_of_path.append("curationoftechnologies")
                list_of_path.append("APICrops")
    
                if request.matched_route.name not in list_of_path:
                    completed, results = getTechnologiesByUserWithoutCropTaxonomy(
                        login, request
                    )
                    if not completed:
                        raise HTTPFound(
                            location=request.route_url("curationoftechnologies")
                        )
    
                list_of_path.append("curationofprojects")
                list_of_path.append("getunitofanalysisbylocation")
                list_of_path.append("getobjectivesbylocationandunitofanalysis")
                list_of_path.append("searchaffiliation")
    
                if request.matched_route.name not in list_of_path:
    
                    completed, projects = getProjectsByUserThatRequireSetup(login, request)
    
                    if not completed:
                        raise HTTPFound(location=request.route_url("curationofprojects"))"""
