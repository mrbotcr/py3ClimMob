import os
import io
import json
import uuid
import logging
import datetime
from hashlib import md5
import climmob.plugins as p
from ast import literal_eval
from pyramid.response import Response
from pyramid.session import check_csrf_token
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from formencode.variabledecode import variable_decode
from climmob.config.auth import getUserData, getUserByApiKey

log = logging.getLogger(__name__)

from climmob.processes import (
    getActiveProject,
    counterChat,
    getLastActivityLogByUser,
    addToLog,
    update_last_login,
    getActiveForm,
)


def resource_callback(request, response):
    """
    This function moves all script code in a html to an ephemeral js file.
    This is important to deny any inline JS as part of Content-Security-Policy while
    keeping the flexibility of having scripts in the jinja2 templates
    """
    if response.content_type == "text/html":
        js_file_id = str(uuid.uuid4())
        paths = ["static", "ephemeral", js_file_id + ".js"]
        repo_dir = request.registry.settings["apppath"]
        js_file = os.path.join(repo_dir, *paths)

        html_content = ""
        js_content = ""
        in_html = True

        f = io.StringIO(response.body.decode())
        lines = f.readlines()
        f.close()
        for a_line in lines:
            ignore_line = False
            a_line = a_line.strip()
            if a_line.find("<script>") >= 0:
                in_html = False
                ignore_line = True
            if a_line.find("</script>") >= 0:
                in_html = True
                ignore_line = True
            if a_line.find("<script ") >= 0:
                ignore_line = False
            if a_line.find("</body>") >= 0:
                a_line = (
                    '<script src="'
                    + request.application_url
                    + "/static/ephemeral/"
                    + js_file_id
                    + ".js"
                    + '"></script>\n'
                    + a_line
                )
            if not ignore_line:
                if in_html:
                    if a_line != "":
                        html_content = html_content + a_line + "\n"
                else:
                    if a_line != "":
                        js_content = js_content + a_line + "\n"

        with open(js_file, "w") as jf:
            if not js_content:
                jf.write("console.log('');")
            else:
                jf.write(js_content)
        response.body = html_content.encode()


