from climmob.views.classes import privateView
from jinja2 import Environment, FileSystemLoader
from climmob.processes import (
    getListOfLanguagesByUser,
    getAllTranslationsOfPhrasesByLanguage,
    savePhraseTranslation,
)
import os


class otherLanguages_view(privateView):
    def processView(self):

        return {
            "listOflanguages": getListOfLanguagesByUser(self.request, self.user.login),
            "sectionActive": "otherLanguages",
        }


class saveOtherLanguages_view(privateView):
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


class getOtherLanguages_view(privateView):
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
