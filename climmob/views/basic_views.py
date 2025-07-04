import datetime
import json
import logging
import secrets
import smtplib
import uuid

from jinja2 import ext
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.security import remember
from pyramid.session import check_csrf_token

from climmob.config.auth import (
    getUserData,
    getUserByEmail,
    setPasswordResetToken,
    resetKeyExists,
    resetPassword,
)
from climmob.config.encdecdata import encodeData
from climmob.config.jinja_extensions import jinjaEnv, extendThis
from climmob.processes import (
    add_user,
    addToLog,
    getCountryList,
    getSectorList,
    getUserCount,
    getProjectCount,
)
from climmob.utility import validate_register_form
from climmob.utility.email import build_email_message
from climmob.utility.helpers import readble_date
from climmob.views.classes import publicView
from climmob.views.validators.session import NotLoggedInValidator

log = logging.getLogger("climmob")


def render_template(template_filename, context):
    return jinjaEnv.get_template(template_filename).render(context)


class RefreshSessionTokensView(publicView):
    def post(self):
        policies = self.request.policies()
        main_policy = None
        for policy in policies:
            if policy["name"] == "main":
                main_policy = policy["policy"]

        login_data = main_policy.authenticated_userid(self.request)

        response_body = {"msg": "Tokens refreshed"}

        if login_data is None:
            response_body["msg"] = "Authentication token expired"
            return Response(status="401", body=json.dumps(response_body))

        safe = check_csrf_token(self.request, raises=False)

        if not safe:
            response_body["msg"] = "Session token expired"
            return Response(status="401", body=json.dumps(response_body))

        return Response(status="200", body=json.dumps(response_body))


class HomeView(publicView):
    def get(self):
        cookies = self.request.cookies
        if "climmob_cookie_question" in cookies.keys():
            ask_for_cookies = False
        else:
            ask_for_cookies = True
        return {
            "user_count": getUserCount(self.request),
            "project_count": getProjectCount(self.request),
            "ask_for_cookies": ask_for_cookies,
        }


class HealthView(publicView):
    def get(self):
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
    def get(self):
        return {}


class PrivacyView(publicView):
    def get(self):
        return {}


class NotFoundView(publicView):
    def get(self):
        self.request.response.status = 404
        return {}


class StoreCookieView(publicView):
    def post(self):
        next_url = self.request.params.get("next") or self.request.route_url("home")
        response = HTTPFound(location=next_url)
        if "accept" in self.request.POST:
            response.set_cookie("climmob_cookie_question", "accept", max_age=31536000)
        return response


class LoginView(publicView):
    validators = (NotLoggedInValidator,)

    def get(self):
        is_cookie_set = self.is_cookie_question_set()

        next_page = self.request.params.get("next") or self.request.route_url(
            "dashboard"
        )
        login = ""
        did_fail = False

        return {
            "login": login,
            "failed_attempt": did_fail,
            "next": next_page,
            "ask_for_cookies": not is_cookie_set,
        }

    def post(self):
        is_cookie_set = self.is_cookie_question_set()

        next_page = self.request.params.get("next") or self.request.route_url(
            "dashboard"
        )

        login = self.request.POST.get("login", "")
        passwd = self.request.POST.get("passwd", "")
        user = getUserData(login, self.request)
        if user is not None and user.check_password(passwd, self.request):
            login_data = {"login": login, "group": "mainApp"}
            headers = remember(self.request, str(login_data), policies=["main"])
            response = HTTPFound(location=next_page, headers=headers)
            return response
        did_fail = True

        return {
            "login": login,
            "failed_attempt": did_fail,
            "next": next_page,
            "ask_for_cookies": not is_cookie_set,
        }

    def is_cookie_question_set(self):
        cookies = self.request.cookies
        return "climmob_cookie_question" in cookies.keys()