# ODKView is a Digest Authorization view. It automates all the Digest work
class odkView(object):
    def __init__(self, request):
        self.request = request
        self._ = self.request.translate
        self.nonce = md5(str(uuid.uuid4()).encode()).hexdigest()
        self.opaque = request.registry.settings["auth.opaque"]
        self.realm = request.registry.settings["auth.realm"]
        self.authHeader = {}
        self.user = ""

    def getAuthDict(self):
        authheader = self.request.headers["Authorization"].replace(", ", ",")
        authheader = authheader.replace('"', "")
        autharray = authheader.split(",")
        for e in autharray:
            t = e.split("=")
            if len(t) == 2:
                self.authHeader[t[0]] = t[1]
            else:
                self.authHeader[t[0]] = t[1] + "=" + t[2]
        # pprint.pprint(self.authHeader)

    def authorize(self, correctPassword):
        # print "***********************77"
        # print self.request.method
        # pprint.pprint(self.authHeader)
        # print "***********************77"
        ha1 = ""
        ha2 = ""
        if self.authHeader["qop"] == "auth":
            ha1 = md5(
                (self.user + ":" + self.realm + ":" + correctPassword.decode()).encode()
            )
            ha2 = md5((self.request.method + ":" + self.authHeader["uri"]).encode())
        if self.authHeader["qop"] == "auth-int":
            ha1 = md5(
                (self.user + ":" + self.realm + ":" + correctPassword.decode()).encode()
            )
            md5_body = md5(self.request.body).hexdigest()
            ha2 = md5(
                (
                    self.request.method + ":" + self.authHeader["uri"] + ":" + md5_body
                ).encode()
            )
        if ha1 == "":
            ha1 = md5(
                (self.user + ":" + self.realm + ":" + correctPassword.decode()).encode()
            )
            ha2 = md5(self.request.method + ":" + self.authHeader["uri"])

        authLine = ":".join(
            [
                ha1.hexdigest(),
                self.authHeader["nonce"],
                self.authHeader["nc"],
                self.authHeader["cnonce"],
                self.authHeader["qop"],
                ha2.hexdigest(),
            ]
        )

        resp = md5(authLine.encode())
        if resp.hexdigest() == self.authHeader["response"]:
            # print "******************66"
            # print "Si esta entrando"
            # print "******************66"
            return True
        else:
            # print "*********************88"
            # print "Calculated response: " + resp.hexdigest()
            # print "Header response: " + self.authHeader["response"]
            # print "*********************88"
            return False

    def askForCredentials(self):
        headers = [
            (
                "WWW-Authenticate",
                'Digest realm="'
                + self.realm
                + '",qop="auth,auth-int",nonce="'
                + self.nonce
                + '",opaque="'
                + self.opaque
                + '"',
            )
        ]
        reponse = Response(status=401, headerlist=headers)
        return reponse

    def createXMLResponse(self, XMLData):
        headers = [
            ("Content-Type", "text/xml; charset=utf-8"),
            ("X-OpenRosa-Accept-Content-Length", "10000000"),
            ("Content-Language", self.request.locale_name),
            ("Vary", "Accept-Language,Cookie,Accept-Encoding"),
            ("X-OpenRosa-Version", "1.0"),
            ("Allow", "GET, HEAD, OPTIONS"),
        ]
        response = Response(headerlist=headers, status=200)
        response.text = str(XMLData, "utf-8")
        return response

    def __call__(self):
        if "Authorization" in self.request.headers:
            if self.request.headers["Authorization"].find("Basic ") == -1:
                self.getAuthDict()
                self.user = self.authHeader["Digest username"]
                return self.processView()
            else:
                headers = [
                    (
                        "WWW-Authenticate",
                        'Digest realm="'
                        + self.realm
                        + '",qop="auth,auth-int",nonce="'
                        + self.nonce
                        + '",opaque="'
                        + self.opaque
                        + '"',
                    )
                ]
                reponse = Response(status=401, headerlist=headers)
                return reponse
        else:
            headers = [
                (
                    "WWW-Authenticate",
                    'Digest realm="'
                    + self.realm
                    + '",qop="auth,auth-int",nonce="'
                    + self.nonce
                    + '",opaque="'
                    + self.opaque
                    + '"',
                )
            ]
            reponse = Response(status=401, headerlist=headers)
            return reponse

    def processView(self):
        # At this point children of odkView have:
        # self.user which us the user requesting ODK data
        # authorize(self,correctPassword) which checks if the password in the authorization is correct
        # askForCredentials(self) which return a response to ask again for the credentials
        # createXMLResponse(self,XMLData) that can be used to return XML data to ODK with the required headers
        return {}


# This is the most basic public view. Used for 404 and 500. But then used for others more advanced classes
class publicView(object):
    def __init__(self, request):
        if request.registry.settings.get("secure.javascript", "false") == "true":
            request.add_response_callback(resource_callback)
        self.request = request
        self._ = self.request.translate

    def __call__(self):
        return self.processView()

    def processView(self):
        return {}

    def getPostDict(self):
        dct = variable_decode(self.request.POST)

        return dct

    def decodeDict(self, dct):
        for key, value in dct.items():
            if isinstance(value, str):
                try:
                    dct[key] = value.decode("utf8")
                except:
                    pass
            if isinstance(value, str):
                try:
                    dct[key] = value.decode("utf8")
                except:
                    pass
        return dct


