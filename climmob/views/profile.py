import base64
import datetime
from io import BytesIO
from pyotp import TOTP

import pyotp
import qrcode

from climmob.config.auth import getUserData
from climmob.processes import (
    getUserLog,
    getUserStats,
    getCountryList,
    getSectorList,
    otherUserHasEmail,
    updateProfile,
    addToLog,
    getActiveProject,
    changeUserPassword,
    # getListOfUnusedLanguagesByUser,
)
from climmob.processes.db.one_time_code import (
    get_active_codes,
    delete_all_codes,
    create_one_time_codes,
)
from climmob.processes.db.user_secret import (
    update_user_secret,
    get_user_secret,
    create_user_secret,
)
from climmob.views.classes import privateView


class profile_view(privateView):
    def processView(self):

        try:
            help = self.request.params["help"]
        except:
            help = None

        limit = True
        if "all" in self.request.params:
            if self.request.params["all"] == "True":
                limit = False
        activities = getUserLog(self.user.login, self.request, limit)
        userstats = getUserStats(self.user.login, self.request)
        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "activities": activities,
            "userstats": userstats,
            # "listOfLanguages": getListOfUnusedLanguagesByUser(
            #    self.request, self.user.login
            # ),
            "help": help,
        }


class editProfile_view(privateView):
    def processView(self):
        userstats = getUserStats(self.user.login, self.request)
        error_summary = {}
        passChanged = False
        profileUpdated = False
        otp_qr_code = None
        one_time_codes = []

        if self.request.method == "POST":
            if "saveprofile" in self.request.POST:
                data = self.getPostDict()
                # print ("*****************77")
                # print (data)
                # print ("*****************77")
                if data["user_fullname"] != "":
                    if data["user_email"] != "":
                        if data["user_organization"] != "":
                            if not otherUserHasEmail(
                                self.user.login, data["user_email"], self.request
                            ):
                                updated, uerror = updateProfile(
                                    self.user.login, data, self.request
                                )
                                if updated:
                                    self.user.userData = data.copy()
                                    self.user.email = data["user_email"]
                                    self.user.organization = data["user_organization"]
                                    self.user.fullName = data["user_fullname"]
                                    self.user.country = data["user_cnty"]
                                    self.user.sector = data["user_sector"]
                                    self.user.about = data["user_about"]
                                    self.user.updateGravatarURL()
                                    addToLog(
                                        self.user.login,
                                        "PRF",
                                        "Updated profile",
                                        datetime.datetime.now(),
                                        self.request,
                                    )
                                    profileUpdated = True
                                else:
                                    error_summary["ChangeProfile"] = uerror
                            else:
                                error_summary["ChangeProfile"] = self._(
                                    "User with the same email address has already been registered."
                                )
                        else:
                            error_summary["ChangeProfile"] = self._(
                                "Organization cannot be empty"
                            )
                    else:
                        error_summary["ChangeProfile"] = self._("Email cannot be empty")
                else:
                    error_summary["ChangeProfile"] = self._("Full name cannot be empty")

            if "changepass" in self.request.POST:
                user = getUserData(self.user.login, self.request)

                if user.check_password(
                    self.request.POST.get("user_password1", ""), self.request
                ):
                    if self.request.POST.get("user_password2", "") != "":
                        if self.request.POST.get(
                            "user_password2", ""
                        ) == self.request.POST.get("user_password3", ""):
                            if changeUserPassword(
                                self.user.login,
                                self.request.POST.get("user_password2", ""),
                                self.request,
                            ):
                                addToLog(
                                    self.user.login,
                                    "PRF",
                                    "Changed password",
                                    datetime.datetime.now(),
                                    self.request,
                                )
                                passChanged = True
                            else:
                                error_summary["ChangePass"] = self._(
                                    "Cannot change password"
                                )
                        else:
                            error_summary["ChangePass"] = self._(
                                "New password and re-type are not equal"
                            )
                    else:
                        error_summary["ChangePass"] = self._(
                            "New password cannot be empty"
                        )
                else:
                    error_summary["ChangePass"] = self._(
                        "The current password is not valid"
                    )

            if "generate" in self.request.POST:
                two_fa_method = self.request.POST.get("two_fa_method")

                # Generar un nuevo secreto para cualquier método
                new_secret = pyotp.random_base32()
                secret_response = get_user_secret(self.request, self.user.login)

                if secret_response.get("success"):
                    # Actualizar el secreto y el método seleccionado
                    update_user_secret(
                        self.request,
                        self.user.login,
                        new_secret,
                        new_two_fa_method=two_fa_method,
                    )
                else:
                    # Crear un nuevo secreto con el método seleccionado
                    create_user_secret(
                        self.request,
                        self.user.login,
                        new_secret,
                        two_fa_method=two_fa_method,
                    )

                if two_fa_method == "app":
                    # Generar QR Code si se selecciona "app"
                    totp = TOTP(new_secret)
                    otp_uri = totp.provisioning_uri(
                        name=self.user.email, issuer_name="ClimMob"
                    )
                    qr = qrcode.make(otp_uri)
                    buffer = BytesIO()
                    qr.save(buffer, format="PNG")
                    buffer.seek(0)
                    otp_qr_code = f"data:image/png;base64,{base64.b64encode(buffer.read()).decode()}"
                    self.request.session.flash(
                        self._("Authenticator App configured successfully!"), "success"
                    )
                elif two_fa_method == "email":
                    # Mensaje de éxito para email
                    self.request.session.flash(
                        self._("Email 2FA configured successfully!"), "success"
                    )

                # Generar códigos de un solo uso
                delete_all_codes(self.request, self.user.login)
                create_one_time_codes(self.request, self.user.login, count=6)
                active_codes = get_active_codes(self.request, self.user.login)
                if active_codes.get("success"):
                    one_time_codes = active_codes["data"]

        return {
            "activeProject": getActiveProject(self.user.login, self.request),
            "userstats": userstats,
            "data": self.decodeDict(self.user.userData),
            "error_summary": error_summary,
            "passChanged": passChanged,
            "profileUpdated": profileUpdated,
            "countries": getCountryList(self.request),
            "sectors": getSectorList(self.request),
            "otp_qr_code": otp_qr_code,
            "one_time_codes": one_time_codes,
        }
