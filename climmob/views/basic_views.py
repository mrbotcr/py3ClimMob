import datetime
import smtplib
import logging
from email import utils
from email.header import Header
from email.mime.text import MIMEText
from time import time
from ast import literal_eval
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember
from climmob.config.encdecdata import encodeData
from climmob.config.auth import (
    getUserData,
    getUserByEmail,
    setPasswordResetToken,
    resetKeyExists,
    resetPassword,
)
from climmob.processes import (
    addUser,
    addToLog,
    getCountryList,
    getSectorList,
    getUserCount,
    getProjectCount,
)
from climmob.utility import valideRegisterForm
from climmob.views.classes import publicView
from pyramid.session import check_csrf_token
import secrets
import uuid

from jinja2 import ext
from climmob.config.jinja_extensions import jinjaEnv, extendThis
from climmob.utility.helpers import readble_date

log = logging.getLogger("climmob")


def render_template(template_filename, context):
    return jinjaEnv.get_template(template_filename).render(context)


class home_view(publicView):
    def processView(self):
        cookies = self.request.cookies
        if "climmob_cookie_question" in cookies.keys():
            ask_for_cookies = False
        else:
            ask_for_cookies = True
        return {
            "numUsers": getUserCount(self.request),
            "numProjs": getProjectCount(self.request),
            "ask_for_cookies": ask_for_cookies,
        }


class HealthView(publicView):
    def processView(self):
        engine = self.request.dbsession.get_bind()
        try:
            res = self.request.dbsession.execute(
                "show status like 'Threads_connected%'"
            ).fetchone()
            threads_connected = res[1]
        except Exception as e:
            threads_connected = str(e)
        return {
            "health": {
                "pool": engine.pool.status(),
                "threads_connected": threads_connected,
            }
        }


class TermsView(publicView):
    def processView(self):
        return {}


class PrivacyView(publicView):
    def processView(self):
        return {}


class notfound_view(publicView):
    def processView(self):
        self.request.response.status = 404
        return {}


class StoreCookieView(publicView):
    def processView(self):
        if self.request.method == "GET":
            raise HTTPNotFound()
        else:
            next_url = self.request.params.get("next") or self.request.route_url("home")
            response = HTTPFound(location=next_url)
            if "accept" in self.request.POST:
                response.set_cookie(
                    "climmob_cookie_question", "accept", max_age=31536000
                )
            return response


def get_policy(request, policy_name):
    policies = request.policies()
    for policy in policies:
        if policy["name"] == policy_name:
            return policy["policy"]
    return None


class login_view(publicView):
    def processView(self):

        cookies = self.request.cookies
        if "climmob_cookie_question" in cookies.keys():
            ask_for_cookies = False
        else:
            ask_for_cookies = True

        # If we logged in then go to dashboard
        policy = get_policy(self.request, "main")
        login_data = policy.authenticated_userid(self.request)
        if login_data:
            login_data = literal_eval(login_data)
            if login_data["group"] == "mainApp":
                currentUser = getUserData(login_data["login"], self.request)
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
                login_data = {"login": login, "group": "mainApp"}
                headers = remember(self.request, str(login_data), policies=["main"])
                response = HTTPFound(location=next, headers=headers)
                return response
            did_fail = True

        return {
            "login": login,
            "failed_attempt": did_fail,
            "next": next,
            "ask_for_cookies": ask_for_cookies,
        }


class RecoverPasswordView(publicView):
    def send_password_by_email(self, body, target_name, target_email, mail_from):
        msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
        ssubject = self._("ClimMob - Password reset request")
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

    def send_password_email(self, email_to, reset_token, reset_key, user_dict):
        jinjaEnv.add_extension(ext.i18n)
        jinjaEnv.add_extension(extendThis)
        _ = self.request.translate
        email_from = self.request.registry.settings.get("email.from", None)
        if email_from is None:
            log.error(
                "ClimMob has no email settings in place. Email service is disabled."
            )
            return False
        if email_from == "":
            return False
        date_string = readble_date(datetime.datetime.now(), self.request.locale_name)
        reset_url = self.request.route_url("reset_password", reset_key=reset_key)
        text = render_template(
            "email/recover_email.jinja2",
            {
                "recovery_date": date_string,
                "reset_token": reset_token,
                "user_dict": user_dict,
                "reset_url": reset_url,
                "_": _,
            },
        )

        self.send_password_by_email(text, user_dict.fullName, email_to, email_from)

    def processView(self):

        # If we logged in then go to dashboard
        policy = get_policy(self.request, "main")
        login = policy.authenticated_userid(self.request)
        currentUser = getUserData(login, self.request)
        if currentUser is not None:
            raise HTTPNotFound()

        error_summary = {}
        if "submit" in self.request.POST:
            email = self.request.POST.get("user_email", None)
            if email is not None:
                user, password = getUserByEmail(email, self.request)
                if user is not None:

                    reset_key = str(uuid.uuid4())
                    reset_token = secrets.token_hex(16)
                    setPasswordResetToken(
                        self.request, user.login, reset_key, reset_token
                    )
                    self.send_password_email(user.email, reset_token, reset_key, user)
                    self.returnRawViewResult = True
                    return HTTPFound(location=self.request.route_url("login"))
                else:
                    error_summary["email"] = self._(
                        "Cannot find an user with such email address"
                    )
            else:
                error_summary["email"] = self._("You need to provide an email address")

        return {"error_summary": error_summary}


