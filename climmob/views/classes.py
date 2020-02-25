from pyramid.security import authenticated_userid
from ..config.auth import getUserData, getUserByApiKey
from pyramid.httpexceptions import HTTPFound

# import climmob.resources as r
from pyramid.session import check_csrf_token
from pyramid.httpexceptions import HTTPNotFound
from formencode.variabledecode import variable_decode
from pyramid.response import Response
from hashlib import md5
import uuid
import logging

log = logging.getLogger(__name__)

from ..processes import getUserProjects, getActiveProject

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
        self.request = request
        self._ = self.request.translate

    def __call__(self):
        # self.injectResources()
        return self.processView()

    """
    def needCSS(self,name):
        CSSToInject = r.getCSSResource(name)
        CSSToInject.need()

    def needJS(self,name):
        JSToInject = r.getJSResource(name)
        JSToInject.need()

    def injectResources(self):
        CSSToInject = r.getCSSResource('style')
        CSSToInject.need()
        JSToInject = r.getJSResource('bootstrap')
        JSToInject.need()
    """

    def processView(self):
        # print("retorna")
        return {}

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


class privateView(object):
    def __init__(self, request):
        self.request = request
        self.user = None
        self._ = self.request.translate
        self.checkCrossPost = False
        self.classResult = {
            "activeUser": None,
            "hasActiveProject": None,
            "userProjects": [],
        }
        self.viewResult = {}
        self.returnRawViewResult = False

    """
    def needCSS(self,name):
        CSSToInject = r.getCSSResource(name)
        CSSToInject.need()

    def needJS(self,name):
        JSToInject = r.getJSResource(name)
        JSToInject.need()
    
    def injectResources(self):
        CSSToInject = r.getCSSResource('style')
        CSSToInject.need()
        JSToInject = r.getJSResource('pace')
        JSToInject.need()
    """

    def __call__(self):
        login = authenticated_userid(self.request)
        self.user = getUserData(login, self.request)
        self.classResult["activeUser"] = self.user

        if self.user == None:
            return HTTPFound(location=self.request.route_url("login"))

        self.classResult["userProjects"] = getUserProjects(
            self.user.login, self.request
        )
        activeProjectData = getActiveProject(self.user.login, self.request)
        if activeProjectData:
            self.classResult["hasActiveProject"] = True
        else:
            self.classResult["hasActiveProject"] = False

        # self.injectResources()
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

        # return self.processView()
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

            if self.request.method == "POST":
                try:
                    self.body = self.request.params["Body"]
                except:
                    response = Response(
                        status=401, body=self.request.translate("Error in the JSON, It does not have the 'body' parameter.")
                    )
                    return response

        except:
            response = Response(
                status=401, body=self.request.translate("Apikey non-existent")
            )
            return response

        return self.processView()

    def processView(self):

        return {}
