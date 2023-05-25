from climmob.views.classes import privateView
from climmob.processes import getAllTranslationsOfPhrases


class otherLanguages_view(privateView):
    def processView(self):

        if self.request.method == "POST":

            print("post")

        return {
            "translations": getAllTranslationsOfPhrases(self.request, self.user.login),
            "sectionActive": "otherLanguages",
        }