class ResetPasswordView(publicView):
    def processView(self):
        error_summary = {}
        dataworking = {}

        reset_key = self.request.matchdict["reset_key"]

        if not resetKeyExists(self.request, reset_key):
            raise HTTPNotFound()

        if self.request.method == "POST":

            safe = check_csrf_token(self.request, raises=False)
            if not safe:
                raise HTTPNotFound()

            dataworking = self.getPostDict()
            login = dataworking["user"]
            token = dataworking["token"]
            new_password = dataworking["password"].strip()
            new_password2 = dataworking["password2"].strip()
            user = dataworking["user"]
            if user != "":
                log.error(
                    "Suspicious bot password recovery from IP: {}. Agent: {}. Email: {}".format(
                        self.request.remote_addr,
                        self.request.user_agent,
                        dataworking["email"],
                    )
                )
            user = getUserData(login, self.request)

            if user is not None:
                if user.userData["user_password_reset_key"] == reset_key:
                    if user.userData["user_password_reset_token"] == token:
                        if (
                            user.userData["user_password_reset_expires_on"]
                            > datetime.datetime.now()
                        ):
                            if new_password != "":
                                if new_password == new_password2:
                                    new_password = encodeData(
                                        self.request, new_password
                                    )
                                    resetPassword(
                                        self.request,
                                        user.userData["user_name"],
                                        reset_key,
                                        token,
                                        new_password,
                                    )
                                    self.returnRawViewResult = True
                                    return HTTPFound(
                                        location=self.request.route_url("login")
                                    )
                                else:
                                    error_summary = {
                                        "Error": self._(
                                            "The password and the confirmation are not the same"
                                        )
                                    }
                            else:
                                error_summary = {
                                    "Error": self._("The password cannot be empty")
                                }
                        else:
                            error_summary = {"Error": self._("Invalid token")}
                    else:
                        error_summary = {"Error": self._("Invalid token")}
                else:
                    error_summary = {"Error": self._("Invalid key")}
            else:
                error_summary = {"Error": self._("User does not exist")}

        return {"error_summary": error_summary, "dataworking": dataworking}


def logout_view(request):
    policy = get_policy(request, "main")
    headers = policy.forget(request)
    loc = request.route_url("home")
    return HTTPFound(location=loc, headers=headers)


class register_view(publicView):
    def processView(self):
        if (
            self.request.registry.settings.get("auth.register_users_via_web", "true")
            == "false"
        ):
            raise HTTPNotFound()

        # If we logged in then go to dashboard
        policy = get_policy(self.request, "main")
        login_data = policy.authenticated_userid(self.request)
        if login_data is not None:
            login_data = literal_eval(login_data)
            if login_data["group"] == "mainApp":
                currentUser = getUserData(login_data["login"], self.request)
                if currentUser is not None:
                    self.returnRawViewResult = True
                    return HTTPFound(location=self.request.route_url("dashboard"))

        data = {}
        error_summary = {}

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
            if "user_policy" in data.keys():
                data["user_policy"] = "True"
            else:
                data["user_policy"] = "False"

            errors, error_summary = valideRegisterForm(data, self.request, self._)
            if not errors:
                res, message = addUser(data, self.request)
                # print("res ---->" + str(res))
                # print("message ---->" +str(message))

                if res:
                    user = getUserData(data["user_name"], self.request)
                    if user is not None:
                        if user.check_password(data["user_password"], self.request):
                            addToLog(
                                user.login,
                                "PRF",
                                "Welcome to ClimMob",
                                datetime.datetime.now(),
                                self.request,
                            )
                            login_data = {
                                "login": data["user_name"],
                                "group": "mainApp",
                            }
                            headers = remember(
                                self.request, str(login_data), policies=["main"]
                            )
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