class privateView(object):
    def __init__(self, request):
        if request.registry.settings.get("secure.javascript", "false") == "true":
            request.add_response_callback(resource_callback)
        self.request = request
        self.user = None
        self._ = self.request.translate
        self.checkCrossPost = False
        self.classResult = {
            "activeUser": None,
            "hasActiveProject": None,
            "activeProject": None,
            "counterChat": 0,
            "showHelp": False,
            "showRememberAfterCreateProject": False,
            "surveyMustBeDisplayed": None,
        }

        self.viewResult = {}
        self.returnRawViewResult = False

    def __call__(self):
        policy = self.get_policy("main")
        login_data = policy.authenticated_userid(self.request)
        if login_data is not None:
            login_data = literal_eval(login_data)
            if login_data["group"] == "mainApp":
                self.user = getUserData(login_data["login"], self.request)
                self.classResult["activeUser"] = self.user
                if self.user == None:
                    return HTTPFound(location=self.request.route_url("login"))
            else:
                return HTTPFound(location=self.request.route_url("login"))
        else:
            return HTTPFound(location=self.request.route_url("login"))

        lastActivity = getLastActivityLogByUser(self.user.login, self.request)
        if lastActivity["log_message"] != "Welcome to ClimMob":
            if (
                self.request.matched_route.name
                not in ["profile", "getUserLanguagesPreview", "addUserLanguage"]
                and not self.user.languages
            ):
                return HTTPFound(
                    location=self.request.route_url(
                        "profile", _query={"help": "languages"}
                    )
                )

            if (
                self.request.matched_route.name
                not in [
                    "curationoftechnologies",
                    "profile",
                    "getUserLanguagesPreview",
                    "addUserLanguage",
                ]
                and not self.user.technologies
            ):
                return HTTPFound(
                    location=self.request.route_url("curationoftechnologies")
                )

        self.classResult["counterChat"] = counterChat(self.user.login, self.request)
        activeProjectData = getActiveProject(self.user.login, self.request)
        if activeProjectData:
            self.classResult["hasActiveProject"] = True
            self.classResult["activeProject"] = activeProjectData["project_id"]
        else:
            self.classResult["hasActiveProject"] = False

        hasActiveForm, formDetails = getActiveForm(self.request, self.user.login)

        if hasActiveForm:
            self.classResult["surveyMustBeDisplayed"] = formDetails["form_name"]

        if lastActivity:
            if lastActivity["log_message"] == "Created a new project":
                self.classResult["showRememberAfterCreateProject"] = True
                addToLog(
                    self.user.login,
                    "PRF",
                    "Dashboard",
                    lastActivity["log_datetime"] + datetime.timedelta(0, 3),
                    self.request,
                )

            if lastActivity["log_message"] == "Welcome to ClimMob":
                self.classResult["showHelp"] = True
                addToLog(
                    self.user.login,
                    "PRF",
                    "Dashboard",
                    lastActivity["log_datetime"] + datetime.timedelta(0, 3),
                    self.request,
                )

        if (
            self.request.method == "POST"
            or self.request.method == "PUT"
            or self.request.method == "DELETE"
        ):
            safe = check_csrf_token(self.request, raises=False)
            if not safe:
                self.request.session.pop_flash()
                log.error("SECURITY-CSRF error at {} ".format(self.request.url))
                raise HTTPNotFound()
            else:
                if self.checkCrossPost:
                    if self.request.referer != self.request.url:
                        self.request.session.pop_flash()
                        log.error(
                            "SECURITY-CrossPost error. Posting at {} from {} ".format(
                                self.request.url, self.request.referer
                            )
                        )
                        raise HTTPNotFound()

        update_last_login(self.request, self.user.login)

        for plugin in p.PluginImplementations(p.IUserFlow):
            try:
                plugin.register_user_flow(self.user, self.request)
            except:
                pass

        self.viewResult = self.processView()

        if not self.returnRawViewResult:
            self.classResult.update(self.viewResult)
            return self.classResult
        else:
            return self.viewResult

    def processView(self):
        return {"activeUser": self.user}

    def getPostDict(self):
        dct = variable_decode(self.request.POST)
        """
        for key,value in dct.items():
            if isinstance(value, str):
                dct[key] = value.encode("utf8")
            if isinstance(value, str):
                dct[key] = value.encode("utf8")
        """
        return dct

    def decodeDict(self, dct):
        for key, value in dct.items():
            if isinstance(value, str):
                try:
                    dct[key] = value.decode("utf8")
                except:
                    pass
            if isinstance(value, str):
                try:
                    dct[key] = value.decode("utf8")
                except:
                    pass
        return dct

    def get_policy(self, policy_name):
        policies = self.request.policies()
        for policy in policies:
            if policy["name"] == policy_name:
                return policy["policy"]
        return None


class apiView(object):
    def __init__(self, request):
        self.request = request
        self.user = None
        self.body = None
        self._ = self.request.translate

    def __call__(self):

        try:
            apiKey = self.request.params["Apikey"]
            self.apiKey = apiKey
            self.user = getUserByApiKey(apiKey, self.request)

            if self.user == None:
                response = Response(
                    status=401,
                    body=self.request.translate(
                        "This Apikey does not exist or is inactive."
                    ),
                )
                return response

            try:
                self.body = self.request.params["Body"]
            except:
                body = {}
                for va in self.request.params:
                    if va != "Apikey":
                        body[va] = self.request.params[va]

                self.body = json.dumps(body)

            update_last_login(self.request, self.user.login)
        except:
            response = Response(
                status=401, body=self.request.translate("Apikey non-existent")
            )
            return response

        return self.processView()

    def processView(self):

        return {}
