from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from climmob.views.classes import privateView
from climmob.processes import (
    getAllLocationUnitOfAnalysis,
    addMetadataForm,
    getAllMetadata,
    getMetadataForm,
    modifyMetadataForm,
    deleteMetadataForm,
    addMetadaFormLocationUnitOfAnalysis,
    deleteMetadaFormLocationUnitOfAnalysisByMetadataForm,
)
from pyxform.xls2json import parse_file_to_json
from pyramid.response import FileResponse
import shutil as sh
import uuid
import json
import os


class MetadataForms_view(privateView):
    def processView(self):

        dataworking = {}
        error_summary = {}

        if self.user.admin not in [1]:
            raise HTTPNotFound()

        if self.request.method == "POST":
            dataworking = self.getPostDict()

            if (
                "metadata_active" in dataworking.keys()
                and dataworking["metadata_active"] == "on"
            ):
                dataworking["metadata_active"] = 1
            else:
                dataworking["metadata_active"] = 0

            if hasattr(self.request.POST["xlsxODK"], "file"):
                (
                    xlsxData,
                    jsonData,
                    error_summary,
                ) = self.ProcedureToObtainInformationFromTheUploadedFile()

                if not error_summary:
                    dataworking["metadata_odk"] = xlsxData
                    dataworking["metadata_json"] = jsonData

            if "btn_add_metadata" in self.request.POST:

                dataworking["metadata_id"] = str(uuid.uuid4())

                if not error_summary:
                    added, message = addMetadataForm(dataworking, self.request)

                    if not added:

                        error_summary = {"error": message}

            elif "btn_modify_metadata" in self.request.POST:

                if not error_summary:

                    deleteMetadaFormLocationUnitOfAnalysisByMetadataForm(
                        self.request, dataworking["metadata_id"]
                    )

                    edited, message = modifyMetadataForm(
                        self.request, dataworking["metadata_id"], dataworking
                    )

                    if not edited:

                        error_summary = {"error": message}

            if not error_summary:

                for location_unit_of_analysis in dataworking["select_project_types"]:
                    metadataForm_luoa = {
                        "metadata_id": dataworking["metadata_id"],
                        "pluoa_id": int(location_unit_of_analysis),
                    }
                    added2, message2 = addMetadaFormLocationUnitOfAnalysis(
                        metadataForm_luoa, self.request
                    )

                self.request.session.flash(
                    self._("The metadata form was modified successfully.")
                )

                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("librarymetadata"))

        listOfMetadata = getAllMetadata(self.request)

        return {
            "sectionActive": "librarymetadata",
            "dataworking": dataworking,
            "listOfMetadata": listOfMetadata,
            "error_summary": error_summary,
            "listOfLocationsAndUnitOfAnalysis": getAllLocationUnitOfAnalysis(
                self.request
            ),
        }

    def ProcedureToObtainInformationFromTheUploadedFile(self):

        pathOfTheMetadata = os.path.join(
            self.request.registry.settings["user.repository"], "_metadata"
        )
        if not os.path.exists(pathOfTheMetadata):
            os.makedirs(pathOfTheMetadata)

        xlsxData = self.request.POST["xlsxODK"].file
        file_name = self.request.POST["xlsxODK"].filename

        filePath = pathOfTheMetadata + "/" + file_name

        xlsxData.seek(0)
        with open(filePath, "wb") as permanent_file:
            sh.copyfileobj(xlsxData, permanent_file)

        xlsxData.seek(0)

        warnings = []
        error = {}
        jsonData = {}
        try:
            jsonData = parse_file_to_json(filePath, warnings=warnings)
            jsonData = json.dumps(jsonData, indent=4, ensure_ascii=False)
        except Exception as e:
            error = {"error": self._("Error with ODK file: {}").format(str(e))}

        os.remove(filePath)
        return xlsxData.read(), jsonData, error


class MetadataFormDetails_view(privateView):
    def processView(self):

        if self.request.method == "GET":
            metadataId = self.request.matchdict["metadataform"]
            metadataForm = getMetadataForm(self.request, metadataId)
            del metadataForm["metadata_odk"]
            del metadataForm["metadata_json"]
            self.returnRawViewResult = True
            return metadataForm

        raise HTTPNotFound


class DownloadMetadataForm_view(privateView):
    def processView(self):
        self.returnRawViewResult = True

        metadataId = self.request.matchdict["metadataform"]

        if self.user.admin not in [1]:
            return False

        metadataForm = getMetadataForm(self.request, metadataId)

        contentType = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = metadataForm["metadata_name"] + ".xlsx"

        path = os.path.join(
            self.request.registry.settings["user.repository"], "_metadata"
        )

        if os.path.exists(path):
            sh.rmtree(path)

        os.mkdir(path)

        xlsxData = metadataForm["metadata_odk"]

        with open(os.path.join(path, filename), "wb") as file:
            file.write(xlsxData)

        response = FileResponse(
            os.path.join(path, filename),
            request=self.request,
            content_type=contentType,
        )
        response.content_disposition = 'attachment; filename="' + filename + '"'
        self.returnRawViewResult = True
        return response


class DeleteMetadataForms_view(privateView):
    def processView(self):

        metadataId = self.request.matchdict["metadataform"]

        metadataForm = getMetadataForm(self.request, metadataId)

        if self.request.method == "POST":

            if not metadataForm:
                return {
                    "status": 400,
                    "error": self._("This metadata form does not exist"),
                }
            else:
                error, msg = deleteMetadataForm(self.request, metadataId)

                if not error:
                    self.returnRawViewResult = True
                    return {"status": 400, "error": msg}
                else:
                    self.returnRawViewResult = True
                    return {"status": 200}
        else:
            return {
                "status": 400,
                "error": self._("This process only accepts POST method"),
            }
