import datetime
import json

from pyramid.response import FileResponse
from pyramid.response import Response

from climmob.plugins.utilities import getProductDirectory
from climmob.processes import (
    projectExists,
    getProductData,
    getTheProjectIdForOwner,
    get_registry_questions_by_project,
    get_assessment_questions_by_project,
)
from climmob.products import product_found
from climmob.views.classes import apiView
from climmob.views.productsList import getDataProduct
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.validators import TextField


class readProducts_view(apiView):
    def processView(self):
        def myconverter(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        if self.request.method == "GET":
            obligatory = ["project_cod", "user_owner"]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        products = getDataProduct(activeProjectId, self.request)

                        response = Response(
                            status=200, body=json.dumps(products, default=myconverter)
                        )
                        return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is not project with that code."),
                        )
                        return response
                else:
                    response = Response(
                        status=401, body=self._("Not all parameters have data.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class downloadApi_view(apiView):
    def processView(self):

        if self.request.method == "GET":
            obligatory = [
                "project_cod",
                "user_owner",
                "celery_taskid",
                "product_id",
            ]
            try:
                dataworking = json.loads(self.body)
            except:
                response = Response(
                    status=401,
                    body=self._(
                        "Error in the JSON, It does not have the 'body' parameter."
                    ),
                )
                return response

            if sorted(obligatory) == sorted(dataworking.keys()):
                dataworking["user_name"] = self.user.login

                dataInParams = True
                for key in dataworking.keys():
                    if dataworking[key] == "":
                        dataInParams = False

                if dataInParams:
                    exitsproject = projectExists(
                        self.user.login,
                        dataworking["user_owner"],
                        dataworking["project_cod"],
                        self.request,
                    )
                    if exitsproject:

                        activeProjectId = getTheProjectIdForOwner(
                            dataworking["user_owner"],
                            dataworking["project_cod"],
                            self.request,
                        )

                        # Here start the code for the download
                        productData = getProductData(
                            activeProjectId,
                            dataworking["celery_taskid"],
                            dataworking["product_id"],
                            self.request,
                        )

                        if productData:
                            product_id = productData["product_id"]

                            if product_found(product_id):
                                contentType = productData["output_mimetype"]
                                filename = productData["output_id"]
                                path = getProductDirectory(
                                    self.request,
                                    dataworking["user_owner"],
                                    dataworking["project_cod"],
                                    product_id,
                                )
                                response = FileResponse(
                                    path + "/outputs/" + filename,
                                    request=self.request,
                                    content_type=contentType,
                                )
                                response.content_disposition = (
                                    'attachment; filename="' + filename + '"'
                                )

                                return response
                            else:
                                response = Response(
                                    status=401,
                                    body=self._(
                                        "There is no product with that product_id."
                                    ),
                                )
                                return response
                        else:
                            response = Response(
                                status=401,
                                body=self._(
                                    "There is no product with that celery_taskid or product_id."
                                ),
                            )
                            return response
                    else:
                        response = Response(
                            status=401,
                            body=self._("There is no project with that code."),
                        )
                        return response
                else:
                    response = Response(
                        status=401, body=self._("Not all parameters have data.")
                    )
                    return response
            else:
                response = Response(status=401, body=self._("Error in the JSON."))
                return response
        else:
            response = Response(status=401, body=self._("Only accepts GET method."))
            return response


class GetListOfQuestionsByProject(apiView):
    validators = (ProjectExistsValidator,)
    valid_fields = (
        TextField("user_owner"),
        TextField("project_cod"),
        TextField(
            "lang_code", False, False
        ),  ##if not set it uses "en" ass default // if language does not exist uses en
    )

    def get(self):
        dataworking = json.loads(self.body)
        if not dataworking.get("lang_code") or dataworking["lang_code"] == "":
            dataworking["lang_code"] = "en"

        activeProjectId = getTheProjectIdForOwner(
            dataworking["user_owner"],
            dataworking["project_cod"],
            self.request,
        )

        registry_questions = get_registry_questions_by_project(
            self.request, activeProjectId, dataworking["lang_code"]
        )
        assessment_questions = get_assessment_questions_by_project(
            self.request, activeProjectId, dataworking["lang_code"]
        )
        json_questions = registry_questions + assessment_questions

        return Response(
            status=200,
            body=json.dumps(json_questions),
            content_type="application/json; charset=UTF-8",
        )
