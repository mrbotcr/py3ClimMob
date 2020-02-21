from ..models import User as userModel, Country, Sector
from .encdecdata import decodeData
from ..models import mapFromSchema

import urllib, hashlib, arrow


# User class Used to store information about the user
class User(object):
    def __init__(self, userData, groups=None):

        # print(userData)
        default = "identicon"
        size = 45
        self.email = userData["user_email"]
        gravatar_url = (
            "http://www.gravatar.com/avatar/"
            + hashlib.md5(self.email.lower().encode("utf8")).hexdigest()
            + "?"
        )
        gravatar_url += urllib.parse.urlencode({"d": default, "s": str(size)})

        self.userData = userData
        self.login = userData["user_name"]
        self.password = ""
        self.groups = groups or []
        self.fullName = userData["user_fullname"]
        self.organization = userData["user_organization"]

        self.country = userData["user_cnty"]
        self.sector = str(userData["user_sector"])
        self.gravatarURL = gravatar_url
        if userData["user_about"] is None:
            self.about = ""
        else:
            self.about = userData["user_about"]

    def check_password(self, passwd, request):
        return checkLogin(self.login, passwd, request)

    def getGravatarUrl(self, size):
        default = "identicon"
        gravatar_url = (
            "http://www.gravatar.com/avatar/"
            + hashlib.md5(self.email.lower().encode("utf8")).hexdigest()
            + "?"
        )
        gravatar_url += urllib.parse.urlencode({"d": default, "s": str(size)})
        # gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?"
        # gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
        return gravatar_url

    def getCntyName(self, request):
        return getCountryName(self.country, request)

    def getSectName(self, request):
        return getSectorName(self.sector, request)

    def getAPIKey(self, request):
        key = ""
        result = (
            request.dbsession.query(userModel).filter_by(user_name=self.login).first()
        )
        if not result is None:
            key = result.user_apikey
        return key

    def getJoinDate(self, request):
        result = (
            request.dbsession.query(userModel).filter_by(user_name=self.login).first()
        )
        ar = arrow.get(result.user_joindate)
        joindate = ar.format("dddd Do of MMMM, YYYY")
        return joindate

    def updateGravatarURL(self):
        default = "identicon"
        size = 45
        gravatar_url = (
            "http://www.gravatar.com/avatar/"
            + hashlib.md5(self.email.lower().encode("utf8")).hexdigest()
            + "?"
        )
        gravatar_url += urllib.parse.urlencode({"d": default, "s": str(size)})
        self.gravatarURL = gravatar_url


def getUserData(user, request):
    res = None
    result = (
        request.dbsession.query(userModel)
        .filter_by(user_name=user)
        .filter_by(user_active=1)
        .first()
    )
    if not result is None:
        res = User(mapFromSchema(result))

    return res


def getUserByApiKey(apiKey, request):
    res = None
    result = (
        request.dbsession.query(userModel)
        .filter_by(user_apikey=apiKey)
        .filter_by(user_active=1)
        .first()
    )
    if not result is None:
        res = User(mapFromSchema(result))

    return res


def getUserByEmail(email, request):
    result = (
        request.dbsession.query(userModel)
        .filter_by(user_email=email)
        .filter_by(user_active=1)
        .first()
    )
    if result is not None:
        return User(mapFromSchema(result)), decodeData(request, result.user_password).decode(
            "utf-8"
        )
    return None, None


def checkLogin(user, password, request):
    result = (
        request.dbsession.query(userModel)
        .filter_by(user_name=user)
        .filter_by(user_active=1)
        .first()
    )
    if result is None:
        return False
    else:
        cpass = decodeData(request, result.user_password)
        if cpass == bytearray(password.encode()):
            return True
        else:
            return False


def getCountryName(cnty_cod, request):
    res = ""
    result = request.dbsession.query(Country).filter_by(cnty_cod=cnty_cod).first()
    if not result is None:
        res = result.cnty_name
    return res


def getSectorName(sector_cod, request):
    res = ""
    result = request.dbsession.query(Sector).filter_by(sector_cod=sector_cod).first()
    if not result is None:
        res = result.sector_name
    return res
