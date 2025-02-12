import base64
from io import BytesIO

import pyotp
import qrcode
from pyotp import TOTP

from climmob.config.auth import getUserData
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


class Force2FAView(privateView):
    def processView(self):
        return {}


class setup2FA_view(privateView):
    def processView(self):
        error_summary = {}
        messages = []
        otp_qr_code = None
        one_time_codes = []
        user = getUserData(self.user.login, self.request)

        data = {}

        secret_response = get_user_secret(self.request, self.user.login)
        if secret_response.get("success") and secret_response["data"]:
            user_secret = secret_response["data"]
            data["two_fa_method"] = user_secret.two_fa_method
        else:
            data["two_fa_method"] = "app"

        if self.request.method == "POST":
            if "generate" in self.request.POST:
                two_fa_method = self.request.POST.get("two_fa_method", "app")
                new_secret = pyotp.random_base32()

                secret_resp = get_user_secret(self.request, self.user.login)
                if secret_resp.get("success") and secret_resp["data"]:
                    update_user_secret(
                        self.request,
                        self.user.login,
                        new_secret,
                        new_two_fa_method=two_fa_method,
                    )
                else:
                    create_user_secret(
                        self.request,
                        self.user.login,
                        new_secret,
                        two_fa_method=two_fa_method,
                    )

                data["two_fa_method"] = two_fa_method

                if two_fa_method == "app":
                    totp = TOTP(new_secret)
                    otp_uri = totp.provisioning_uri(
                        name=user.email, issuer_name="ClimMob"
                    )
                    qr = qrcode.make(otp_uri)
                    buffer = BytesIO()
                    qr.save(buffer, format="PNG")
                    buffer.seek(0)
                    otp_qr_code = f"data:image/png;base64,{base64.b64encode(buffer.read()).decode()}"
                    messages.append("Authenticator App configured successfully!")
                else:
                    messages.append("Email 2FA configured successfully!")

                delete_all_codes(self.request, self.user.login)
                create_one_time_codes(self.request, self.user.login, count=6)
                codes_resp = get_active_codes(self.request, self.user.login)
                if codes_resp["success"]:
                    one_time_codes = codes_resp["data"]

        return {
            "error_summary": error_summary,
            "messages": messages,
            "otp_qr_code": otp_qr_code,
            "one_time_codes": one_time_codes,
            "data": data,
        }
