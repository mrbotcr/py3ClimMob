from climmob.views.classes import privateView
from jinja2 import Environment, FileSystemLoader
from climmob.processes import (
    getListOfLanguagesByUser,
    getAllTranslationsOfPhrasesByLanguage,
    savePhraseTranslation,
    getListOfLanguagesInClimMob,
    languageByLanguageCode,
    getAllUserAdmin,
)
from climmob.views.basic_views import RecoverPasswordView
import os


class OtherLanguagesView(privateView):
    def processView(self):

        try:
            help = self.request.params["help"]
        except:
            help = None

        return {
            "listOflanguages": getListOfLanguagesByUser(self.request, self.user.login),
            "listOfLanguagesInClimMob": getListOfLanguagesInClimMob(self.request),
            "sectionActive": "otherLanguages",
            "help": help,
        }


class SaveOtherLanguagesView(privateView):
    def processView(self):
        self.returnRawViewResult = True

        if self.request.method == "POST":

            dataworking = self.getPostDict()

            for phrase in dataworking.keys():

                info = phrase.split("_")

                if info[0] == "phrase":
                    good, message = savePhraseTranslation(
                        self.request,
                        info[2],
                        dataworking[phrase],
                        self.user.login,
                        info[1],
                    )

            return {"status": 200}

        return {"status": 400, "error": "Only POST methods are accepted"}


class GetOtherLanguagesView(privateView):
    def processView(self):

        if self.request.method == "GET":
            self.returnRawViewResult = True

            language = self.request.matchdict["language"]

            translations = getAllTranslationsOfPhrasesByLanguage(
                self.request, self.user.login, language
            )

            PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            env = Environment(
                autoescape=False,
                loader=FileSystemLoader(
                    os.path.join(PATH, "templates", "otherLanguages")
                ),
                trim_blocks=False,
            )
            template = env.get_template("tableOfPhrases.jinja2")

            info = {"translations": translations, "_": self._}

            render_temp = template.render(info)

            return render_temp

        return ""


class requestLanguageTranslation_view(privateView):
    def processView(self):

        if self.request.method == "POST":
            self.returnRawViewResult = True

            dataworking = self.getPostDict()

            language = languageByLanguageCode(dataworking["language"], self.request)

            PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            env = Environment(
                autoescape=False,
                loader=FileSystemLoader(os.path.join(PATH, "templates", "email")),
                trim_blocks=False,
            )
            template = env.get_template("language_request.jinja2")

            info = {
                "user_fullname": self.user.fullName,
                "user_name": self.user.login,
                "email": self.user.userData["user_email"],
                "language": language,
                "contribute": dataworking["contribute"],
                "instance": self.request.registry.settings.get(
                    "analytics.instancename", ""
                ),
            }

            render_temp = template.render(info)

            email_from = self.request.registry.settings.get("email.from", None)
            if email_from is None:
                return {
                    "status": 400,
                    "error": self._(
                        "It has not been possible to request a new local language, due to email problems."
                    ),
                }

            for user in getAllUserAdmin(self.request):

                RecoverPasswordView.send_password_by_email(
                    self,
                    render_temp,
                    "Request for local language in ClimMob",
                    user["user_fullname"],
                    user["user_email"],
                    email_from,
                )

            return {"status": 200}

        return {"status": 400, "error": self._("Only POST methods are accepted")}
