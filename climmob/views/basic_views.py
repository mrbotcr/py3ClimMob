import re
from datetime import datetime
import json
import logging
import secrets
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
    userExists,
    emailExists,
)
from climmob.utility.email import build_email_message, EmailSender
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
        showMainPage = False
        if not showMainPage:
            return HTTPFound(location=self.request.route_url("login"))

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


class ForbiddenView(publicView):
    def __init__(self, context, request):
        super().__init__(request)
        self.context = context

    def get(self):
        self.request.response.status = 403
        return {"message": self.context.detail}


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
        email_sender = EmailSender(self.request.registry.settings)
        email_sender.send_email([target_email], msg)

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
        date_string = readble_date(datetime.now(), self.request.locale_name)
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

        # fmt: off
        errors = {
            user is None:
                self._("User does not exist"),
            user and user.userData["user_password_reset_key"] != reset_key:
                self._("Invalid key"),
            user and user.userData["user_password_reset_token"] != token:
                self._("Invalid token"),
            user and user.userData["user_password_reset_expires_on"] < datetime.now():
                self._("Invalid token"),
            user and new_password == "":
                self._("The password cannot be empty"),
            user and new_password != new_password2:
                self._("The password and the confirmation are not the same"),
        }
        # fmt: on

        for condition, message in errors.items():
            if condition:
                return {"error_summary": {"Error": message}, "dataworking": dataworking}

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

        response = {
            "data": data,
            "error_summary": {},
            "countries": getCountryList(self.request),
            "sectors": getSectorList(self.request),
        }
        errors, error_summary = self.validate_register_form(data)

        if errors:
            response["error_summary"] = error_summary
            return response

        res, message = add_user(data, self.request)

        if not res:
            response["error_summary"]["createError"] = self._(
                "Unable to create user",
                default="Unable to create user: ${user}",
                mapping={"user": message},
            )
            return response

        user = getUserData(data["user_name"], self.request)
        if user is None:
            response["error_summary"]["createError"] = self._("User is None!")
            return response

        if not user.check_password(data["user_password"], self.request):
            response["error_summary"]["createError"] = self._(
                "Password does not match {}".format(data["user_password"])
            )
            return response

        addToLog(
            user.login,
            "PRF",
            "Welcome to ClimMob",
            datetime.now(),
            self.request,
        )
        login_data = {
            "login": data["user_name"],
            "group": "mainApp",
        }
        headers = remember(self.request, str(login_data), policies=["main"])
        return HTTPFound(
            location=self.request.route_url("dashboard"),
            headers=headers,
        )

    # Create validator if needed by another view
    def validate_register_form(self, data):
        error_summary = {}
        errors = False

        if data["user_password"] != data["user_password2"]:
            error_summary["InvalidPassword"] = self._("Invalid password")
            errors = True
        if userExists(data["user_name"], self.request):
            error_summary["UserExists"] = self._("Username already exits")
            errors = True
        if emailExists(data["user_email"], self.request):
            error_summary["EmailExists"] = self._(
                "There is already an account using to this email"
            )
            errors = True
        if data["user_policy"] == "False":
            error_summary["CheckPolicy"] = self._(
                "You need to accept the terms of service"
            )
            errors = True
        if data["user_name"] == "":
            error_summary["EmptyUser"] = self._("User cannot be emtpy")
            errors = True
        if data["user_password"] == "":
            error_summary["EmptyPass"] = self._("Password cannot be emtpy")
            errors = True
        if data["user_fullname"] == "":
            error_summary["EmptyName"] = self._("Full name cannot be emtpy")
            errors = True
        if data["user_email"] == "":
            error_summary["EmptyEmail"] = self._("Email cannot be emtpy")
            errors = True
        reg = re.compile(r"^[a-z0-9]+$")
        if not reg.match(data["user_name"]):
            error_summary["Caracters"] = self._(
                "The username can only use lowercase letters and numbers."
            )
            errors = True

        return errors, error_summary
