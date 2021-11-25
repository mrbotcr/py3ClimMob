from climmob.views.classes import apiView
from pyramid.response import Response
import json
import telebot
import datetime
from climmob.processes import addChat, readChatByUser


class sendFeedbackToBot_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "POST":
            obligatory = [u"message"]
            dataworking = json.loads(self.body)

            if sorted(obligatory) == sorted(dataworking.keys()):
                try:
                    TOKEN = self.request.registry.settings.get("telegram.token")
                    bot = telebot.TeleBot(TOKEN)
                    managers = self.request.registry.settings.get("telegram.managers")
                    date = datetime.datetime.now()
                    for manager in managers.split("|"):
                        send_message = bot.send_message(
                            manager,
                            "User:\n"
                            + self.user.login
                            + "\nFull name:\n"
                            + self.user.fullName
                            + "\nEmail:\n"
                            + self.user.email
                            + "\nOrganization:\n"
                            + self.user.organization
                            + "\nMessage:\n"
                            + str(dataworking["message"]),
                        )
                        message = {}
                        message["user_name"] = self.user.login
                        message["chat_id"] = send_message.message_id
                        message["chat_message"] = dataworking["message"]
                        message["chat_send"] = 1
                        message["chat_read"] = 0
                        message["chat_tofrom"] = 1
                        message["chat_date"] = date
                        add, out = addChat(message, self.request)

                    # if add:
                    response = Response(
                        status=200,
                        body=json.dumps(
                            readChatByUser(self.user.login, self.request),
                            default=myconverter,
                        ),
                    )
                    return response
                except:
                    response = Response(
                        status=401, body=self._("Feedback could not be sent.")
                    )
                    return response

            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts POST method."))
            return response


class readFeedback_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":

            response = Response(
                status=200,
                body=json.dumps(
                    readChatByUser(self.user.login, self.request), default=myconverter
                ),
            )
            return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response