class RecoverPasswordView(publicView):
    validators = (NotLoggedInValidator,)

    def send_password_by_email(
        self, body, subject, target_name, target_email, mail_from
    ):
        msg = build_email_message(body, subject, target_name, target_email, mail_from)

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

        self.send_password_by_email(
            text,
            self._("ClimMob - Password reset request"),
            user_dict.fullName,
            email_to,
            email_from,
        )

    def get(self):
        return {}

    def post(self):
        error_summary = {}
        email = self.request.POST.get("user_email", None)

        if email is None:
            error_summary["email"] = self._("You need to provide an email address")
            return {"error_summary": error_summary}

        user, password = getUserByEmail(email, self.request)

        if user is None:
            error_summary["email"] = self._(
                "Cannot find an user with such email address"
            )
            return {"error_summary": error_summary}

        reset_key = str(uuid.uuid4())
        reset_token = secrets.token_hex(16)
        setPasswordResetToken(self.request, user.login, reset_key, reset_token)
        self.send_password_email(user.email, reset_token, reset_key, user)
        return HTTPFound(location=self.request.route_url("login"))


class ResetPasswordView(publicView):
    def get(self):
        reset_key = self.request.reset_key

        if not resetKeyExists(self.request, reset_key):
            raise HTTPNotFound()

        return {"error_summary": {}, "dataworking": {}}

    def post(self):
        reset_key = self.request.reset_key

        if not resetKeyExists(self.request, reset_key):
            raise HTTPNotFound()

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

        if user is None:
            error_summary = {"Error": self._("User does not exist")}
            return {"error_summary": error_summary, "dataworking": dataworking}

        if user.userData["user_password_reset_key"] != reset_key:
            error_summary = {"Error": self._("Invalid key")}
            return {"error_summary": error_summary, "dataworking": dataworking}

        if user.userData["user_password_reset_token"] != token:
            error_summary = {"Error": self._("Invalid token")}
            return {"error_summary": error_summary, "dataworking": dataworking}

        if user.userData["user_password_reset_expires_on"] < datetime.datetime.now():
            error_summary = {"Error": self._("Invalid token")}
            return {"error_summary": error_summary, "dataworking": dataworking}

        if new_password == "":
            error_summary = {"Error": self._("The password cannot be empty")}
            return {"error_summary": error_summary, "dataworking": dataworking}

        if new_password != new_password2:
            error_summary = {
                "Error": self._("The password and the confirmation are not the same")
            }
            return {"error_summary": error_summary, "dataworking": dataworking}

        new_password = encodeData(self.request, new_password)
        resetPassword(
            self.request,
            user.userData["user_name"],
            reset_key,
            token,
            new_password,
        )
        return HTTPFound(location=self.request.route_url("login"))


class LogoutView(publicView):
    def get(self):
        policy = self.get_policy("main")
        headers = policy.forget(self.request)
        loc = self.request.route_url("home")
        return HTTPFound(location=loc, headers=headers)


class RegisterView(publicView):
    validators = (NotLoggedInValidator,)

    def get(self):
        register_users_via_web = self.request.registry.settings.get(
            "auth.register_users_via_web", "true"
        )
        if register_users_via_web == "false":
            raise HTTPNotFound()
        return {
            "data": {},
            "error_summary": {},
            "countries": getCountryList(self.request),
            "sectors": getSectorList(self.request),
        }

    def post(self):
        data = self.getPostDict()
        if "user_policy" in data.keys():
            data["user_policy"] = "True"
        else:
            data["user_policy"] = "False"

        errors, error_summary = validate_register_form(data, self.request, self._)
        if not errors:
            res, message = add_user(data, self.request)
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
                        return HTTPFound(
                            location=self.request.route_url("dashboard"),
                            headers=headers,
                        )
                    else:
                        error_summary["createError"] = self._(
                            "Password does not match {}".format(data["user_password"])
                        )
                else:
                    error_summary["createError"] = self._("User is None!")
            else:
                error_summary["createError"] = self._(
                    "Unable to create user",
                    default="Unable to create user: ${user}",
                    mapping={"user": message},
                )

        return {
            "data": data,
            "error_summary": error_summary,
            "countries": getCountryList(self.request),
            "sectors": getSectorList(self.request),
        }
