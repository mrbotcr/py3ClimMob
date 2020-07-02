from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from ..config.auth import getUserData, getUserByEmail
from .classes import publicView
from ..utility import valideRegisterForm
from ..processes import (
    addUser,
    addToLog,
    getCountryList,
    getSectorList,
    getUserCount,
    getProjectCount,
)
from pyramid.security import authenticated_userid
from pyramid.security import forget
import re
from email.mime.text import MIMEText
from email.header import Header
from email import utils
from time import time
import smtplib


class home_view(publicView):
    def processView(self):
        # self.needJS("landing")
        # self.needCSS("landing")
        return {
            "numUsers": getUserCount(self.request),
            "numProjs": getProjectCount(self.request),
        }


class notfound_view(publicView):
    def processView(self):
        self.request.response.status = 404
        return {}


class login_view(publicView):
    def processView(self):

        # If we logged in then go to dashboard
        login = authenticated_userid(self.request)
        currentUser = getUserData(login, self.request)
        if currentUser is not None:
            self.returnRawViewResult = True
            return HTTPFound(location=self.request.route_url("dashboard"))

        next = self.request.params.get("next") or self.request.route_url("dashboard")
        login = ""
        did_fail = False
        if "submit" in self.request.POST:
            login = self.request.POST.get("login", "")
            passwd = self.request.POST.get("passwd", "")
            user = getUserData(login, self.request)
            if not user == None and user.check_password(passwd, self.request):
                headers = remember(self.request, login)
                response = HTTPFound(location=next, headers=headers)
                return response
            did_fail = True

        return {"login": login, "failed_attempt": did_fail, "next": next}


class RecoverPasswordView(publicView):
    def send_password_by_emial(self, body, target_name, target_email):
        mail_from = self.request.registry.settings.get("email.from")
        msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
        ssubject = self._("ClimMob Version 3 - Password recovery")
        subject = Header(ssubject.encode("utf-8"), "utf-8")
        msg["Subject"] = subject
        msg["From"] = "{} <{}>".format("ClimMob", mail_from)
        recipient = "{} <{}>".format(target_name.encode("utf-8"), target_email)
        msg["To"] = Header(recipient, "utf-8")
        msg["Date"] = utils.formatdate(time())
        try:
            smtp_server = self.request.registry.settings.get(
                "email.server", "localhost"
            )
            smtp_user = self.request.registry.settings.get("email.user")
            smtp_password = self.request.registry.settings.get("email.password")

            server = smtplib.SMTP(smtp_server, 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(mail_from, [target_email], msg.as_string())
            server.quit()

        except Exception as e:
            print(str(e))

    def processView(self):

        # If we logged in then go to dashboard
        login = authenticated_userid(self.request)
        currentUser = getUserData(login, self.request)
        if currentUser is not None:
            raise HTTPNotFound()
        error_summary = {}
        if "submit" in self.request.POST:
            email = self.request.POST.get("user_email", None)
            if email is not None:
                user, password = getUserByEmail(email, self.request)
                if user is not None:
                    message = self._("Hello, \n\n")
                    message = message + self._(
                        "You requested ClimMob Version 3 to send you your password.\n\n"
                    )
                    message = message + self._("Your account is: {} \n").format(
                        user.login
                    )
                    message = message + self._("Your password is: {} \n\n").format(
                        password
                    )
                    message = message + self._("Regards,\n")
                    message = message + self._("The ClimMob team.\n")
                    self.send_password_by_emial(message, user.fullName, email)
                    response = HTTPFound(location=self.request.route_url("home"))
                    return response
                else:
                    error_summary["email"] = self._(
                        "Cannot find an user with such email address"
                    )
            else:
                error_summary["email"] = self._("You need submit an email")

        return {"error_summary": error_summary}


def logout_view(request):
    headers = forget(request)
    loc = request.route_url("home")
    return HTTPFound(location=loc, headers=headers)


class register_view(publicView):
    def processView(self):

        # If we logged in then go to dashboard
        login = authenticated_userid(self.request)
        currentUser = getUserData(login, self.request)
        if currentUser is not None:
            self.returnRawViewResult = True
            return HTTPFound(location=self.request.route_url("dashboard"))

        data = {}
        error_summary = {}
        # self.needJS('register')
        # self.needCSS('select2')
        # self.needJS("icheck")
        # self.needCSS("icheck")

        data["user_name"] = ""
        data["user_fullname"] = ""
        data["user_password"] = ""
        data["user_organization"] = ""
        data["user_email"] = ""
        data["user_cnty"] = ""
        data["user_sector"] = ""
        data["user_policy"] = "no"

        if "submit" in self.request.POST:
            errors = False
            data = self.getPostDict()
            # data["user_name"] = self.request.POST.get('user_name', '')
            # data["user_fullname"] = self.request.POST.get('user_fullname', '')
            # data["user_organization"] = self.request.POST.get('user_organization', '')
            # data["user_email"] = self.request.POST.get('user_email', '')
            # data["user_cnty"] = self.request.POST.get('user_cnty', '')
            # data["user_sector"] = self.request.POST.get('user_sector', '')
            if "user_policy" in data.keys():
                data["user_policy"] = "True"
            else:
                data["user_policy"] = "False"
            # data["user_password"] = self.request.POST.get('user_password', '')
            # data["user_password2"] = self.request.POST.get('user_password2', '')

            errors, error_summary = valideRegisterForm(data, self.request)
            if not errors:
                res, message = addUser(data, self.request)
                # print("res ---->" + str(res))
                # print("message ---->" +str(message))

                if res:
                    user = getUserData(data["user_name"], self.request)
                    if user is not None:
                        reg = re.compile(r"^[a-z0-9]+$")
                        if reg.match(data["user_name"]):
                            if user.check_password(data["user_password"], self.request):
                                addToLog(
                                    user.login,
                                    "PRF",
                                    self._("Welcome to Climmob"),
                                    self.request,
                                )
                                headers = remember(self.request, data["user_name"])
                                self.returnRawViewResult = True
                                return HTTPFound(
                                    location=self.request.route_url("dashboard"),
                                    headers=headers,
                                )
                            else:
                                error_summary["createError"] = self._(
                                    "Password does not match {}".format(
                                        data["user_password"]
                                    )
                                )
                        else:
                            error_summary["createError"] = self._(
                                "The account name cannot have any characters."
                            )
                    else:
                        error_summary["createError"] = self._("User is None!")
                else:
                    error_summary["createError"] = self._(
                        "Unable to create user",
                        default="Unable to create user: ${user}",
                        mapping={"user": message},
                    )

        # return {'data': self.decodeDict(data), 'error_summary': error_summary,'countries':getCountryList(self.request),'sectors':getSectorList(self.request)}
        return {
            "data": data,
            "error_summary": error_summary,
            "countries": getCountryList(self.request),
            "sectors": getSectorList(self.request),
        }
